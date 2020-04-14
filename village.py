from math import hypot


class Village:
    """
    Class used to represent a village in the model.
    """

    village_counter = 1

    def __init__(self, model, coords, k,
                 fission_threshold, catchment, leap_distance, permanence,
                 tolerance):

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

        # Initialize village at saturation point
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

        self.tolerance = tolerance

    def get_neighborhood(self, radius):
        """
        Returns all the cells within a given radius from the
        village.
        """
        neighborhood = {(x, y): self.model.grid[(x, y)]
                        for x in range(self.coords[0] - radius,
                                       self.coords[0] + radius + 1)
                        for y in range(self.coords[1] - radius,
                                       self.coords[1] + radius + 1)
                        if (self.get_distance((x, y)) <= radius and
                            x >= 0 and y >= 0)}
        return neighborhood

    def get_neighbors(self, radius):
        """
        Returns the ids of all other villages within a given
        radius of the village.
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
        Returns all the cells that are at a given distance from the
        village.
        """
        destinations = {(x, y): self.model.grid[(x, y)]
                        for x in range(self.coords[0] - distance,
                                       self.coords[0] + distance + 1)
                        for y in range(self.coords[1] - distance,
                                       self.coords[1] + distance + 1)
                        if (self.get_distance((x, y)) == distance and
                            x >= 0 and y >= 0)}
        return destinations

    def get_empty_destinations(self, distance, pioneer=False):
        """
        Returns all cells at a given distance that are not owned.
        If in pioneer mode, restricts the search to cells that have
        never been claimed.
        """
        destinations = self.get_destinations(distance)
        if pioneer:
            available_destinations = {cell: destinations[cell]['env']
                                      for cell in destinations
                                      if not destinations[cell]['owner']
                                      and (destinations[cell]['env'] >=
                                           self.tolerance) 
                                      and not destinations[cell]['arrival_time']}
        else:
            available_destinations = {cell: destinations[cell]['env']
                                      for cell in destinations
                                      if not destinations[cell]['owner']
                                      and (destinations[cell]['env'] >=
                                           self.tolerance)}
        return available_destinations

    def get_distance(self, next_coords):
        """
        Returns the distance (in cells) from the village to a pair of
        coordinates.
        """
        x, y = self.coords
        next_x, next_y = next_coords
        return round(hypot((next_x - x), (next_y - y)))

    def grow(self):
        """
        Population grows exponentially. Update land is called to add
        new cells in case population is above K.
        """
        self.population += round(self.r * self.population)
        self.update_land()

    def update_land(self):
        """
        Calculates total K from all cells owned by the village. In case
        population exceeds total K, tries to add new cells. If
        population is still beyond K after adding all available cells,
        population is reduced back to total K and the village becomes
        inactive.
        """
        while self.population > self.total_k:
            # Cells within catchment that are not owned.
            territory = self.get_neighborhood(self.catchment)
            free_land = {cell: territory[cell]['env']
                         for cell in territory if not territory[cell]['owner']
                         and territory[cell]['env'] >= self.tolerance}

            if free_land:
                # Choose cell with highest suitability.
                new_land = max(free_land, key=free_land.get)
                self.claim_land(new_land)

            else:
                self.population = self.total_k
                self.active = False

    def claim_land(self, coords):
        """
        Claims a cell for the village, updates total carrying capacity
        and records the simulated date.
        """

        self.model.grid[coords]['owner'] = self._id
        self.land.append(coords)
        self.total_k = self.k * len(self.land)

    def record_date(self):
        neighborhood = self.get_neighborhood(self.catchment)
        for cell in neighborhood:
            if not self.model.grid[cell]['arrival_time']:
                self.model.grid[cell]['arrival_time'] = self.model.bp

    def check_fission(self):
        """
        If population is above fission threshold and there are
        available cells outside its catchment, the village fissions and
        the daughter village moves away. If there are no empty cells
        but leapfrogging is allowed, another search is performed for
        leap distance. If there is no possibility of moving, the
        village becomes inactive.
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

                # Only perform leapfrogging if attractiveness of the
                # destination is higher than current cell.
                if (distant_land and max(distant_land.values()) >
                        self.model.grid[self.coords]['env']):
                    new_village = self.fission()
                    self.model.agents[new_village._id] = new_village
                    new_village.move(distant_land)

    def fission(self):
        """
        A new village is created with the same attributes as the parent
        village and half its population.
        """
        new_village = Village(self.model, self.coords,
                              self.k,
                              self.fission_threshold, self.catchment,
                              self.leap_distance, self.permanence,
                              self.tolerance)
        self.population //= 2
        new_village.population = self.population
        return new_village

    def move(self, neighborhood):
        """
        Moves the village to the cell with highest suitability in a
        given neighborhood. After moving, the village claims cells
        according to the population size.
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
        If settled beyond maximum permanence time in a given location,
        the village searches for available cells beyond its catchment
        to move. If no cells are available but leapfrogging is allowed,
        another search is performed for leap distance. When there is no
        possibility of moving, the village becomes inactive.
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
