from math import hypot


class Village:
    """
    Class used to represent a village agent in the model.
    """

    # Unique id for each village
    village_counter = 1

    # Memoized grid "masks" to speed up the calculation of neighborhoods and
    # destinations
    dist_mask = {}
    neighbor_mask = {}

    def __init__(self, model, coords, k, fission_threshold, catchment,
                 leap_distance, permanence, tolerance):

        self._id = Village.village_counter
        Village.village_counter += 1

        self.active = True

        # Basic settings
        self.model = model
        self.coords = coords

        # Demographic parameters
        self.r = 0.025
        self.k = k
        self.total_k = 0

        # Initialize village at max population before fission
        self.population = fission_threshold

        # Territory and movement parameters
        self.catchment = catchment
        self.fission_threshold = fission_threshold
        self.leap_distance = leap_distance

        # Start with no land
        self.land = []

        # Keep track of permanence
        self.permanence = permanence
        self.time_here = 0

        # Minimum env value acceptable for settling
        self.tolerance = tolerance

    def get_neighborhood(self, radius):
        """
        Returns all the cells within a given radius from the village.
        """
        if radius not in Village.neighbor_mask:
            Village.neighbor_mask[radius] = [(i, j) for i in range(-radius, radius + 1)
                                             for j in range(-radius, radius + 1)
                                             if self.get_distance((self.coords[0] + i,
                                                                   self.coords[1] + j)) <= radius]

        neighborhood = {(self.coords[0] + cell[0], self.coords[1] + cell[1]):
                         self.model.grid[(self.coords[0] + cell[0],
                                          self.coords[1] + cell[1])]
                         for cell in Village.neighbor_mask[radius]
                         if (self.coords[0] + cell[0],
                             self.coords[1] + cell[1]) in self.model.grid}
        return neighborhood

    def get_neighbors(self, radius):
        """
        Returns the ids of all other villages within a given radius of the village.
        """
        neighbors = []
        neighborhood = self.get_neighborhood(radius)
        for cell in neighborhood:
            if (neighborhood[cell]['agent'] and
                    neighborhood[cell]['agent'] != self._id):
                neighbors.append(neighborhood[cell]['agent'])
        return neighbors

    def get_destinations(self, distance):
        """
        Returns all the cells that are at a given distance from the village.
        """
        if distance not in Village.dist_mask:
            Village.dist_mask[distance] = [(i, j) for i in range(-distance, distance + 1)
                                           for j in range(-distance, distance + 1)
                                           if self.get_distance((self.coords[0] + i,
                                                                 self.coords[1] + j)) == distance]

        destinations = {(self.coords[0] + cell[0], self.coords[1] + cell[1]):
                         self.model.grid[(self.coords[0] + cell[0],
                                          self.coords[1] + cell[1])]
                         for cell in Village.dist_mask[distance]
                         if (self.coords[0] + cell[0],
                             self.coords[1] + cell[1]) in self.model.grid}
        return destinations

    def get_empty_destinations(self, distance, pioneer=False):
        """
        Returns all cells at a given distance that are not owned. If in pioneer
        mode, restricts the search to cells that have never been claimed.
        """
        destinations = self.get_destinations(distance)
        if pioneer:
            available_destinations = {cell: destinations[cell]['env']
                                      for cell in destinations
                                      if not destinations[cell]['owner'] and
                                      (destinations[cell]['env'] >=
                                       self.tolerance) and
                                      not destinations[cell]['arrival_time']}
        else:
            available_destinations = {cell: destinations[cell]['env']
                                      for cell in destinations
                                      if not destinations[cell]['owner'] and
                                      (destinations[cell]['env'] >=
                                       self.tolerance)}
        return available_destinations

    def get_distance(self, next_coords):
        """
        Returns the distance (in cells) from the village to a pair of coordinates.
        """
        x, y = self.coords
        next_x, next_y = next_coords
        return round(hypot((next_x - x), (next_y - y)))

    def grow(self):
        """
        Population grows exponentially. Update land is called to add new cells
        in case population is above K.
        """
        self.population += round(self.r * self.population)
        self.update_land()

    def update_land(self):
        """
        Calculates total K* from all cells owned by the village. In case
        population exceeds total K*, tries to add new cells. If population is
        still beyond K* after adding all available cells, population is reduced
        back to total K* and the village becomes inactive.
        """
        while self.population > self.total_k:
            # Cells within catchment that are not owned
            territory = self.get_neighborhood(self.catchment)
            free_land = {cell: territory[cell]['env']
                         for cell in territory if not territory[cell]['owner']
                         and territory[cell]['env'] >= self.tolerance}

            if free_land:
                # Choose cell with highest suitability
                new_land = max(free_land, key=free_land.get)
                self.claim_land(new_land)

            else:
                self.population = self.total_k
                self.active = False

    def claim_land(self, coords):
        """
        Claims a cell for the village and updates total K*.
        """
        self.model.grid[coords]['owner'] = self._id
        self.land.append(coords)
        self.total_k = self.k * len(self.land)

    def record_date(self):
        """
        Records the simulated date of arrival.
        """
        neighborhood = self.get_neighborhood(self.catchment)
        for cell in neighborhood:
            if not self.model.grid[cell]['arrival_time']:
                self.model.grid[cell]['arrival_time'] = self.model.bp

    def check_fission(self):
        """
        If population is above fission threshold and there are available cells
        outside its catchment, the village fissions and the daughter village
        moves away. If there are no empty cells but leapfrogging is allowed,
        another search is performed for leap distance.
        """
        if self.population >= self.fission_threshold:
            empty_land = self.get_empty_destinations(self.catchment * 2)
            neighbors = self.get_neighbors(self.catchment * 2)
            if empty_land and len(neighbors) < 6:
                new_village = self.fission()
                self.model.agents[new_village._id] = new_village
                new_village.move(empty_land)

            elif self.leap_distance:
                distant_land = self.get_empty_destinations(self.leap_distance,
                                                           pioneer=True)

                # Only perform leapfrogging if attractiveness of the destination
                # is higher than current cell
                if (distant_land and max(distant_land.values()) >
                        self.model.grid[self.coords]['env']):
                    new_village = self.fission()
                    self.model.agents[new_village._id] = new_village
                    new_village.move(distant_land)

    def fission(self):
        """
        A new village is created with the same attributes as the parent village
        and half its population.
        """
        new_village = Village(self.model, self.coords, self.k,
                              self.fission_threshold, self.catchment,
                              self.leap_distance, self.permanence,
                              self.tolerance)
        self.population //= 2
        new_village.population = self.population
        return new_village

    def move(self, neighborhood):
        """
        Moves the village to the cell with highest suitability in a given
        neighborhood. After moving, the village claims cells according to the
        population size.
        """
        new_home = max(neighborhood, key=neighborhood.get)
        if self.model.grid[self.coords]['agent'] == self._id:
            self.model.grid[self.coords]['agent'] = 0
        self.coords = new_home
        self.model.grid[new_home]['agent'] = self._id
        self.record_date()
        self.claim_land(new_home)
        self.update_land()

    def abandon_land(self):
        """
        Release ownership of cells.
        """
        for cell in self.land:
            self.model.grid[cell]['owner'] = 0
        self.land = []

    def check_move(self):
        """
        If settled beyond maximum permanence time in a given location, the
        village searches for available cells beyond its catchment to move. If
        no cells are available but leapfrogging is allowed, another search is
        performed for leap distance.
        """
        if self.time_here >= self.permanence:
            empty_land = self.get_empty_destinations(self.catchment * 2)

            if empty_land:
                self.abandon_land()
                self.move(empty_land)
                self.time_here = 0

            else:
                # self.active = False
                self.time_here += 1

        else:
            self.time_here += 1

    def step(self):
        if self.active:
            self.grow()
            self.check_fission()
            self.check_move()
