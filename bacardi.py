from PIL import Image, ImageDraw, ImageFont
import sys
import string
from math import ceil
import yaml

PRESET_FILE = "obj/presets.yaml"
CONFIG_FILE = "../testconfig.yaml"
CARDS_FILE = "../testcards.yaml"

class Bacardi():

    def __init__(self, CONFIG_FILE, CARDS_FILE, PRESET_FILE="obj/presets.yaml", IMAGE_DIR = '../'):
        self.dpi = 300
        self.img_dir = IMAGE_DIR
        self.load_presets(PRESET_FILE)
        self.load_config(CONFIG_FILE)
        self.load_cards(CARDS_FILE)
    
    def load_presets(self, PRESET_FILE):
        pf = open(PRESET_FILE, 'r')
        self.presets = yaml.safe_load(pf)
        
    def load_config(self, CONFIG_FILE):
        pf = open(CONFIG_FILE, 'r')
        confs = yaml.safe_load(pf)

        self.layout = confs['layout']

        try:
            self.grid_width = confs['grid']['width']
            self.grid_heigth = confs['grid']['heigth']
        except:
            print("please define the card grid.")
        
        if(type(confs['size']) == str):
            if(confs['size'] in self.presets):
                width = self.presets[confs['size']]['width']
                heigth = self.presets[confs['size']]['heigth']
                unit = self.presets[confs['size']]['unit']
                self.calculate_pixel_size(width, heigth, unit)
            else:
                print("unknown preset.")
        elif(type(confs['size']) == dict):
            width = confs['size']['width']
            heigth = confs['size']['heigth']
            unit = confs['size']['unit']
            self.calculate_pixel_size(width, heigth, unit)
        else:
            print("parameter 'size' should be the name of a preset or a dict with parameters width, heigth and unit")


    def load_cards(self, CARDS_FILE):
        pf = open(CARDS_FILE, 'r')
        self.cards = yaml.safe_load(pf)

    def calculate_pixel_size(self, width, heigth, unit):
        # produces an image with 300 dpi given dimensions and units
        # units can be mm, px or in
        if(unit == 'px'):
            self.width = width
            self.heigth = heigth
        elif(unit == 'in'):
            self.width = ceil(self.dpi * width)
            self.heigth = ceil(self.dpi * heigth)
            if(unit == 'mm'):
                self.width = ceil(width/25.4)
                self.heigth = ceil(heigth/25.4)
        else:
            print("unknown unit: ", unit)


    def get_next_piece_of_layout(self):
        #yield next thing to render or end and reset
        order = sorted(self.layout, key=lambda x: x['level'])
        for i in order:
            yield i

    def square_to_pixels(self, square, end=False):
        #calculate where in pixels the grid square starts or ends
        width_square = ceil(self.width/self.grid_width)
        heigth_square = ceil(self.heigth/self.grid_heigth)
        
        column = ''.join(list(filter(lambda x: x in string.ascii_letters, square)))
        row = ''.join(list(filter(lambda x: x not in string.ascii_letters, square)))
        row = int(row)
        column = column.upper()
        
        # if len(column > 1):
        ## TODO mais de 26 colunas
        
        loc_col = (ord(column) - 65) * width_square
        loc_row = (row-1) * heigth_square 
        if(end == True):
            loc_col += width_square
            loc_row += heigth_square
        # if(loc_col < 0 or loc_row < 0):
        #     raise exception("Use only upper case letters and numbers as index")
        ## TODO
        return ceil(loc_col), ceil(loc_row)

    def get_size_from_squares(self, start, end):
        return tuple(map(lambda i, j: i - j, self.square_to_pixels(end, True), self.square_to_pixels(start)))

    def render(self, obj):
        card = Image.new('RGBA', (self.width, self.heigth), (255,255,255,255))
        part = self.get_next_piece_of_layout()
        #verify if it exists else use default value
        for part_conf in part:
            if(part_conf["name"] in obj):
                value = obj[part_conf["name"]]
            elif 'default' in part_conf:
                value = part_conf["default"]
            else:
                print("there must be a value or default for ", part_conf["name"])
            
            print("rendering: ", value)
            
            # Value can be null
            if(value != None):
                if(part_conf["type"] == "image"):
                    img_el = Image.open(self.img_dir + value)
                    img_el = img_el.resize(self.get_size_from_squares(part_conf["start"], part_conf["end"]))
                    
                    # transparency mask can be in either file
                    if("mask" in part_conf):
                        msk = part_conf["mask"]
                    elif("mask" in obj):
                        msk = obj["mask"]
                    else:
                        msk = img_el.convert('RGBA')
                    
                    card.paste(img_el, self.square_to_pixels(part_conf["start"]), msk)
                
                elif(part_conf["type"] == "text"):
                    text = ImageDraw.Draw(card)
                    if("scale" in obj):
                        scale = obj["scale"]
                    elif("scale" in part_conf):
                        scale = part_conf["scale"]
                    else:
                        scale = 1
                    fnt = ImageFont.truetype("obj/Font/arial.ttf", size=ceil(self.width/self.grid_width * scale))
                    text.multiline_text((self.square_to_pixels(part_conf["start"])), value, font=fnt, fill=(0, 0, 0))

        return card
    
    def save_card(self, card, title, formt):
        card.save(title + formt)

    def run(self):

        count = 0
        for obj in self.cards:
            count += 1
            card = self.render(obj)
            self.save_card(card, "card_" + str(count), ".png")


b = Bacardi(CONFIG_FILE, CARDS_FILE)
b.run()

"""

        if(isinstance(obj["start"], str)):
            itert = [card for card in string.ascii_uppercase]
        else:
            try:
                itert = [str(card).zfill(obj["fill"]) for card in range(obj["start"], obj["end"] +1)]
            except:
                itert = [str(card) for card in range(obj["start"], obj["end"] +1 )]

        for card in itert:

            background = Image.new('RGBA', (obj["width"], obj["heigth"]), (255,255,255,255))
            idraw = ImageDraw.Draw(background)
            
            code = expansion + obj["prefix"] + card

            #Creating an instance of qrcode
            qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=5)
            qr.add_data(code)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            background.paste(img, (obj["width"] - 310, obj["heigth"] - 310))

            try:
                text = obj["text"][int(card)-1]
            except:
                text = card

            font = ImageFont.truetype("Font/BebasNeue-Regular.ttf", size=158)
            idraw.text((30, 10), text, (0,0,0), font=font)

            title = code + '.png'
            background.save(title)
"""
