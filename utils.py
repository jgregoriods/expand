import csv
import math
import os
import time
import numpy as np
import pyproj


# Base layers are in Albers Equal Area Conical for South America.
albers = pyproj.Proj("+proj=aea +lat_1=-5 +lat_2=-42 +lat_0=-32 +lon_0=-60 \
                     +x_0=0 +y_0=0 +ellps=aust_SA +towgs84=-57,1,-41,0,0,0,0 \
                     +units=m +no_defs")


def get_dates():
    dates = {}
    for filename in os.listdir('./dates/'):
        global x, y
        with open('./dates/{}'.format(filename)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    x, y = to_canvas(float(row[0]), float(row[1]))
                    dates[(x, y)] = {}
                else:
                    dates[(x, y)][int(row[0])] = float(row[1])
                line_count += 1
    return dates


def to_lonlat(coords):
    x, y = coords
    lon, lat = albers(x, y, inverse=True)
    return lon, lat


def transform_coords(coords):
    x, y = coords
    x_m = -2985163.8955 + (x * 10000)
    y_m = 5227968.786 - (y * 10000)
    return x_m, y_m


def to_canvas(x, y):
    x_canvas = int((albers(x, y)[0] + 2985163.8955) / 10000)
    y_canvas = int((5227968.786 - albers(x, y)[1]) / 10000)
    return x_canvas, y_canvas
