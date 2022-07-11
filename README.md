# BaCardI
Basic Card Imagemaker

This is a python script that generates card decks for board game prototypes from simple YAML descriptions. Contrary to other projects, it does not try to be a image editor or a spreadsheed editor, this is WYSIWYG.

You can download it and run `bacardi.py` from your command line, start the [FastAPI](https://fastapi.tiangolo.com/tutorial/) backend environment or use the web interface at [BacardiWeb](https://mateusumbelino.github.io/bacardlWeb/)

For the CLI you can run `python bacardi.py`. It expects files named "config.yaml", "cards.yamls" and a directory named "images" with the project images to be present at the root, if you do not have them you will be prompted to provide the necessary files.

For the fastAPI just have run `uvicorn main:app --reload` and navigate to `localhost:8000/docs`

## How To Use It

you'll need two files, one with the card layout and one with all the card descriptions. The card layout looks like this:

```
layout:
  - name: Titulo
    type: text
    start: C11
    end: G9
    level: 3
    color: "black"

  - name: Ilustra
    type: image
    start: B2
    end: H9
    level: 1

  - name: TextBox
    type: image
    start: B10
    end: H14
    level: 1
    default: tbt.png

  - name: Description
    type: text
    start: D12
    scale: 0.6
    end: G13
    level: 2

  - name: Fundo
    type: image
    start: A1
    end: I15
    level: 0
    default: bg.jpg

size: 
  width: 600
  heigth: 1000
  unit: px

grid:
  width: 9
  heigth: 15
```

It is a [YAML](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) file, with the necessary structure:
- **layout**: this keyword marks the start of the card layout. Every object inside of it is a piece of the design. Every piece has a:
  - name: the name under which it will be locared at the cards file (see more below)
  - type: wheter it's an image or a text
  - start and end: where in the design it is located (see grid details below)
  - level: Write here the order the elements will be rendered. For example: 0 is the lowest level (for the background) and will be rendered first, then levels 1-beyond will be pasted on top of it. This is not really fixed, you can write any number, there can be however many levels you want.
  - default: if this is something in the design that is present in every card, you can just set the value here and not bother writing it in the cards file. If there is a value in the cards file, it will overwrite this default.
  - **Text-only options**:
    - scale: for text, it changes the size of the font, a value of scale = 1 equals one whole square per default. Then you do the math.
    - color: the font color
- **size**: The size of the actual image itself, on 300dpi. It can be the name of one of the presets defined in `presets.yaml`, like 'poker', 'mini' or 'tarot', or a list with the card dimensions in milimiters (mm), inches (in), or pixels (px).
- **grid**: this is an important element and where the design happens. Basically, the number of squares you will need to divide the card to replicate your design.

### Example layout:

```
layout:
  - name: Titulo
    type: text
    start: C11
    end: G9
    level: 3

  - name: Ilustra
    type: image
    start: B2
    end: H9
    level: 1

  - name: TextBox
    type: image
    start: B10
    end: H14
    level: 1
    default: tbt.png

  - name: Description
    type: text
    start: D12
    scale: 0.6
    end: G13
    level: 2

  - name: Fundo
    type: image
    start: A1
    end: I15
    level: 0
    default: bg.jpg

size: 
  width: 600
  height: 1000
  unit: px

grid:
  width: 9
  height: 15
```

## The Grid

A grid is used to position the elements in the canvas. You define the size of the grid you needin the config, for example, the grid below is width: 9 and heigth: 11, and place each element accordingly, like in a chessboard, column names are letters of the alphabet and row names are numbers.

![Grid.png](https://github.com/istrangeloop/BaCardI/blob/main/doc/grid.png)

Then you'll just need to write the top left square your element occupies at the "start" parameter in your configuration yaml file and the bottom right square at the "end" parameter. 

## The Cards File

This is the file in which you will add and modify your cards one by one. It looks like this:
```
- Titulo: "Grifinória"
  Ilustra: Gryffindor.png
  Description: "A casa dos Corajosos"

- Titulo: "Corvinal"
  Ilustra: Ravenclaw.png
  Description: "A casa dos Sábios"

- Titulo: "Lufa-Lufa"
  Ilustra: Hufflepuff.png
  Description: "A casa dos Honestos"

- Titulo: "Sonserina"
  Ilustra: Slytherin.png
  Description: "A casa dos Ardilosos"
```
You can see it is really simple. It uses the names defined in the configuration file above and sets the value for them in each card. Any of the values anywhere can also be empty if you write the keyword Null. Values that were set as default in the config file will be overrided if something else is set instead under the corresponding keyword.

The result:

![cards.png](https://github.com/istrangeloop/BaCardI/blob/main/doc/cardstest-0.png)
