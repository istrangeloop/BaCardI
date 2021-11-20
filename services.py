import os
import fastapi
import bacardi
import shutil
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
    #if os.path.exists(OUTPUT_DIR):
    #    shutil.rmtree(OUTPUT_DIR)

def is_zip(filename: str) -> bool:
    valid_extensions = (".zip", ".rar", ".yaml")
    return filename.endswith(valid_extensions)

def upload_zip(compressed: fastapi.UploadFile):
    if is_zip(compressed.filename):
        with open(f"{IMAGE_DIR}/{compressed.filename}", "wb+") as zip_upload:
            zip_upload.write(compressed.file.read())
        return str(IMAGE_DIR) +"/" + str(compressed.filename)
    return None

def extract_images(file_name: str) -> None:
    with ZipFile(file_name, 'r') as zip:
        zip.printdir()
        zip.extractall(path=IMAGE_DIR)

def process(layout: str, cards: str):
    b = bacardi.Bacardi(layout, cards, IMAGE_DIR=IMAGE_DIR, OUTPUT_DIR=OUTPUT_DIR)
    b.run()

def get_all_file_paths():

    file_paths = []

    for root, dirs, files in os.walk(OUTPUT_DIR):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths  

def zip_deck(deck_name):
         
    file_paths = get_all_file_paths()

    for file_name in file_paths:
        print(file_name)

    with ZipFile(f"{OUTPUT_DIR}/{deck_name}", 'w') as zip:
        for file in file_paths:
            zip.write(file)

    print('All files zipped successfully!')
    return f"{OUTPUT_DIR}/{deck_name}"     
  