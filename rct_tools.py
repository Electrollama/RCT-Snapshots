from matplotlib import pyplot as plt
from PIL import Image
from file_tools import *
from numpy import array
from math import ceil, floor
from os.path import basename


file_list = (('RCT track', '.TP4'),('RCT screenshot', '.PCX'), ('BMP', '.bmp'))
test_file = "C:/Users\Karl Muster\PycharmProjects\Misc\Batflyer.TP4"
test_screen = 'C:/Program Files (x86)/Hasbro Interactive/RollerCoaster Tycoon/SCR7.PCX'
black = '00001010'
palette_path = 'C:/Users/Karl Muster/PycharmProjects/Misc/rct_palette.csv'
Palette = read_data(palette_path)

def read_tp4(color='r'):
    # Attempt to read track image file
    with open(file_dialog(file_list), 'rb') as f:
        dump = f.read()
    print(len(dump))
    print(dump[0], type(dump[0]))
    header = 400
    h = 200
    w = 258 #-4
    dump2 = []
    for i in range(h):
        start = i*w + header
        stop = (i+1)*w + header
        row = list(dump[start:stop])
        row = row[2:129] + row[131:] #remove vertical stripes, 4 pixels
        color_code = [read_8bit(n, color) for n in row]
        dump2.append(color_code)
    return dump2

def read_bmp2():
    path = file_dialog()
    im = Image.open(path)
    bmp_array = rgb_to_bit(array(im).tolist())
    return bmp_array

def read_bmp():
    path = file_dialog()
    return Image.open(path)

def convert_bmp(image):
    data = array(image).tolist()
    bmp_array = rgb_to_bit(data)
    return bmp_array

def tp4_header():
    result = []
    for i in range(56):
        result.append(144+i*2)
        result.append(i+1)
    for i in range(128):
        result.append(i * 2)
        result.append(i + 58)
    for i in range(16):
        result.append(i * 2)
        result.append(i + 187)
    print(len(result))
    return result

def write_tp4(bmp_array, name=None):
    size = [len(bmp_array), len(bmp_array[0])]
    elem_type = type(bmp_array[0][0])
    if size != [200, 254]:
        msg = 'Wrong array size ({}x{}) for .tp4 (200x254)'.format(size[0], size[1])
        raise IndexError(msg)
    elif elem_type is not int:
        msg = 'Wrong input type ({}, {}) for .tp4 (int)'
        msg = msg.format(elem_type, bmp_array[0][0])
        raise IndexError(msg)
    result = tp4_header()
    for row in bmp_array:
        result.append(127)
        result.append(0)
        result += row[:127]
        result.append(255)
        result.append(127)
        result += row[127:]
    if name is None:
        name = file_dialog(file_list)
    else:
        name = 'Track_Images\{}.TP4'.format(name)
    with open(name, 'wb') as f:
        f.write(bytearray(result))
    print('File', name, 'written.')

def plot_bitmap(bmp_array, color='r'):
    print(bmp_array)#, len(bmp_array[0]), bmp_array[0][0])
    Maps = {'r': 'Reds', 'g': 'Greens', 'b': 'Blues',
            'rgb': None, 'k': 'binary', 'n': 'nipy_spectral'}
    plt.imshow(bmp_array, cmap=Maps[color])
    plt.show()

def read_8bit_old(n, color='r'):
    bin_str = bin(n)[2:].zfill(8)
    if color == 'n':
        result = bin_str
    elif color == 'r':
        result = bin_str[0:3]
    elif color == 'g':
        result = bin_str[3:6]
    elif color == 'b':
        result = bin_str[6:]
    elif color == 'k':
        result = str(int(bin_str == '00001010'))
    elif color == 'rgb':
        red = round(read_8bit_old(n, 'r')*255/15)
        green = round(read_8bit_old(n, 'g')*255/15)
        blue = round(read_8bit_old(n, 'b')*255/7)
        return [int(n) for n in (red, green, blue)]
    else:
        result = '000'
    return int(result,2)

def read_8bit(n, color='r'):
    if color == 'n':
        n_index = Palette['n'].index(n)
        red = Palette['R'][n_index]
        green = Palette['G'][n_index]
        blue = Palette['B'][n_index]
        return [int(n) for n in (red, green, blue)]
    elif color == 'r':
        n_index = Palette['n'].index(n)
        result = Palette['R'][n_index]
    elif color == 'g':
        n_index = Palette['n'].index(n)
        result = Palette['G'][n_index]
    elif color == 'b':
        n_index = Palette['n'].index(n)
        result = Palette['B'][n_index]
    elif color == 'k':
        result = str(int(n == 10))
    elif color == 'rgb':
        red = round(read_8bit(n, 'r')*255/15)
        green = round(read_8bit(n, 'g')*255/15)
        blue = round(read_8bit(n, 'b')*255/7)
        return [int(n) for n in (red, green, blue)]
    else:
        result = 0
    return result

def round_color(rgb, Palette=Palette):
    scores = []
    r, g, b = rgb[0:3]
    size = len(Palette['n'])
    for i in range(size):
        r_err = (r - Palette['R'][i]) ** 2
        g_err = (g - Palette['G'][i]) ** 2
        b_err = (b - Palette['B'][i]) ** 2
        err = r_err + g_err + b_err
        if err == 0:
            return int(Palette['n'][i])
        scores.append((Palette['n'][i], err))
    min_score = 444
    n_opt = 0
    for elem in scores:
        if elem[1] < min_score:
            min_score = elem[1]
            n_opt = elem[0]
    return int(n_opt)

def rgb_to_bit(rgb_array):
    """
    result = []
    count = 0
    for row in rgb_array:
        temp = []
        count += 1
        for elem in row:
            temp.append(round_color(elem))
    """
    return [[round_color(elem) for elem in row] for row in rgb_array]

def make_preview(preview=True):
    test = read_bmp()
    pcx_file_name = basename(test.filename)[-4]
    print('Loaded image:', pcx_file_name)
    if preview:
        plot_bitmap(test, 'n')
    box = [int(input('lf:')),
           int(input('up:')),
           int(input('rt:')),
           int(input('dn:'))]
    box2 = auto_window_mult(box)
    cropped = test.crop(box2)
    sized = cropped.resize((254, 200), resample=Image.NEAREST)
    if preview:
        plot_bitmap(sized, 'n')
    bmp_array = array(sized).tolist()
    if type(bmp_array[0][0]) is list: #if from bitmap
        bmp_array = rgb_to_bit(bmp_array)
    ride_name = input('Ride Name:')
    if ride_name == '':
        ride_name = pcx_file_name
    write_tp4(bmp_array, ride_name)

def auto_window(box, pad=1.0):
    # acommodate re-sizing by making factors or multiples of 127x100
    left, up, right, down = box
    print('Start:', box)
    width, height = (right - left)*pad//2, (down - up)*pad//2
    center_x, center_y = (right + left)//2, (up + down)//2
    if width/height > 254/200: #too long
        print('Too wide')
        height = round(width * 200 / 254)
    else: #too tall
        print('Too tall')
        width = round(height * 254 / 200)
    left2, right2 = center_x - width, center_x + width
    up2, down2 = center_y - height, center_y + height
    box2 = [left2, up2, right2, down2]
    print('End:', box2)
    if (left2 < 0) or (right2 > 1000):
        print('Outside Horizontally')
        left2, right2 = max(left2, 0), min(right2, 1000)
        up2, down2 = center_y - height // 5, center_y + height // 5
        box2 = [left2, up2, right2, down2]
        return auto_window(box2, pad)
    elif (up2 < 30) or (down2 > 732):
        print('Outside Vertically')
        left2, right2 = center_x - width // 5, center_x + width // 5
        up2, down2 = max(up2, 30), min(down2, 732)
        box2 = [left2, up2, right2, down2]
        return auto_window(box2, pad)
    else:
        print('Acceptable Window')
        box2 = [left2, up2, right2, down2]
        return box2

def auto_window_mult(box):
    # acommodate re-sizing by making factors or multiples of 127x100
    left, up, right, down = box
    print('Start:', box)
    width, height = (right - left)//2, (down - up)//2
    center_x, center_y = (right + left)//2, (up + down)//2
    if width/height > 254/200: #too wide
        print('Too wide')
        factor = int(floor(width/127)) #round up to multiple of 127
    else: #too tall
        print('Too tall')
        factor = int(floor(height / 100))
    factor = max(1, factor)
    print('Factor:', factor)
    width = factor * 127
    height = factor * 100
    left2, right2 = center_x - width, center_x + width
    up2, down2 = center_y - height, center_y + height
    box2 = [left2, up2, right2, down2]
    print('End:', box2)
    if (left2 < 0) or (right2 > 1020):
        print('Outside Horizontally')
        left2, right2 = max(left2, 1), min(right2, 1019)
        up2, down2 = center_y - width // 5, center_y + width // 5
        box2 = [left2, up2, right2, down2]
        return auto_window_mult(box2)
    elif (up2 < 30) or (down2 > 732):
        print('Outside Vertically')
        left2, right2 = center_x - width // 5, center_x + width // 5
        up2, down2 = max(up2, 31), min(down2, 731)
        box2 = [left2, up2, right2, down2]
        return auto_window_mult(box2)
    else:
        print('Acceptable Window')
        box2 = [left2, up2, right2, down2]
        return box2

make_preview()

#test = read_tp4('n')
#plot_bitmap(test, 'n')