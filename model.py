import numpy as np
from time import time
from village import Village
from utils import get_dates, to_lonlat, transform_coords


class Model:
    def __init__(self, start, params):

        self.width = 638
        self.height = 825

        self.current_id = 0

        self.agents = {}
        self.grid = {}

        # Start at earliest date in the model
        self.bp = start

        # Model parameters
        self.params = params

        # Layers to keep track of agents, land ownership and dates
        # of arrival for each culture.
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)] = {'agent': 0,
                                     'owner': 0,
                                     'arrival_time': 0}

        # Add layers with ecological niche of each culture.
        layer = np.loadtxt('./layers/arawak.asc', skiprows=6)
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)]['env'] = layer[y, x]
                # Prevent water cells from being settled.
                if layer[y, x] == -9999:
                    self.grid[(x, y)]['owner'] = -1

        self.setup_agents()

    def setup_agents(self):
        """
        Create a village for each culture, add land to their territory
        and record their start dates (not current year).
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
        timestamp = int(time())
        filename = './results/res{}.csv'.format(str(timestamp))
        breed = self.params[1]
        with open(filename, 'w') as file:
            file.write('breed,x,y,bp\n')
            for coords in self.grid:
                if self.grid[coords]['arrival_time']:
                    bp = self.grid[coords]['arrival_time']
                    x, y = to_lonlat(transform_coords(coords))
                    file.write(str(breed) + ',' + str(x) + ',' + str(y) + ',' +
                               str(bp) + '\n')

    def step(self):
        agent_list = list(self.agents.keys())
        for _id in agent_list:
            self.agents[_id].step()
        self.bp -= 1
