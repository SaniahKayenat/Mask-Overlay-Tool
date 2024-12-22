import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QLabel, QSlider, QPushButton, QHBoxLayout, QLineEdit, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Viewer with Masks")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.top_layout = QHBoxLayout()
        self.openImageButton = QPushButton("Load Images")
        self.openImageButton.clicked.connect(self.load_images)
        self.top_layout.addWidget(self.openImageButton)

        self.openMaskButton = QPushButton("Load Masks")
        self.openMaskButton.clicked.connect(self.load_masks)
        self.top_layout.addWidget(self.openMaskButton)

        self.file_name_label = QLabel("No files loaded")
        self.file_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.top_layout.addWidget(self.file_name_label)

        self.layout.addLayout(self.top_layout)

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.image_label)

        self.opacity_layout = QHBoxLayout()
        self.opacity_label = QLabel("Mask Opacity:")
        self.opacity_input = QLineEdit("0.5")
        self.opacity_button = QPushButton("Apply Opacity")
        self.opacity_button.clicked.connect(self.update_opacity)

        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_input)
        self.opacity_layout.addWidget(self.opacity_button)
        self.layout.addLayout(self.opacity_layout)

        self.navigation_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_image)
        self.navigation_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_image)
        self.navigation_layout.addWidget(self.next_button)
        self.layout.addLayout(self.navigation_layout)

        self.images = []
        self.masks = []
        self.current_index = 0
        self.opacity = 0.5

    def load_images(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder", options=options)
        if folder_path:
            self.images = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])
            self.current_index = 0
            self.update_display()

    def load_masks(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Mask Folder", options=options)
        if folder_path:
            # Load all mask files with valid extensions
            self.masks = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])
            
            if not self.masks:
                self.file_name_label.setText("No valid masks found in the selected folder.")
                return
            
            # Ensure the number of masks matches the images
            if len(self.masks) != len(self.images):
                self.file_name_label.setText(f"Warning: {len(self.masks)} masks do not match {len(self.images)} images.")
            
            self.update_display()


    def update_opacity(self):
        try:
            self.opacity = float(self.opacity_input.text())
            if self.opacity < 0 or self.opacity > 1:
                raise ValueError
            self.update_display()
        except ValueError:
            self.opacity_input.setText("0.5")

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.update_display()

    def update_display(self):
        if not self.images:
            self.image_label.setText("No images loaded")
            return

        image_path = self.images[self.current_index]
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if self.masks and self.current_index < len(self.masks):
            mask_path = self.masks[self.current_index]
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

            # Resize the mask to match the image dimensions
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)

            mask_colored = np.zeros_like(image)
            mask_colored[:, :, 0] = mask  # Apply mask to red channel

            # Create an overlay
            overlay = cv2.addWeighted(image, 1 - self.opacity, mask_colored, self.opacity, 0)
            image = overlay

        # Resize the image for display (e.g., 224x224) without altering the original file
        display_image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)

        height, width, channel = display_image.shape
        qimage = QImage(display_image.data, width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)
        self.file_name_label.setText(f"Image: {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.images)})")


def main():
    app = QApplication([])
    viewer = ImageViewer()
    viewer.show()
    app.exec_()

if __name__ == '__main__':
    main()
