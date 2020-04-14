import numpy as np
from time import time
from village_un import Village
from utils import get_dates, to_lonlat, transform_coords
from NN import sigmoid, activation


class Model:
    def __init__(self, params):

        self.width = 638
        self.height = 825

        self.current_id = 0

        self.agents = {}
        self.grid = {}

        # Model parameters
        self.params = params
        self.nnpars = self.params[8:len(self.params)]
        """
        self.ele_beta = self.params[8]
        self.slo_beta = self.params[9]
        self.drivs_beta = self.params[10]
        self.npp_beta = self.params[11]
        self.sq_beta = self.params[12]
        self.ele_beta2 = self.params[13]
        self.slo_beta2 = self.params[14]
        self.drivs_beta2 = self.params[15]
        self.npp_beta2 = self.params[16]
        self.sq_beta2 = self.params[17]
        self.eleslo_beta = self.params[18]
        self.eledrivs_beta = self.params[19]
        self.elenpp_beta = self.params[20]
        self.elesq_beta = self.params[21]
        self.slodrivs_beta = self.params[22]
        self.slonpp_beta = self.params[23]
        self.slosq_beta = self.params[24]
        self.drivsnpp_beta = self.params[25]
        self.drivssq_beta = self.params[26]
        self.nppsq_beta = self.params[27]
        """
        # Start at earliest date in the model
        self.start_date = self.params[2]
        self.bp = self.start_date

        # Layers to keep track of land ownership and dates of arrival
        # for each culture.
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)] = {'owner': 0,
                                     'arrival_time': 0}

        """
        # Add layers with ecological niche of each culture.
        breed_name = self.params[1]
        layer = loadtxt('./layers/{}.asc'.format(breed_name), skiprows=6)
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)][breed_name] = layer[y, x]
                # Prevent water cells from being settled.
                if layer[y, x] == -9999:
                    self.grid[(x, y)]['owner'] = -1
        """

        ele_layer = np.loadtxt('./layers/eleNorm.asc', skiprows=6)
        slo_layer = np.loadtxt('./layers/sloNorm.asc', skiprows=6)
        drivs_layer = np.loadtxt('./layers/drivsNorm.asc', skiprows=6)
        npp_layer = np.loadtxt('./layers/nppNorm.asc', skiprows=6)
        sq_layer = np.loadtxt('./layers/sqNorm.asc', skiprows=6)

        breed_name = self.params[1]

        w = [np.array(self.nnpars[0:36]).reshape(6, 6),
             np.array(self.nnpars[37:len(self.nnpars)])]
        
        for y in range(self.height):
            for x in range(self.width):
                if (ele_layer[y, x] > -9999 and slo_layer[y, x] > -9999 and
                    drivs_layer[y, x] > -9999 and npp_layer[y, x] > -9999 and
                    sq_layer[y, x] > -9999):
                    """
                    suit = (
                        (ele_layer[y, x] * self.ele_beta) +
                        (slo_layer[y, x] * self.slo_beta) +
                        (drivs_layer[y, x] * self.drivs_beta) +
                        (npp_layer[y, x] * self.npp_beta) +
                        (sq_layer[y, x] * self.sq_beta) +
                        ((ele_layer[y, x] ** 2) * self.ele_beta2) +
                        ((slo_layer[y, x] ** 2) * self.slo_beta2) +
                        ((drivs_layer[y, x] ** 2) * self.drivs_beta2) +
                        ((npp_layer[y, x] ** 2) * self.npp_beta2) +
                        ((sq_layer[y, x] ** 2) * self.sq_beta2) +
                        (ele_layer[y, x] * slo_layer[y, x] * self.eleslo_beta) +
                        (ele_layer[y, x] * drivs_layer[y, x] * self.eledrivs_beta) +
                        (ele_layer[y, x] * npp_layer[y, x] * self.elenpp_beta) +
                        (ele_layer[y, x] * sq_layer[y, x] * self.elesq_beta) +
                        (slo_layer[y, x] * drivs_layer[y, x] * self.slodrivs_beta) +
                        (slo_layer[y, x] * npp_layer[y, x] * self.slonpp_beta) +
                        (slo_layer[y, x] * sq_layer[y, x] * self.slosq_beta) +
                        (drivs_layer[y, x] * npp_layer[y, x] * self.drivsnpp_beta) +
                        (drivs_layer[y, x] * sq_layer[y, x] * self.drivssq_beta) +
                        (npp_layer[y, x] * sq_layer[y, x] * self.nppsq_beta)
                    )
                    self.grid[(x, y)][breed_name] = 1 / (1 + 2.7182 ** (-suit))
                    """

                    suit = activation(w, np.array([ele_layer[y, x],
                                                  slo_layer[y, x],
                                                  drivs_layer[y, x],
                                                  npp_layer[y, x],
                                                  sq_layer[y, x]]))
                    self.grid[(x, y)][breed_name] = suit[len(suit) - 1]
                else:
                    self.grid[(x, y)][breed_name] = 0
                    self.grid[(x, y)]['owner'] = -1

        self.setup_agents()

    def next_id(self):
        """
        Generates continuous unique id values for agents.
        Start at 1.
        """
        self.current_id += 1
        return self.current_id

    def setup_agents(self):
        """
        Create a village for each culture, add land to their territory
        and record their start dates (not current year).
        """
        village = Village(self.next_id(), self, *self.params[:8])
        self.agents[village._id] = village
        village.claim_land(village.coords)

    def eval(self):
        """
        Returns a score from 0 to 1 of model fitness based on match
        with archaeological dates.
        """
        total_score = 0

        breed_name = self.params[1]
        dates = get_dates(breed_name)

        for coords in dates:
            score = 0
            sim_date = self.grid[coords]['arrival_time']
            if sim_date and sim_date in dates[coords]:
                # Normalize probability distribution
                score += (dates[coords][sim_date] /
                          max(dates[coords].values()))

            total_score += score

        return total_score / len(dates)

    def write(self):
        breed_name = self.params[1]
        timestamp = int(time())
        filename = './results/res{}.csv'.format(str(timestamp))
        with open(filename, 'w') as file:
            file.write('breed,x,y,bp\n')
            for coords in self.grid:
                if self.grid[coords][breed_name]:
                    bp = self.grid[coords][breed_name]
                    breed = self.params[1]
                    x, y = to_lonlat(transform_coords(coords))
                    file.write(str(breed) + ',' + str(x) + ',' + str(y) + ',' +
                               str(bp) + '\n')

    def step(self):
        agent_list = list(self.agents.keys())
        for _id in agent_list:
            self.agents[_id].step()
        self.bp -= 1
