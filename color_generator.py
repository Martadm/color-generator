#!/usr/bin/python
"""
Script for generating a new color depending on the selected mode.

Author: Marta Dmitrzak
"""

import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mode', '-m',
                    default='mix',
                    const='mix',
                    nargs='?',
                    choices=['mix', 'lowest', 'highest', 'mix-saturate'],
                    help='mix, lowest, highest or mix-saturate (default: %(default)s)')
parser.add_argument('color', type=str, nargs='*')
args = parser.parse_args()
config = vars(args)
print(config)
mode = config['mode']
colorcode = config['color']

MIN2 = (2, 7,)
MIN3 = (3, 0,)
if not (sys.version_info == MIN2 or sys.version_info >= MIN3):
    raise EnvironmentError("Python version should be 2.7 or 3.x")


class Color:
    """Calculate parameters of the given color."""

    def __init__(self, r: int, g: int, b: int, a: int):
        """
        Init Color class using color values.

        :param r: int (value of red, from 0 to 255)
        :param g: int (value of green, from 0 to 255)
        :param b: int (value of blue, from 0 to 255)
        :param a: int (value of blue, from 0 to 255)
        """
        self.r = r / 255.
        self.g = g / 255.
        self.b = b / 255.
        self.a = a / 255.

    def color_to_hex(self) -> str:
        """
        Convert RGBA color codes to hex format.

        :return: string (hex code of color)
        """
        hex_red = "{:02x}".format(int(self.r * 255.))
        hex_green = "{:02x}".format(int(self.g * 255.))
        hex_blue = "{:02x}".format(int(self.b * 255.))
        hex_alpha = "{:02x}".format(int(self.a * 255.))
        return '#' + hex_red + hex_green + hex_blue + hex_alpha

    def calc_hue(self) -> float:
        """
        Calculate hue of color.

        :return: float (hue value, from 0 to 360)
        """
        cmax = max(self.r, self.g, self.b)
        cmin = min(self.r, self.g, self.b)
        delta = cmax - cmin

        if delta == 0:
            return 0
        elif cmax == self.r:
            h = (self.g - self.b) / delta * 60
        elif cmax == self.g:
            h = (self.b - self.r) / delta * 60
        else:
            h = (self.r - self.g) / delta * 60

        if h < 0:
            h += 360

        return h

    @staticmethod
    def calc_saturation(r: int, g: int, b: int) -> float:
        """
        Calculate saturation of color.

        :param r: int (value of red, from 0 to 255)
        :param g: int (value of green, from 0 to 255)
        :param b: int (value of blue, from 0 to 255)
        :return: float (saturation value, from 0 to 1)
        """
        r /= 255.
        g /= 255.
        b /= 255.
        if max(r, g, b) != min(r, g, b):
            saturation = (max(r, g, b) - min(r, g, b)) / (1 - abs(max(r, g, b) + min(r, g, b) - 1))
        else:
            saturation = 0

        return saturation

    def calc_lightness(self) -> float:
        """
        Calculate lightness of color.

        :return: float (lightness value, from 0 to 1)
        """
        lightness = (max(self.r, self.g, self.b) + min(self.r, self.g, self.b)) / 2

        return lightness


def format_color(color: str) -> list:
    """
    Convert color code to list of RGBA values from 0 to 255.

    :param color: string (color code)
    :return: list (list of R, G, B and A values)
    """
    if re.search(r"^([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", color):
        color_code_length = len(color)
        if color_code_length == 3:
            red_value = int('0x' + color[0] * 2, 0)
            green_value = int('0x' + color[1] * 2, 0)
            blue_value = int('0x' + color[2] * 2, 0)
            alpha_value = int('0xff', 0)
        else:
            red_value = int('0x' + color[:2], 0)
            green_value = int('0x' + color[2:4], 0)
            blue_value = int('0x' + color[4:6], 0)
            alpha_value = int('0x' + color[6:], 0) if color_code_length == 8 else int('0xff', 0)

        return [red_value, green_value, blue_value, alpha_value]
    elif re.search(r"^([0-9]{1,3},){3}[0-9]{1,3}$", color):
        color = color.split(',')
        red_value = int(color[0])
        green_value = int(color[1])
        blue_value = int(color[2])
        alpha_value = int(color[3])
        return [red_value, green_value, blue_value, alpha_value]

    else:
        return None


def read_colors(name_of_file: str, color_cli: list) -> list:
    """
    Read file and save RGBA values to a list.

    Convert formats: #rrggbbaa, #rrggbb, #rgb, and 0,0,0,0.
    :param name_of_file: string (name of file with color codes)
    :param color_cli: list (list of colors from CLI)
    :return: list (list of all RGBA values from 0 to 255)
    """
    try:
        a_file = open(name_of_file, "r")
    except IOError as e:
        print(e)
        quit()

    reds = []
    greens = []
    blues = []
    alphas = []
    lines = a_file.read()
    content_lines = lines.split("\n")
    content_lines.extend(color_cli)

    for line in content_lines:
        line = line.rstrip()
        color_rgba = format_color(line)
        if color_rgba is not None:
            reds.append(color_rgba[0])
            greens.append(color_rgba[1])
            blues.append(color_rgba[2])
            alphas.append(color_rgba[3])
        else:
            print("Invalid color format!\n")
            continue
    a_file.close()
    return [reds, greens, blues, alphas]


def mix(red_mix: list, green_mix: list, blue_mix: list, alpha_mix: list) -> list:
    """
    Calculate new color, that is average of values RGBA.

    :param red_mix: list (list of red values, from 0 to 255)
    :param green_mix: list (list of green values, from 0 to 255)
    :param blue_mix: list (list of blue values, from 0 to 255)
    :param alpha_mix: list (list of blue values, from 0 to 255)
    :return: list (list of new RGBA values)
    """
    new_red_mix = sum(red_mix) / len(red_mix)
    new_green_mix = sum(green_mix) / len(green_mix)
    new_blue_mix = sum(blue_mix) / len(blue_mix)
    new_alpha_mix = sum(alpha_mix) / len(alpha_mix)
    mixed_color = [int(round(new_red_mix, 0)), int(round(new_green_mix, 0)), int(round(new_blue_mix, 0)),
                   int(round(new_alpha_mix, 0))]
    return mixed_color


def lowest(red_low: list, green_low: list, blue_low: list, alpha_low: list) -> list:
    """
    Calculate new color, that is created from the lowest RGBA values.

    :param red_low: list (list of red values, from 0 to 255)
    :param green_low: list (list of green values, from 0 to 255)
    :param blue_low: list (list of blue values, from 0 to 255)
    :param alpha_low: list (list of blue values, from 0 to 255)
    :return: list (list of new RGBA values)
    """
    new_red_low = min(red_low)
    new_green_low = min(green_low)
    new_blue_low = min(blue_low)
    new_alpha_low = min(alpha_low)
    lowest_color = [new_red_low, new_green_low, new_blue_low, new_alpha_low]
    return lowest_color


def highest(red_high: list, green_high: list, blue_high: list, alpha_high: list) -> list:
    """
    Calculate new color, that is created from the highest RGBA values.

    :param red_high: list (list of red values, from 0 to 255)
    :param green_high: list (list of green values, from 0 to 255)
    :param blue_high: list (list of blue values, from 0 to 255)
    :param alpha_high: list (list of blue values, from 0 to 255)
    :return: list (list of new RGBA values)
    """
    new_red_high = max(red_high)
    new_green_high = max(green_high)
    new_blue_high = max(blue_high)
    new_alpha_high = max(alpha_high)
    highest_color = [new_red_high, new_green_high, new_blue_high, new_alpha_high]
    return highest_color


def average_saturation(red_avg: list, green_avg: list, blue_avg: list) -> float:
    """
    Calculate average saturation.

    :param red_avg: list (list of red values, from 0 to 255)
    :param green_avg: list (list of green values, from 0 to 255)
    :param blue_avg: list (list of blue values, from 0 to 255)
    :return: float (value of average saturation)
    """
    saturations = []
    for i in range(len(red_avg)):
        s = Color.calc_saturation(red_avg[i], green_avg[i], blue_avg[i])
        saturations.append(s)
    return sum(saturations) / len(saturations)


def mix_saturate(red_mixsat: list, green_mixsat: list, blue_mixsat: list, alpha_mixsat: list, avg_saturation: float) \
        -> list:
    """
    Calculate new color, which is last color with new saturation.

    The function changes maximum color value, if average saturation is higher than saturation of this color, otherwise
    it changes minimum color value.
    :param red_mixsat: list (list of red values, from 0 to 255)
    :param green_mixsat: list (list of green values, from 0 to 255)
    :param blue_mixsat: list (list of blue values, from 0 to 255)
    :param alpha_mixsat: list (list of blue values, from 0 to 255)
    :param avg_saturation: float (value of average saturation)
    :return: list (list of new RGBA values)
    """
    last_red_mixsat = red_mixsat[-1]
    last_green_mixsat = green_mixsat[-1]
    last_blue_mixsat = blue_mixsat[-1]
    last_alpha_mixsat = alpha_mixsat[-1]
    last_color = [last_red_mixsat, last_green_mixsat, last_blue_mixsat]
    cmax_mixsat = max(last_color)
    index_max = last_color.index(cmax_mixsat)
    cmin_mixsat = min(last_color)
    index_min = last_color.index(cmin_mixsat)
    cmax_mixsat /= 255.
    cmin_mixsat /= 255.
    last_saturation = Color.calc_saturation(last_red_mixsat, last_green_mixsat, last_blue_mixsat)
    if avg_saturation > last_saturation and cmax_mixsat != cmin_mixsat:
        new_cmax_first = (2 * avg_saturation - avg_saturation * cmin_mixsat + cmin_mixsat) / (avg_saturation + 1)
        new_cmax_second = (- avg_saturation * cmin_mixsat - cmin_mixsat) / (avg_saturation - 1)
        new_cmax = new_cmax_first if 0 <= new_cmax_first <= 1 else new_cmax_second
        last_color[index_max] = int(round(new_cmax * 255))
    elif avg_saturation < last_saturation and cmax_mixsat != cmin_mixsat:
        new_cmin_first = (2 * avg_saturation - avg_saturation * cmax_mixsat - cmax_mixsat) / (avg_saturation - 1)
        new_cmin_second = (cmax_mixsat - avg_saturation * cmax_mixsat) / (avg_saturation + 1)
        new_cmin = new_cmin_first if 0 <= new_cmin_first <= 1 else new_cmin_second
        last_color[index_min] = int(round(new_cmin * 255))
    else:
        last_color = last_color

    last_color.append(last_alpha_mixsat)
    return last_color


if __name__ == '__main__':
    filename = "colors.txt"
    color_values = read_colors(filename, colorcode)
    red = color_values[0]
    green = color_values[1]
    blue = color_values[2]
    alpha = color_values[3]

    mean_saturation = average_saturation(red, green, blue)

    if mode == 'mix':
        new_color = mix(red, green, blue, alpha)
    elif mode == 'lowest':
        new_color = lowest(red, green, blue, alpha)
    elif mode == 'highest':
        new_color = highest(red, green, blue, alpha)
    elif mode == 'mix-saturate':
        new_color = mix_saturate(red, green, blue, alpha, mean_saturation)

    new_red = new_color[0]
    print("New red value: ", new_red)
    new_green = new_color[1]
    print("New green value: ", new_green)
    new_blue = new_color[2]
    print("New blue value: ", new_blue)
    new_alpha = new_color[3]
    print("New alpha value: ", new_alpha)

    color_object = Color(new_red, new_green, new_blue, new_alpha)
    color_hex = color_object.color_to_hex()
    print("Color in hex: ", color_hex)
    hue = color_object.calc_hue()
    print("Hue: ", round(hue, 2))
    saturation = color_object.calc_saturation(new_red, new_green, new_blue)
    print("Saturation: ", round(saturation, 2))
    lightness = color_object.calc_lightness()
    print("Lightness: ", round(lightness, 2))
