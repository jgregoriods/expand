from numpy import loadtxt
from village import Village
from utils import get_dates


class Model:
    def __init__(self, params):

        self.width = 638
        self.height = 825

        self.current_id = 0

        self.agents = {}
        self.grid = {}

        # Start at earliest date in the model
        self.bp = 4600

        # Model parameters
        self.params = params
        self.start_dates = [param[2] for param in self.params]

        # Layers to keep track of land ownership and dates of arrival
        # for each culture.
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x, y)] = {'owner': 0,
                                     'arrival_time': {'arawak': 0,
                                                      'carib': 0,
                                                      'tupi': 0,
                                                      'je': 0}}

        # Add layers with ecological niche of each culture.
        for param in params:
            breed_name = param[1]
            layer = loadtxt('./layers/{}.asc'.format(breed_name), skiprows=6)
            for y in range(self.height):
                for x in range(self.width):
                    self.grid[(x, y)][breed_name] = layer[y, x]
                    # Prevent water cells from being settled.
                    if layer[y, x] == -9999:
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
        for param in self.params:
            if param[2] == self.bp:
                village = Village(self.next_id(), self, *param)
                self.agents[village._id] = village

                # Make space for new village in case landscape is taken
                neighbors = village.get_neighbors(village.catchment)
                if neighbors:
                    for _id in neighbors:
                        self.agents[_id].abandon_land()
                        del self.agents[_id]

                village.claim_land(village.coords)

    def eval(self):
        """
        Returns a score from 0 to 1 of model fitness based on match
        with archaeological dates.
        """
        total_score = 0

        for param in self.params:
            breed_name = param[1]
            dates = get_dates(breed_name)
            score = 0

            for coords in dates:
                sim_date = self.grid[coords]['arrival_time'][breed_name]
                if sim_date and sim_date in dates[coords]:
                    # Normalize probability distribution
                    score += (dates[coords][sim_date] /
                              max(dates[coords].values()))

            total_score += score / len(dates)

        return total_score / 4

    def step(self):
        if self.bp in self.start_dates:
            self.setup_agents()
        agent_list = list(self.agents.keys())
        for _id in agent_list:
            self.agents[_id].step()
        self.bp -= 1
