# created with help of https://www.youtube.com/watch?v=0cVybZ_loWw
import fastapi
from fastapi import responses
import services

app = fastapi.FastAPI()

@app.get("/")
def root():
    return {"message": "Hi :) you are using the BaCardI API version 1.0 created by Ingrid Spangler"}

@app.post("/layout")
def create_layout(l_file: fastapi.UploadFile = fastapi.File(...)):
    content = l_file.file.read()
    pass
        

@app.post("/create")
def create_cards(image: fastapi.UploadFile = fastapi.File(...), 
                layout: fastapi.UploadFile = fastapi.File(...), 
                cardinfo: fastapi.UploadFile = fastapi.File(...)):
    # TODO: create unique name for each temporary folder then
    # delete them after processing the request
    services.setup_dirs()
    path = services.upload_zip(image)
    l_path = services.upload_zip(layout)
    c_path = services.upload_zip(cardinfo)
    if path is None:
        return fastapi.HTTPException(status_code=409, detail="incorrect file type")

    services.extract_images(path)
    services.process(l_path, c_path)
    deck = services.zip_deck('generated_deck.zip')
    
    services.destroy_dirs()

    return responses.FileResponse(deck)