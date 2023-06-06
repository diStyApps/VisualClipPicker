import os 
os.system("")

class style():
    GREEN = '\033[32m'
    GREEN_BRIGHT= '\033[92m'

    RED = '\033[91m'
    RED_LIGHT = '\033[31m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    ORANGE = '\033[93m'

    RED_WHITE_TEXT = '\033[41m'
    RED_BLACK_TEXT = '\033[101m'
    GREEN_WHITE_TEXT = '\33[42m\33[1m'
    GREEN_BLACK_TEXT = '\33[102m\33[1m'

    BLUE_WHITE_TEXT = '\33[44m'
    BLUE_BLACK_TEXT = '\33[104m'
    BLUE_WHITE_BOLD_TEXT = '\33[44m\33[1m'
    BLUE_BLACK_BOLD_TEXT = '\33[104m\33[1m'

    # GREEN_WHITE_TEXT2 = '\33[42m'
    # GREEN_WHITE_TEXT2 = '\x1b[6;37;42m'


    # GREEN_BLACK_TEXT = '\33[102m'

    GRAY = '\033[30m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    RE = '\033[0m'
    WHAT = '\x1b[0m'

def cprint(color='green',text=''):
    GREEN = style.GREEN
    RED = style.RED
    RED_LIGHT = style.RED_LIGHT
    YELLOW = style.YELLOW
    BLUE = style.BLUE
    CYAN = style.CYAN
    MAGENTA = style.MAGENTA
    WHITE = style.WHITE
    GRAY = style.GRAY
    UNDERLINE = style.UNDERLINE
    RESET = style.RESET

    if color == 'GREEN':
        color = GREEN
    if color == 'RED':
        color = RED
    if color == 'RED_LIGHT':
        color = RED_LIGHT  
    if color == 'YELLOW':
        color = YELLOW
    if color == 'BLUE':
        color = BLUE
    if color == 'CYAN':
        color = CYAN
    if color == 'MAGENTA':
        color = MAGENTA
    if color == 'WHITE':
        color = WHITE
    if color == 'GRAY':
        color = GRAY
    if color == 'UNDERLINE':
        color = UNDERLINE        
    if color == 'RESET':
        color = RESET     

    print(f'{color}{text}',RESET)