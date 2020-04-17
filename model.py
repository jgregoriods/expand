import numpy as np
from time import time

from utils import get_dates, to_lonlat, transform_coords
from village import Village


class Model:
    def __init__(self, start, params):

        # Dimensions of the asc layers
        self.width = 638
        self.height = 825

        self.agents = {}
        self.grid = {}

        # Start at earliest date in the model
        self.bp = start

        # Model parameters to be passed down to the village agents
        # as a dictionary. Initial coords, fission threshold, K*,
        # catchment, leap distance, permanence
        self.params = params

        # Layers to keep track of agents, land ownership and dates
        # of arrival
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)] = {'agent': 0,
                                     'owner': 0,
                                     'arrival_time': 0}

        # Add layers with ecological niche
        env = np.loadtxt('./layers/env.asc', skiprows=6)
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)]['env'] = env[y, x]
                # Prevent water cells from being settled
                if env[y, x] == -9999:
                    self.grid[(x, y)]['owner'] = -1

        self.setup_agents()

    def setup_agents(self):
        """
        Creates a village, adds land to its territory and records
        its start date.
        """
        village = Village(self, **self.params)
        self.agents[village._id] = village
        self.grid[village.coords]['agent'] = village._id
        village.claim_land(village.coords)
        village.record_date()

    def eval(self):
        """
        Returns a score from 0 to 1 of model fitness based on match
        with archaeological dates.
        """
        total_score = 0

        dates = get_dates()

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
        """
        Writes the simulated arrival times and scores of
        archaeological dates to csv files.
        """
        timestamp = int(time())
        sim_file = './results/sim{}.csv'.format(str(timestamp))

        with open(sim_file, 'w') as file:
            file.write('x,y,bp\n')
            for coords in self.grid:
                if self.grid[coords]['arrival_time']:
                    bp = self.grid[coords]['arrival_time']
                    x, y = to_lonlat(transform_coords(coords))
                    file.write(str(x) + ',' + str(y) + ',' + str(bp) + '\n')

        date_file = './results/dates{}.csv'.format(str(timestamp))
        dates = get_dates()

        with open(date_file, 'w') as file:
            file.write('x,y,score\n')
            for coords in dates:
                sim_date = self.grid[coords]['arrival_time']
                if sim_date in dates[coords]:
                    score = (dates[coords][sim_date] /
                             max(dates[coords].values()))
                else:
                    score = 0
                x, y = to_lonlat(transform_coords(coords))
                file.write(str(x) + ',' + str(y) + ',' + str(score) + '\n')

    def step(self):
        agent_list = list(self.agents.keys())
        for _id in agent_list:
            self.agents[_id].step()
        self.bp -= 1
