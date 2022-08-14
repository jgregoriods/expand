import numpy as np
import matplotlib.pyplot as plt

from time import time
from tqdm import tqdm

from utils import get_dates, to_lonlat, transform_coords, to_canvas
from village import Village


class Model:
    def __init__(self, start, params):
        
        with open('./layers/env.asc', 'r') as f:
            self.header = [next(f) for i in range(6)]

        # Dimensions of the asc layers
        self.width = int(self.header[0].split()[1])
        self.height = int(self.header[1].split()[1])

        self.nodata = int(self.header[-1].split()[1])
        self.img = np.full((self.height, self.width), self.nodata)

        self.agents = {}
        self.grid = {}

        # Start at earliest date in the model
        self.bp = start

        # Model parameters to be passed down to the village agents as a
        # dictionary. Initial coords, fission threshold, K*, catchment,
        # leap distance, permanence
        self.params = params

        self.xmin = float(self.header[2].split()[1])
        self.ymax = float(self.header[3].split()[1]) + self.height * int(self.header[4].split()[1])

        self.params['coords'] = to_canvas(params['coords'], self.xmin, self.ymax)
        self.params['catchment'] //= 10
        self.params['leap_distance'] //= 10

        # Layers to keep track of agents, land ownership and dates of arrival
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)] = {'agent': 0, 'owner': 0, 'arrival_time': 0}

        # Add layers with ecological niche
        env = np.loadtxt('./layers/env.asc', skiprows=6)
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)]['env'] = env[y, x]
                # Prevent water cells from being settled
                if env[y, x] == self.nodata:
                    self.grid[(x, y)]['owner'] = -1

        self.setup_agents()

    def setup_agents(self):
        """
        Creates a village, adds land to its territory and records its start date.
        """
        village = Village(self, **self.params)
        self.agents[village._id] = village
        self.grid[village.coords]['agent'] = village._id
        village.claim_land(village.coords)
        village.record_date()

    def eval(self):
        """
        Returns a score from 0 to 1 of model fitness based on match with
        archaeological dates.
        """
        total_score = 0

        dates = get_dates(self.xmin, self.ymax)

        for coords in dates:
            score = 0
            sim_date = self.grid[coords]['arrival_time']
            if sim_date and sim_date in dates[coords]:
                # Normalize probability distribution
                score += (dates[coords][sim_date] / max(dates[coords].values()))

            total_score += score

        return total_score / len(dates)

    def write(self):
        """
        Writes the simulated arrival times to an asc file and scores of
        archaeological dates to a csv file.
        """
        timestamp = int(time())

        np.savetxt(f'./results/sim{str(timestamp)}.asc',
                   self.img, header=''.join(self.header)[:-1], comments='')

        date_file = f'./results/dates{str(timestamp)}.csv'
        dates = get_dates(self.xmin, self.ymax)

        with open(date_file, 'w') as file:
            file.write('x,y,score\n')
            for coords in dates:
                sim_date = self.grid[coords]['arrival_time']
                if sim_date in dates[coords]:
                    score = (dates[coords][sim_date] / max(dates[coords].values()))
                else:
                    score = 0
                x, y = to_lonlat(transform_coords(coords, self.xmin, self.ymax))
                file.write(f'{str(x)},{str(y)},{str(score)}\n')

    def step(self):
        agent_list = list(self.agents.keys())
        for _id in agent_list:
            self.agents[_id].step()
        self.bp -= 1

    def plot(self):
        plt.rcParams['figure.dpi'] = 150
        img = self.img.copy().astype('float')
        img[img==self.nodata] = np.nan
        plt.imshow(img)
        plt.show()

    def run(self, num_iter, show_prog=False, plot=False):
        if show_prog:
            for i in tqdm(range(num_iter)):
                self.step()
        else:
            for i in range(num_iter):
                self.step()

        for (x,y) in self.grid:
            if self.grid[(x,y)]['arrival_time']:
                self.img[y,x] = self.grid[(x,y)]['arrival_time']

        if plot:
            self.plot()