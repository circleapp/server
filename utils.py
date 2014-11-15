# -*- coding: utf-8 -*-
import re


def valid_coords(latitude, longitude):
    regexp = r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'
    compiler = re.compile(regexp)
    coord = "%s,%s" % (latitude, longitude)

    if compiler.match(coord):
        return True
    else:
        return False
