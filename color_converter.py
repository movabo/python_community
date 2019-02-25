# -*- coding: utf-8 -*-

"""Convert between color systems and color representations.
Usage: <rgb|hex|yiq|hls|hsv> <color (comma seperated)>
Examples: rgb 100 60 20
          hsv 0.5 0.4 0.3
"""

from albertv0 import *
from colorsys import *
import re
import os
import traceback
import tempfile

"""
In the following, all color parameters (except hex of course) need three
values.

For consistency between conversion methods are all conversion methods
lower_case_with_underscores.
"""

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Color Converter"
__version__ = "1.0"
__author__ = "Moritz Bock"
__dependencies__ = []


hex_pattern = re.compile("^([a-zA-Z0-9]{3}|[a-zA-Z0-9]{6})$")
"""Regular expression matching hex colors (without #)."""

svg = '<svg viewBox="0 0 1 1"><rect width="1" height="1" fill="{}" /></svg>'
"""One colored SVG string containing one format field which should be a
(fill-)color."""

color_file_location = None
"""Location of the last used color file."""


###########
# Parsers #
###########

def baseParser(string):
    """Basic parser for parsing colors with three values.

    Args:
        string (str): Comma-separated string representation of
            the color.

    Returns:
        tuple or False: Three-tuple of the values in the string. False
        when not parsable.
    """
    for remove in remove_strings:
        string = string.replace(remove, "")
    color = string.split(",")
    if len(color) is not 3:
        return False
    try:
        return tuple(map(float, color))
    except Exception:
        return False


def minMaxParser(string, minimum=0, maximum=255):
    """Parser where each of the three values should be in
    a defined range.

    Args:
        string (str): Comma-separated string representation of
            the color.
        minimum (float or int): Minimum of each value of the color.
        maximum (float or int): Maximum of each value of the color.

    Returns:
        tuple or False: Three-tuple of the values in the string. False
        when not parsable.
    """
    color = baseParser(string)
    if not color:
        return False
    return tuple(map(lambda x: min(maximum, max(minimum, x)), color))


def getMinMaxParser(minimum=0, maximum=255):
    """Get a minMaxParser where minimum and maximum is
    previously (here) set.

    Args:
        minimum (float or int): Minimum of each value of the color.
        maximum (float or int): Maximum of each value of the color.

    Returns:
        function: minMaxParser where minimum and maximum is already set
        and only one parameter (the color-string) is required.
    """
    return lambda color: minMaxParser(color, minimum, maximum)


def hexParser(string):
    """Parser for parsing hexadecimal (rgb) colors.

    Args:
        string (str): Hex color to parse.

    Returns:
        str or False: Hex color (without #) contained in the string or
        False if it is not a valid hex string.
    """
    string = string.lstrip(" ")
    if len(string) is 0:
        return False
    hex = string.lstrip("#")
    if len(hex) not in (3, 6):
        return False
    if hex_pattern.match(hex):
        return (hex,)
    else:
        return False


def HLSHSVParser(string):
    """Parse a comma-separated string to HLS / HSL or HSV.

    Args:
        string (str): HLS / HSL or HSV color to parse.

    Returns:
        tuple: Three values: HLS / HSL or HSV.
    """
    color = baseParser(string)
    return (color[0] % 360,
            min(100, max(0, color[1])),
            min(100, max(0, color[2])))


parsers = {
    "rgb": minMaxParser,
    "hex": hexParser,
    "yiq": getMinMaxParser(-1, 1),
    "hls": HLSHSVParser,
    "hsl": HLSHSVParser,
    "hsv": HLSHSVParser
}
"""Parsers to be used for which color type."""


##############
# Converters #
##############

def rgb_to_hex(r, g, b):
    """Convert rgb to hex.

    Args:
        r (float): Red-portion of the color.
        g (float): Green-portion of the color.
        b (float): Blue-portion of the color.

    Returns:
        str: Hex-representation of the color.
    """
    rgb = (r, g, b)
    rgb = tuple(map(lambda x: int(min(255, max(0, x*255))), rgb))
    return "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])


def hex_to_rgb(hex):
    """Convert hex to rgb.

    Args:
        hex (str): Hex-representation of the color.

    Returns:
        tuple: Three values: The red, green, and blue-portion of the
        color.
    """
    hex = hex.lstrip("#")
    if len(hex) is 3:
        hex = ''.join([char*2 for char in hex])
    return tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))


def toggleHSLHLS(h, s_l_1, s_l_2):
    """Transform HLS to HSL or HSL to HLS.

    Args:
        h (float or int): Hue part of the color.
        s_l_1 (float or int): Saturation or value part of the color.
        s_l_2 (float or int): Saturation or value part of the color.

    Returns:
        tuple: HSL or HLS representation of the color
    """
    return (h, s_l_2, s_l_1)


def transformHSLHSV(h, s_l_v_1, s_l_v_2):
    """Transform HLS / HSL or HSV with values in [0, 1] to 'normal'
    HLS / HSL or HSV.

    Args:
        h (float): Normalized hue part of the color.
        s_l_v_1 (float): Normalized saturation, lightness, or value part
            of the color.
        s_l_v_2 (float): Normalized saturation, lightness, or value part
            of the color.

    Returns:
        tuple: The transformed 'unnormalized' HLS / HSL or HSV.
    """
    return (h * 360, s_l_v_1 * 100, s_l_v_2 * 100)


converters_from = {
    "rgb": lambda r, g, b: (r / 255, g / 255, b / 255),
    "hex": hex_to_rgb,
    "yiq": yiq_to_rgb,
    "hls": lambda h, l, s: hls_to_rgb(h % 360 / 360, l / 100, s / 100),
    "hsl": lambda h, s, l: hls_to_rgb(h % 360 / 360, l / 100, s / 100),
    "hsv": lambda h, s, v: hsv_to_rgb(h % 360 / 360, v / 100, s / 100)
}
"""Converters to convert from a system to rgb."""


converters_to = {
    "rgb": lambda r, g, b: (r * 255, g * 255, b * 255),
    "hex": rgb_to_hex,
    "yiq": rgb_to_yiq,
    "hls": lambda r, g, b: transformHSLHSV(*rgb_to_hls(r, g, b)),
    "hsl": lambda r, g, b: toggleHSLHLS(*transformHSLHSV(*rgb_to_hls(r, g, b))),
    "hsv": lambda r, g, b: transformHSLHSV(*rgb_to_hls(r, g, b))
}
"""Converters to convert from rgb to a system."""


remove_strings = list(dict.keys(converters_from)) + ["(", ")", " ", "%", "°"]
"""String to remove when parsing the colors."""


#################
# Color Helpers #
#################

def colorString(system, color):
    """Create a string from a color.

    Args:
        system (str): The color system to create the string of.
        color (tuple): Tuple containing the values of the portions
            of the color.

    Returns:
        str: Color as string representation.
    """
    if system == "hex":
        if type(color) in (list, tuple):
            return "#" + color[0]
        return color
    elif system in ("hls", "hsl", "hsv"):
        return system + "({0:g}, {1:g}%, {2:g}%)".format(*color)
    return system + "({0:g}, {1:g}, {2:g})".format(*color)


def colorSVG(r, g, b):
    """Get a one-colored svg as bytes.

    Args:
        r (float): Red-portion of the color.
        g (float): Green-portion of the color.
        b (float): Blue-portion of the color.

    Returns:
        byte: One colored svg with the specified color as byte-string.
    """
    color = colorString("rgb", converters_to["rgb"](r, g, b))
    return bytes(svg.format(color), encoding="utf8")


def colorFile(r, g, b):
    """Create a temporary file containing a one-colored svg.

    Args:
        r (float): Red-portion of the color.
        g (float): Green-portion of the color.
        b (float): Blue-portion of the color.

    Returns:
        str: Location of the created SVG-file.
    """
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(colorSVG(r, g, b))
    return f.name


#################
# Item creation #
#################

def buildItem(completion,
              source_system,
              destination_system,
              source_color,
              destination_color,
              icon_file):
    """Build an item to show in albert.

    Args:
        completion (str): The completion string of the item. This string
            will be used to replace the input line when the user hits
            the Tab key on an item.
        source_system (str): Color system of the source color.
        destination_system (str): Color to which the source color was
            converted.
        source_color (tuple): Source color.
        destination_color (tuple): converted color.
        icon_file (str): Location of the icon file.

    Returns:
        Item: An item containing a converted color.
    """
    item = Item(id=__prettyname__, completion=completion)
    item.text = colorString(destination_system, destination_color)
    item.subtext = "Converting {} to {}" \
        .format(colorString(source_system, source_color), destination_system)
    item.addAction(ClipAction("Copy to clipboard", item.text))
    item.icon = icon_file
    return item


def run(query):
    """Run the script to search if the query matches a color and convert
    these colors.

    Args:
        query (Query): Query object representing the current query
            execution.

    Returns:
        list or None: Items of the converted colors.
    """
    global color_file_location
    source_system = query.string[:3]
    if source_system not in converters_from:
        return

    # Delete old temp file
    if color_file_location:
        os.remove(color_file_location)
        color_file_location = None

    # Check if valid color
    string = query.string[3:]
    color = parsers[source_system](string)
    if not color:
        return

    rgb = converters_from[source_system](*color)
    color_file_location = colorFile(*rgb)

    # Convert to all colors and add them.
    results = []
    for destination_system, func in converters_to.items():
        if source_system == destination_system:
            continue
        item = buildItem(query.rawString,
                         source_system,
                         destination_system,
                         color,
                         func(*rgb),
                         color_file_location)
        results.append(item)
    return results


def handleQuery(query):
    """Run the script to search if the query matches a color and convert
    these colors.

    Args:
        query (Query): Query object representing the current query
            execution.

    Returns:
        list or None: Items of the converted colors.
    """
    try:
        return run(query)
    except Exception as e:
        critical(''.join(traceback.format_exception(etype=type(e),
                 value=e,
                 tb=e.__traceback__)))
