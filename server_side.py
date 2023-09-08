from flask import Flask, request, send_file, make_response
import os
import uuid
import shutil
from zipfile import ZipFile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_images'
app.config['PROCESSED_FOLDER'] = 'processed_images'

def process_image(img_path):
    # Your image processing code goes here
    # Replace the following line with your actual image processing logic
    processed_img_path = img_path
    return processed_img_path

def process_images_in_folder(folder_path):
    processed_images = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            processed_path = process_image(file_path)
            processed_images.append(processed_path)
    return processed_images

@app.route('/process_images', methods=['POST'])



def process_images_endpoint():
    if not request.files:
        return "No image parts in the request", 400

    uploaded_files = request.files.getlist('images')
    if not uploaded_files:
        return "No image parts in the request", 400

    folder_name = str(uuid.uuid4())
    upload_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(upload_folder_path)

    for image in uploaded_files:
        filename = str(uuid.uuid4()) + '_' + image.filename
        img_path = os.path.join(upload_folder_path, filename)
        image.save(img_path)

    processed_images = process_images_in_folder(upload_folder_path)

    processed_folder_path = os.path.join(app.config['PROCESSED_FOLDER'], folder_name)
    os.makedirs(processed_folder_path)

    for i, processed_image in enumerate(processed_images):
        processed_filename = f"processed_{i}.png"
        processed_dest_path = os.path.join(processed_folder_path, processed_filename)
        shutil.copy(processed_image, processed_dest_path)

    shutil.rmtree(upload_folder_path)

    zip_filename = f"{folder_name}_processed_images.zip"
    zip_path = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)

    with ZipFile(zip_path, 'w') as zip_file:
        for root, _, files in os.walk(processed_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.basename(file_path))

    shutil.rmtree(processed_folder_path)

    response = make_response(send_file(zip_path, as_attachment=True))
    response.headers['processed_file_paths'] = ','.join(processed_images)
    return response

if __name__ == '__main__':
    app.run()
