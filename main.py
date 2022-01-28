# created with help of https://www.youtube.com/watch?v=0cVybZ_loWw
import fastapi
from fastapi import Form, responses, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import services

from pydantic import BaseModel
from typing import Optional, List
app = fastapi.FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Layout(BaseModel):
    type: str
    name: str
    start: str
    end: str
    level: int
    scale: Optional[float]
    default: Optional[bytes]


class Grid(BaseModel):
    width: int
    height: int


class Size(Grid):
    unit: str


class LayoutRequest(BaseModel):
    size: Optional[Size] = None
    grid: Optional[Grid] = None
    layout: List[Layout] = []


@app.get("/")
def root():
    return {"message": "Hi :) you are using the BaCardI API version 1.0 created by Ingrid Spangler"}


@app.post("/junk")
async def test(layout: LayoutRequest):
    services.setup_dirs()
    # lista de enderecos das imagens registradas
    # equivalente a services.upload(images)
    # porem para N imagens
    image_list = (services.upload_image(images.default) for images in layout.layout)
    return image_list


@app.post("/layout")
def create_layout(background_tasks: BackgroundTasks, layout: LayoutRequest , images: Optional[fastapi.UploadFile] = None):
    services.setup_dirs()
    if images != None:
        services.upload(images)
    json_layout = jsonable_encoder(layout)
    services.process_preview(json_layout)
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