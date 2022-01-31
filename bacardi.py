import os
import string
import yaml
import json
from PIL import Image, ImageDraw, ImageFont
from math import ceil


PRESET_FILE = os.path.join("util", "presets.yaml")
ASSEMBLE = 0
PREVIEW = 1

class Bacardi():

    def __init__(self, CONFIG_FILE, CARDS_FILE, IMAGE_DIR='images', OUTPUT_DIR='out', PRESET_FILE=PRESET_FILE):
        self.dpi = 300
        self.img_dir = IMAGE_DIR
        self.out_dir = OUTPUT_DIR
        self.mode = ASSEMBLE
        self.load_presets(PRESET_FILE)
        self.load_config(CONFIG_FILE)
        self.load_cards(CARDS_FILE)
    
    def load_presets(self, PRESET_FILE):
        pf = open(PRESET_FILE, 'r')
        self.presets = yaml.safe_load(pf)
        
    def load_config(self, CONFIG_FILE):
#        pf = open(CONFIG_FILE, 'r')
#        confs = yaml.safe_load(pf)
        confs = CONFIG_FILE
        self.layout = confs['layout']

        try:
            self.grid_width = confs['grid']['width']
            self.grid_height = confs['grid']['height']
        except:
            print("please define the card grid.")
        
        if('preset' in confs):
            print(self.presets[confs['preset']])
            if(confs['preset'] in self.presets):
                width = self.presets[confs['preset']]['width']
                height = self.presets[confs['preset']]['height']
                unit = self.presets[confs['preset']]['unit']
                self.calculate_pixel_size(width, height, unit)
            else:
                print("unknown preset.")
        elif(type(confs['size']) == dict):
            width = confs['size']['width']
            height = confs['size']['height']
            unit = confs['size']['unit']
            self.calculate_pixel_size(width, height, unit)
        else:
            print("parameter 'size' should be a dict with parameters width, height and unit, or send the name of a preset")
            return
        self.width_square = ceil(self.width/self.grid_width)
        self.height_square = ceil(self.height/self.grid_height)
        

    def load_cards(self, CARDS_FILE):
        if CARDS_FILE == None:
            self.mode = PREVIEW
        else:
            self.cards = CARDS_FILE
            # pf = open(CARDS_FILE, 'r')
            # self.cards = yaml.safe_load(pf)

    def calculate_pixel_size(self, width, height, unit):
        # produces an image with 300 dpi given dimensions and units
        # units can be mm, px or in
        if(unit == 'px'):
            self.width = width
            self.height = height
        elif(unit == 'in' or unit == 'mm'):
            self.width = ceil(self.dpi * width)
            self.height = ceil(self.dpi * height)
            if(unit == 'mm'):
                self.width = ceil(self.width/25.4)
                self.height = ceil(self.height/25.4)
        else:
            print("unknown unit: ", unit)


    def get_next_piece_of_layout(self):
        #yield next thing to render or end and reset
        order = sorted(self.layout, key=lambda x: x['level'])
        for i in order:
            yield i

    def square_to_pixels(self, square, end=False):
        #calculate where in pixels the grid square starts or ends

        column = ''.join(list(filter(lambda x: x in string.ascii_letters, square)))
        row = ''.join(list(filter(lambda x: x not in string.ascii_letters, square)))
        row = int(row)
        column = column.upper()
        
        # if len(column > 1):
        ## TODO: if there are more than A-Z columns
        
        loc_col = (ord(column) - 65) * self.width_square
        loc_row = (row-1) * self.height_square 
        if(end == True):
            loc_col += self.width_square
            loc_row += self.height_square
        ## TODO: except if end < start
        return ceil(loc_col), ceil(loc_row)

    def get_size_from_squares(self, start, end):
        return tuple(map(lambda i, j: i - j, self.square_to_pixels(end, True), self.square_to_pixels(start)))

    def render_preview(self):

        card = Image.new('RGBA', (self.width, self.height), (255,255,255,255))
        grid = ImageDraw.Draw(card)
        for i in range(0, self.grid_width + 1):
            for j in range(self.grid_height + 1):
                grid.line([((i+1) * self.width_square, j * self.height_square),
                 (i * self.width_square, j * self.height_square), 
                 (i * self.width_square, j+1 * self.height_square)], fill=128)
                fnt = ImageFont.truetype(os.path.join("util", "Font", "arial.ttf"), size=ceil(self.width/self.grid_width * 0.3))
                grid.multiline_text((i * self.width_square, j * self.height_square), chr(65+i) + str(j+1), fill=(128,128,128), font=fnt)
        
        part = self.get_next_piece_of_layout()
        for part_conf in part:
            if(part_conf["type"] == "image"):
                if(part_conf["default"] != None):
                    img_el = Image.open(os.path.join(self.img_dir, part_conf["default"]))
                    img_el = img_el.resize(self.get_size_from_squares(part_conf["start"], part_conf["end"]))
                    card.paste(img_el, self.square_to_pixels(part_conf["start"]))
                else:
                    # create image with stripes to show location
                    img_el = Image.new('RGBA', self.get_size_from_squares(part_conf["start"], part_conf["end"]), (245,245,245,245))
                    prv_grd = ImageDraw.Draw(img_el)
                    prv_grd.rectangle([(0,0), (img_el.width+3, img_el.height+3)])
                    fnt = ImageFont.truetype(os.path.join("util", "Font", "arial.ttf"), size=ceil(self.width/self.grid_width * 0.5))
                    prv_grd.multiline_text((0,0), part_conf["name"], fill=(10*part_conf['level'], 10*part_conf['level'], 10*part_conf['level']), font=fnt)
                    card.paste(img_el, self.square_to_pixels(part_conf["start"]))
            
            elif(part_conf["type"] == "text"):
                text = ImageDraw.Draw(card)
                if("scale" in part_conf):
                    scale = part_conf["scale"]
                else:
                    scale = 1
                fnt = ImageFont.truetype(os.path.join("util", "Font", "arial.ttf"), size=ceil(self.width/self.grid_width * scale))
                text.multiline_text((self.square_to_pixels(part_conf["start"])), part_conf["name"], font=fnt, fill=(0, 0, 0))

        return card
    
    def render(self, obj):
        card = Image.new('RGBA', (self.width, self.height), (255,255,255,255))
        part = self.get_next_piece_of_layout()
        #verify if it exists else use default value
        for part_conf in part:
            if(part_conf["name"] in obj):
                value = obj[part_conf["name"]]
            elif 'default' in part_conf:
                value = part_conf["default"]
            else:
                print("there must be a value or default for ", part_conf["name"])
            
            # Value can be null
            if(value != None):
                
                print("rendering: ", value)
                
                if(part_conf["type"] == "image"):
                    img_el = Image.open(os.path.join(self.img_dir, value))
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
                    fnt = ImageFont.truetype(os.path.join("util", "Font", "arial.ttf"), size=ceil(self.width/self.grid_width * scale))
                    text.multiline_text((self.square_to_pixels(part_conf["start"])), value, font=fnt, fill=(0, 0, 0))

        return card

    def run(self):
        count = 0
        if(self.mode == PREVIEW):
            card = self.render_preview()
            card.save(os.path.join(self.out_dir, "card_preview.png"))
        else:
            for obj in self.cards:
                count += 1
                card = self.render(obj)
                card.save(os.path.join(self.out_dir, "card_" + str(count) +".png"))


if __name__ == '__main__':
    
    cff = "config.yaml"
    cdf = "cards.yaml"
    imd = "images"
    ouf = "out"

    if(not os.path.isfile(cff) or not os.path.isfile(cdf) or not os.path.isdir(imd)):
        cff = input("enter the path of the configuration file: ")
        cdf = input("enter the path of the cards file: ")
        imd = input("enter the path of the directory with the images: ")

    b = Bacardi(cff, cdf, IMAGE_DIR=imd, OUTPUT_DIR=ouf)
    b.run()
