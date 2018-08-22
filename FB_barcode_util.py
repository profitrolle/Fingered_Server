#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import barcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import subprocess
from barcode import get

ID_POSITION = 1
ID_PRODUCT = 2
ID_PRODUCT_IN_ADVANCE = 3
# Defines the length og each field
LENGTH_ID_BC = 1
LENGTH_POS_X = 5
LENGTH_POS_Y = 5
LENGTH_PROD_ID = 4
LENGTH_PROD_X = 3
LENGTH_PROD_Y = 2
LENGTH_PROD_Z = 2

# LENGTH OF THE USED BARCODE
LENGHT_BC = 13

def compute_checksum(code):
    weight = [1,3] * 6
    magic = 10
    checksum = 0
    for i in range(12):         # traditional mod 10 checksum
        checksum = checksum + int(code[i]) * weight[i]
        
    z = ( magic - (checksum % magic) ) % magic
    
    if z < 0 or z >= magic:
        return None
        
    return z


def fill_digits(p_value, p_filler, p_size):
    """
    Takes interger and returns a string!
    """
    formatter = "%" + str(p_size) + "d"
    return (formatter % p_value).replace(" ", "0")


def fill_12_with_0(p_bc):
    len_bc = len(p_bc)
    if len_bc < LENGHT_BC-1:
        p_bc += (LENGHT_BC-len_bc)*"0"
    return p_bc
    
def create_product_barcode(p_id, p_x, p_y, p_z):
    """
    @param param: All must be integers!
    """
    product_barcode = fill_digits(ID_PRODUCT, 0, LENGTH_ID_BC) + \
        fill_digits(p_id, 0, LENGTH_PROD_ID) + \
        fill_digits(p_x, 0, LENGTH_PROD_X) + \
        fill_digits(p_y, 0, LENGTH_PROD_Y) + \
        fill_digits(p_z, 0, LENGTH_PROD_Z)
    product_barcode = fill_12_with_0(product_barcode)
    product_barcode += str(compute_checksum(product_barcode))
    return product_barcode


def create_position_barcode(p_x, p_y):
    """
    @param param: All must be integers!
    """
    position_barcode = fill_digits(ID_POSITION, 0, LENGTH_ID_BC) + \
        fill_digits(p_x, 0, LENGTH_POS_X) + \
        fill_digits(p_y, 0, LENGTH_POS_Y)
    position_barcode = fill_12_with_0(position_barcode)
    print(position_barcode)
    position_barcode += str(compute_checksum(position_barcode))        
    return position_barcode


def create_barcode(p_bc):
    len_bc = len(p_bc)
    if len_bc < LENGHT_BC:
        p_bc += (LENGHT_BC-len_bc)*"0"
    name = str(p_bc)
    ean = barcode.get('ean13', str(p_bc), writer=barcode.writer.ImageWriter())
    filename = ean.save(name)    
    return name, int(ean.ean)


def add_product_size(p_name, p_length, p_height, p_depth):
    img = Image.open(p_name + '.png')
    img.resize((800, 600))
    new_img = Image.new('RGB', (img.size[0], img.size[1] * 2), "white")
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf", 50)
    draw.text((0, img.size[1]), "X = " + str(p_length) + " - Y = " + str(p_height) +\
              " - Z = " + str(p_depth), (0, 0, 0), font=font)
    new_img.save(p_name + '.png')


def add_position_coord(p_name, p_x, p_y):
    img = Image.open(p_name + '.png')
    img.resize((800, 600))
    new_img = Image.new('RGB', (img.size[0], img.size[1] * 2), "white")
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf", 50)
    draw.text((0, img.size[1]), "X = " + str(p_x) + " - Y = " + str(p_y), font=font)
    new_img.save(p_name + '.png')


def print_barcode(p_filename):
    subprocess.call(["lp", "-d", "DYMO_LabelWriter_450", "-o", "landscape",
                     "-o", "media=Custom.89x41mm","-o", "fit-to-page",
                     p_filename + ".png"])


def remove_barcode(p_filename):
    os.remove(p_filename + ".png")

def get_product_barcode_info(p_barcode):
    start_position = LENGTH_ID_BC
    end_position = start_position + LENGTH_PROD_ID
    board_id = p_barcode[start_position:end_position]
    start_position += LENGTH_PROD_ID
    end_position += LENGTH_PROD_X
    length = p_barcode[start_position:end_position]
    start_position += LENGTH_PROD_X
    end_position += LENGTH_PROD_Y
    height = p_barcode[start_position:end_position]
    start_position += LENGTH_PROD_Y
    end_position += LENGTH_PROD_Z
    depth = p_barcode[start_position:end_position]
    return int(length), int(height), int(depth), int(board_id)

def get_position_barcode_info(p_barcode):
    start_position = LENGTH_ID_BC
    end_position = start_position + LENGTH_POS_X
    length = p_barcode[start_position:end_position]
    start_position += LENGTH_POS_X
    end_position += LENGTH_POS_Y
    height = p_barcode[start_position:end_position]
    return int(length), int(height)

def do_product_barcode(p_barcode):
    bc_name, _ = create_barcode(p_barcode)
    length, height, depth, _ = get_product_barcode_info(p_barcode)
    add_product_size(bc_name, length, height, depth)
#     print_barcode(bc_name)
    remove_barcode(bc_name)

def do_position_barcode(p_x, p_y):
    barcode = create_position_barcode(p_x, p_y)
    bc_name, _ = create_barcode(barcode)
    length, height = get_position_barcode_info(barcode)
    add_position_coord(bc_name, length, height)
    print_barcode(bc_name)
    remove_barcode(bc_name)

if __name__ == '__main__':
    pos_bc = create_product_barcode(1, 153, 32, 50)
    name, eeean = create_barcode(pos_bc)
    add_product_size(name, 60, 25, 50)
    print(pos_bc)
#     print_barcode(name)
    
