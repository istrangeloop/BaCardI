# created with help of https://www.youtube.com/watch?v=0cVybZ_loWw
import fastapi
from fastapi import Form, responses, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import services
from typing import Optional
app = fastapi.FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hi :) you are using the BaCardI API version 1.0 created by Ingrid Spangler"}

@app.post("/layout")
def create_layout(background_tasks: BackgroundTasks, layout: str = Form(...) , images: Optional[fastapi.UploadFile] = None):
    print('a')
    services.setup_dirs()
    if images != None:
        services.upload(images)
    services.process_preview(layout)
    card = responses.FileResponse(f"{services.OUTPUT_DIR}/card_preview.png")
    background_tasks.add_task(services.destroy_dirs)
    return card

@app.post("/create")
def create_cards(background_tasks: BackgroundTasks,
                image: fastapi.UploadFile = fastapi.File(...), 
                layout: fastapi.UploadFile = fastapi.File(...), 
                cardinfo: fastapi.UploadFile = fastapi.File(...)):
    # TODO: create unique name for each temporary folder then
    # delete them after processing the request
    services.setup_dirs()
    path = services.upload(image)
    l_path = services.upload(layout)
    c_path = services.upload(cardinfo)
    if path is None:
        return fastapi.HTTPException(status_code=409, detail="incorrect file type")

    services.extract_images(path)
    services.process(l_path, c_path)
    deck = services.zip_deck()
    background_tasks.add_task(services.destroy_dirs)
    return responses.Response(deck.getvalue(), media_type="application/x-zip-compressed", headers={
        'Content-Disposition': f'attachment;filename=generated_deck.zip'
    })