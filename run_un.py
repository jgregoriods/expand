from time import time
from model_mx import Model
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
corporito = (-61.81, 8.99)
saladero = (-62.2009, 8.6817)
sao_bento = (-53.1869, -3.5514)
go_cp_02 = (-51.5753, -16.9612)


def run_model(params):
    init_time = time()

    # p = np.array(params).reshape((4, 5))
    """
    arawak = params
    arawak.insert(0, to_canvas(*corporito))
    arawak.insert(1, 'arawak')
    arawak.insert(2, 5133)
    arawak.append(0.222)

    carib = params
    carib.insert(0, to_canvas(*saladero))
    carib.insert(1, 'carib')
    carib.insert(2, 1782)
    carib.append(0.413)

    """
    tupi = params
    tupi.insert(0, to_canvas(*abraham))
    tupi.insert(1, 'tupi')
    tupi.insert(2, 2411)
    tupi.append(0.442)

    """
    je = params
    je.insert(0, to_canvas(*gentio))
    je.insert(1, 'je')
    je.insert(2, 3513)
    je.append(0.275)
    """

    new_model = Model(params=tupi)

    for i in range(new_model.start_date - 500):
        new_model.step()
        # Abort if execution time is too long and assign
        # worst possible score to avoid passing to next
        # generation.
        if time() - init_time >= 600:
            return 0

    result = new_model.eval()
    return result
