from utils import to_canvas

# Coordinates of earliest sites
la_gruta = (-65.77, 7.82)
hato_calzada = (-70.45, 8)
pointe_maripa = (-52.33, 4.67)
corozal = (-65.697, 7.92)
bela_vista = (-48.5534, -5.1164)
talhada = (-48.2772, -13.9506)
gentio = (-46.8958, -16.3792)
corporito = (-61.81, 8.99)
abraham = (-50.5414, -5.8059)
sao_bento = (-53.1869, -3.5514)


arawak = [to_canvas(*la_gruta), 'arawak', 4553, 62, 126, 2, 20, 15, 0.222]

carib = [to_canvas(*corozal), 'carib', 1610, 80, 237, 3, 20, 16, 0.413]

tupi = [to_canvas(*sao_bento), 'tupi', 2787, 46, 227, 1, 15, 28, 0.411]

je = [to_canvas(*gentio), 'je', 3717, 50, 150, 2, 0, 10, 0.275]
