#! /usr/bin/python3
from FB_barcode_util import do_position_barcode
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers about position.')
    parser.add_argument('--x_offset', metavar='X', type=int, nargs=1,
                   help='X offset position.')
    parser.add_argument('--y_offset', metavar='Y', type=int, nargs=1,
                   help='Y offset position.')
    args = parser.parse_args()
    do_position_barcode(args.x_offset[0], args.y_offset[0])


if __name__ == "__main__":
    parse_arguments()
