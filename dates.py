import os
import csv

from utils import to_canvas


def write_dates(name):
    dates = {}
    for filename in os.listdir(name):
        global x, y
        new_dates = {}
        with open('./{}/{}'.format(name, filename)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 1:
                    x, y = to_canvas(float(row[1]), float(row[2]))
                    new_dates[(x, y)] = {}
                elif line_count > 1:
                    new_dates[(x, y)][int(row[1])] = float(row[2])
                line_count += 1
            dates.update(new_dates)
    return dates
