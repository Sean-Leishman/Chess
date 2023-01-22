import io
import svgutils
import pygame

WIDTH = 600
HEIGHT = 600

SQUARE_SIZE = WIDTH / 8

WHITE = (255,255,255)
BLACK  = (0,0,0)

COLOR = {
    WHITE: ['WHITE',(255,255,255)],
    BLACK : ['BLACK',(0,0,0)]
}

INITIALS = {
    "Pawn":"p",
    "Queen":"q",
    "King":"k",
    "Bishop":"b",
    "Knight":"n",
    "Castle":"r",
}

COLOR_INITIAL = {
    "WHITE":"l",
    "BLACK":"d"
}

white_letter_coord = ['a','b','c','d','e','f','g','h']

def convert_pos_to_coord(pos, turn):
    """
    Converts position of piece into a coordinate in chess formate (eg. A1)

    :param pos: List[int]
        represents position -> range [[1..8], [1..8]
    :param turn: [str, (int,int,int)]
        turn of color String of Color, RGB value for Color
    :return: str
        coordinate of position with turn listed
    """
    if turn == COLOR[WHITE]:
        return str(white_letter_coord[pos[0]] + str(8 - pos[1]))
    elif turn == COLOR[BLACK]:
        return str(list(reversed(white_letter_coord))[pos[0]] + str(1 + pos[1]))

def load_and_scale_svg(filename, scale):
    """
    Get image from a file and resize into a certain scale and return as Pygame Image

    :param filename: str
        filename representing svg file
    :param scale: float
        attribute to scale by
    :return:
        Pygame Image object of rescaled file
    """
    svg_string = open(filename, "rt").read()
    start = svg_string.find('<svg')
    if start > 0:
        svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]

    start = svg_string.find('<g style="')
    if start > 0:
        svg_string = svg_string[:start + 10] + f'overflow=visible; ' + svg_string[start + 10:]

    svg = svgutils.compose.SVG(filename)
    svg.scale(scale)
    figure = svgutils.compose.Figure(float(svg.height) * 2, float(svg.width) * 2, svg)
    figure.save('svgNew.svg')
    svg_string = open('svgNew.svg', "rt").read()
    print(svg_string)
    return pygame.image.load(io.BytesIO(svg_string.encode()))
