import sys

from PIL.Image import Resampling
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from PIL import Image


class ImageInfoWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Info")

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Create a button to browse for an image
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_image)

        # Create a label to display the image description
        self.description_label = QLabel(self)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)

    def browse_image(self):
        # Open a file dialog to browse for an image
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", filter="Image Files (*.png *.jpg *.jpeg)")

        if image_path:
            # Open the image using Pillow
            img = Image.open(image_path)

            # Check if the 'Description' key exists in the image info
            if 'Description' in img.info:
                # Get the image description from the comments field
                img_desc = img.info['Description']

                # Set the image description label text
                self.description_label.setText(img_desc)
            else:
                # Set the image description label text
                self.description_label.setText("No description found for this image.")

            # Resize the image to fit the label
            img = img.resize((self.image_label.width(), self.image_label.height()), resample=Image.LANCZOS)

            # Convert the image to a QPixmap
            pixmap = QPixmap.fromImage(img.toqimage())

            # Set the image label pixmap
            self.image_label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ImageInfoWindow()
    window.resize(500, 500)
    window.show()

    sys.exit(app.exec_())
