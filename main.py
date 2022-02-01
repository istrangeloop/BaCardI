# created with help of https://www.youtube.com/watch?v=0cVybZ_loWw
import fastapi
from fastapi import Form, responses, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import services
import base64
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
    size: Optional[Size] or str = None
    grid: Optional[Grid] = None
    preset: Optional[str] = None
    layout: List[Layout] = []

class CardsRequest(LayoutRequest):
    cards: list = []

@app.get("/")
def root():
    return {"message": "Hi :) you are using the BaCardI API version 1.0 created by Ingrid Spangler"}

# @app.post("/junk")
# async def test(layout: LayoutRequest):
#     services.setup_dirs()
#     # lista de enderecos das imagens registradas
#     # equivalente a services.upload(images)
#     # porem para N imagens
#     image_list = (services.upload_image(images.default) for images in layout.layout)
#     return image_list


@app.post("/layout")
def create_layout(background_tasks: BackgroundTasks, layout: LayoutRequest):
    services.setup_dirs()
    for el in layout.layout:
        if el.default != None:
            filename = services.upload_image(el.default)
            el.default = filename
    json_layout = jsonable_encoder(layout)
    services.process_preview(json_layout)
    card = open(f"{services.OUTPUT_DIR}/card_preview.png", "rb").read()
    encoded = base64.b64encode(card)
    background_tasks.add_task(services.destroy_dirs)
    return encoded

@app.post("/create")
def create_cards(background_tasks: BackgroundTasks, 
                cards: CardsRequest):
    services.setup_dirs()
    for el in cards.layout:
        if el.default != None:
            filename = services.upload_image(el.default)
            el.default = filename

    for el in cards.layout:
        if(el.type == 'image'):
            for card in cards.cards:
                filename = services.upload_image(bytes(card[el.name], 'UTF-8'))
                if filename is None:
                    return fastapi.HTTPException(status_code=409, detail="incorrect file type")

                card[el.name] = filename
    json_cards = jsonable_encoder(cards)
    services.process(json_cards)
    deck = services.zip_deck()
    background_tasks.add_task(services.destroy_dirs)
    return responses.Response(deck.getvalue(), media_type="application/x-zip-compressed", headers={
        'Content-Disposition': f'attachment;filename=generated_deck.zip'
    })