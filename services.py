import os
import fastapi
import bacardi
import shutil
import io
import uuid
import base64
from zipfile import ZipFile

IMAGE_DIR = os.path.join(".", "tmp", "images")
OUTPUT_DIR = os.path.join(".", "tmp", "out")


def setup_dirs():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def destroy_dirs():
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)


def is_valid(filename: str) -> bool:
    valid_extensions = (".zip", ".rar", ".yaml", ".png", ".jpg", ".jpeg")
    return filename.endswith(valid_extensions)


def upload_image(image: bytes):
    guid = uuid.uuid4()
    with open(f"{IMAGE_DIR}/{guid}.png", "wb+") as f:
        f.write(base64.decodebytes(image))
    return str(guid) + '.png'


def upload(obj: fastapi.UploadFile):
    if is_valid(obj.filename):
        with open(f"{IMAGE_DIR}/{obj.filename}", "wb+") as f:
            f.write(obj.file.read())
        return str(IMAGE_DIR) +"/" + str(obj.filename)
    return None


def extract_images(file_name: str) -> None:
    with ZipFile(file_name, 'r') as zip:
        zip.printdir()
        zip.extractall(path=IMAGE_DIR)


def process(cards: str):
    b = bacardi.Bacardi(cards, cards['cards'], IMAGE_DIR=IMAGE_DIR, OUTPUT_DIR=OUTPUT_DIR)
    b.run()


def process_preview(layout: str):
    b = bacardi.Bacardi(layout, None, IMAGE_DIR=IMAGE_DIR, OUTPUT_DIR=OUTPUT_DIR)
    b.run()


def get_all_file_paths():

    file_paths = []

    for root, dirs, files in os.walk(OUTPUT_DIR):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths  


def zip_deck():
         
    file_paths = get_all_file_paths()

    for file_name in file_paths:
        print(file_name)
    zip_io = io.BytesIO()
    with ZipFile(zip_io, 'w') as zip:
        for file in file_paths:
            zip.write(file)

    print('All files zipped successfully!')
    return zip_io    
  