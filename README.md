# BaCardI
Basic Card Imagemaker

This is a python script that generates card decks for board game prototypes from simple YAML descriptions. Contrary to other projects, it does not try to be a image editor or a spreadsheed editor, this is WYSIWYG.

## How To Use It

you'll need two files, one with the card layout and one with all the card descriptions. The card layout looks like this:

```
layout:
  - name: Titulo
    type: text
    start: B1
    end: E1
    level: 3

  - name: Ilustra
    type: image
    start: B2
    end: E6
    level: 1

  - name: TextBox
    type: image
    start: B7
    end: E9
    level: 1
    default: tbt.png

  - name: Description
    type: text
    start: A4
    end: F6
    level: 2

  - name: Fundo
    type: image
    start: A1
    end: F10
    level: 0
    default: bg.jpg

size: 
  width: 600
  heigth: 1000
  unit: px

grid:
  width: 6
  heigth: 10
```

It is a [YAML](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) file, with the necessary structure:
- layout: this keyword marks the start of the card layout. Every object inside of it is a piece of the design. Every piece has a:
  - name: the name under which it will be locared at the cards file (see more below)
  - type: wheter it's an image or a text
  - start and end: where in the design it is located (see grid details below)
  - level: things often go atop of each other. Write here the order the elements will be rendered. For example: 0 is the lowest level (for the background) and will be rendered first, then levels 1-beyond will be pasted on top of it. This is not really fixed, you can write any number, there can be however many levels you want.
  - default: if this is something in the design that is present in every card, you can just set the value here and not bother writing it in the cards file.
  size: it can be a string or a list with the card dimensions in milimiters (mm), inches (in), or pixels (px).
  grid: this is an important element and where the design happens. Basically, the number of squares you will need to divide the card to replicate your design.

## The Grid

A grid is used to position the elements in the canvas. You define the size of the grid you need, and place each element accordingly, like in a chessboard, column names are letters of the alphabet and row names are numbers.

![Grid.png](https://github.com/istrangeloop/BaCardI/blob/main/grid.png)

Then you'll just need to write the top left square your element occupies at the "start" parameter in your configuration yaml file and the bottom right square at the "end" parameter. 

## The Cards File

This is the file in which you will add and modify your cards one by one. It looks like this:
```
- Titulo: Grifinoria
  Ilustra: Gryffindor.png
  Description: A casa dos Corajosos

- Titulo: Corvinal
  Ilustra: Ravenclaw.png
  Description: A casa dos Sábios

- Titulo: Lufa-Lufa
  Ilustra: Hufflepuff.png
  Description: A casa dos Honestos

- Titulo: Sonserina
  Ilustra: Slytherin.png
  Description: A casa dos Ardilosos
```
You can see it is really simple. It uses the names we have defined above and sets the value for them in each card. Any of the values anywhere can also be empty if you write the keyword Null.

The result:

![cards.png](https://github.com/istrangeloop/BaCardI/blob/main/cardstest-0.png)
