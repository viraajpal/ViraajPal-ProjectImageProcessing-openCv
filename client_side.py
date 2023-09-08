from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImageReader
from PyQt5.QtCore import Qt
import sys
import requests
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API GUI")
        self.resize(800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        vertical_layout = QVBoxLayout()

        horizontal_layout = QHBoxLayout()

        self.upload_button = QPushButton("Upload Folder", self)
        self.download_button = QPushButton("Download Processed Image", self)
        self.exit_button = QPushButton("Exit", self)

        horizontal_layout.addWidget(self.upload_button)
        horizontal_layout.addWidget(self.download_button)
        horizontal_layout.addWidget(self.exit_button)

        vertical_layout.addLayout(horizontal_layout)

        central_widget.setLayout(vertical_layout)

        self.upload_button.clicked.connect(self.open_folder_dialog)
        self.download_button.clicked.connect(self.download_processed_image)
        self.exit_button.clicked.connect(self.close)

        self.processed_image_paths = []

    def open_folder_dialog(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        if folder_dialog.exec_():
            folder_path = folder_dialog.selectedFiles()[0]
            self.upload_images_to_api(folder_path)

    def upload_images_to_api(self, folder_path):
        url = 'http://localhost:5000/process_images'
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                files.append(('images', open(file_path, 'rb')))

        response = requests.post(url, files=files)

        if response.status_code == 200:
            print("Images uploaded successfully!")
            self.processed_image_paths = response.headers.get('processed_file_paths').split(',')
            if len(self.processed_image_paths) > 0:
                self.show_processed_image(self.processed_image_paths[0])
        else:
            print(f"Error uploading images: {response.text}")



    def download_processed_image(self):
        if len(self.processed_image_paths) > 0:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Processed Image", "", "Images (*.png *.xpm *.jpg *.jpeg)")

            if save_path:
                with open(save_path, 'wb') as f:
                    response = requests.get(self.processed_image_paths[0])
                    f.write(response.content)
                    print("Download complete!")
        else:
            print("No processed images available for download.")

    def show_processed_image(self, file_path):
        image_label = QLabel(self)
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setGeometry(300, 50, 400, 400)

# Run 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
