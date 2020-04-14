from time import time
import numpy as np
from model import Model
from utils import to_canvas


# Coordinates of earliest sites
la_gruta = (-65.77, 7.82)
hato_calzada = (-70.45, 8)
pointe_maripa = (-52.33, 4.67)
corozal = (-65.697, 7.92)
bela_vista = (-48.5534, -5.1164)
talhada = (-48.2772, -13.9506)
gentio = (-46.8958, -16.3792)
abraham = (-50.5414, -5.8059)


def run_model(params):
    init_time = time()

    p = np.array(params).reshape((4, 5))

    arawak = list(p[0])
    arawak.insert(0, to_canvas(*la_gruta))
    arawak.insert(1, 'arawak')
    arawak.insert(2, 4553)

    carib = list(p[1])
    carib.insert(0, to_canvas(*corozal))
    carib.insert(1, 'carib')
    carib.insert(2, 1610)

    tupi = list(p[2])
    tupi.insert(0, to_canvas(*abraham))
    tupi.insert(1, 'tupi')
    tupi.insert(2, 2411)

    je = list(p[3])
    je.insert(0, to_canvas(*gentio))
    je.insert(1, 'je')
    je.insert(2, 3717)

    new_model = Model(params=[arawak, carib, tupi, je])

    for i in range(4053):
        new_model.step()
        # Abort if execution time is too long and assign
        # worst possible score to avoid passing to next
        # generation.
        if time() - init_time >= 3600:
            return -1

    result = new_model.eval()
    return result
