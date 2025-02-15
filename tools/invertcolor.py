# /usr/bin/python
#
# GNU General Public License Usage
# This file may be used under the terms of the GNU
# General Public License version 3 as published by the Free Software
# Foundation. Please review the following information to
# ensure the GNU General Public License version 3 requirements
# will be met: https://www.gnu.org/licenses/gpl-3.0.html.

__author__ = "Michele Albano"
__copyright__ = "Copyright 2023"
__credits__ = ["Michele Albano"]
__license__ = "GPL"
__version__ = "0.91"
__maintainer__ = "Michele Albano"
__email__ = "michele.albano@gmail.com"
__status__ = "Prototype"


"""
This program enters recursively a folder containing a Mixxx skin, and creates
an "inverted color" skin.
In particular, it copies the directory structure and the .png / .psd files
from the src directory to the current directory, and it creates svg /
xml / ... files where the codes for the colors (e.g.: #001122) are
inverted (#ffffff - #001122).

RUN THIS FILE FROM THE FOLDER YOU WANT TO POPULATE WITH THE NEW SKIN!

For an example of usage, run
python3 invertcolor.py
"""

import sys
import re
import pathlib
import os
import shutil


def from_hex(hexdigits):
    return int(hexdigits, 16)


def invert_color(len, line):
    regge1 = "^[0-9A-F]{" + str(len) + "}[^0-9a-fA-F]"
    regge2 = "^[0-9a-f]{" + str(len) + "}[^0-9a-fA-F]"
    p1 = re.compile(regge1)
    p2 = re.compile(regge2)
    tokens = line.split("#")
    ret = tokens.pop(0)
    for tok in tokens:
        m1 = p1.search(tok)
        m2 = p2.search(tok)
        if m1:
            val = from_hex("f" * len) - from_hex("0x" + m1.group()[:-1])
            ret += "#" + f"{val:#0{len+2}x}"[2:] + tok[len:]
        elif m2:
            val = from_hex("f" * len) - from_hex("0x" + m2.group()[:-1])
            ret += "#" + f"{val:#0{len+2}x}"[2:] + tok[len:]
        else:
            ret += "#" + tok
    ret = re.sub("PaleMoon", "PaleSun", ret);
    ret = re.sub("palemoon", "palesun", ret);
    return ret


def process_binary(src, dst):
    print("copying from " + src + " to " + dst)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)


def process_file(filename):
    fp1 = open(filename, "r")
    lines = fp1.readlines()
    output = ""
    for line in lines:
        output += invert_color(3, invert_color(6, line))
    fp1.close()
    return output


def process_dir(rootdir, where):
    desktop = pathlib.Path(rootdir + where)
    for item in desktop.iterdir():
        filename = os.path.basename(str(item))
        newwhere = where + os.path.sep + filename
        if item.is_file():
            something, file_extension = os.path.splitext(newwhere)
            if file_extension == ".png" or file_extension == ".psd":
                # currently, I consider every non-PNG file as
                # text to be processed
                process_binary(str(item), newwhere)
            else:
                processed_file = process_file(str(item))
                fp2 = open(newwhere, "w")
                fp2.write(processed_file)
                fp2.close()
        else:
            print("create dir " + newwhere)
            if not os.path.exists(newwhere):
                os.makedirs(newwhere)
            process_dir(rootdir, newwhere)


if len(sys.argv) < 2:
    print("tell me where to find the source skin")
    print("for example:")
    print("md " + os.path.normpath("Mixxx/res/skins/LateNight/palesun"))
    print("cd " + os.path.normpath("Mixxx/res/skins/LateNight/palesun"))
    print("cd " + os.path.normpath("Mixxx/skins/LateNight/palesun"))
    print(
        "python3 "
        + os.path.normpath("../../../../tools/invertcolor.py")
        + " "
        + os.path.normpath("../palemoon")
    )
    sys.exit("missing argument")


start_string = os.path.normpath(sys.argv[1])
target = pathlib.Path(start_string)

if not target.is_dir():
    output = process_file(start_string)
    print(output)
else:
    process_dir(start_string + os.sep, ".")
