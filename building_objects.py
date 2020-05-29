import simpy
import numpy as np

class Building():

    def __init__(self, env, num_residents):
        self.env = env
        self.num_residents = num_residents

    def process_delivery(self, num_packages):
        '''
        Generic Delivery Process: Make Delivery, Return to Vehicle
        '''
        yield self.env.process(self._deliver_packages(num_packages))

    def _deliver_packages(self, num_packages):
        pass

class SingleFamily(Building):
    '''
    Single Family or Townhouses
    '''
    def __init__(self, deliver, **kwargs):
        super().__init__(**kwargs)
        self.deliver = deliver
        self.name = "SingleFamily"

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(num_packages * np.max([self.deliver.rvs(),1/360]))

class MultiStory(Building):
    '''
    Condos or apartments that are multiple stories

    Init:
        deliver = random distribution that follows scipy api
        deliver_params = list(parameters for deliver distribution)

    '''
    def __init__(self, deliver, deliver_params, **kwargs):
        super().__init__(**kwargs)
        self.deliver = deliver
        self.deliver_params = deliver_params # Constant for number of residents delivery
        self.name = "MultiStory"

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(np.random.randint(low=1, high=num_packages)*self.deliver_params + num_packages * np.max([self.deliver.rvs(),1/360]))

# Other Buildings
class Apartment(Building):
    '''
<<<<<<< HEAD
    Duplex|Single|Townhouse|Triplex
=======
    single-family
    residential-small lot

    Init:
        deliver = random distribution that follows scipy api
        deliver_params = list(parameters for deliver distribution)

    '''
    def __init__(self, deliver, deliver_params, **kwargs):
        super().__init__(**kwargs)
        self.deliver = deliver
        self.deliver_params = deliver_params

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(np.max([self.deliver.rvs(*self.deliver_params), 1/360])*num_packages)

class Condo(Building):
    '''
<<<<<<< HEAD
    Condominium
=======
    multi-row townhouse

    Init:
        deliver = random distribution that follows scipy api
        deliver_params = list(parameters for deliver distribution, constant for delivering to multiple houses)

    '''
    def __init__(self, num_houses, deliver, deliver_params, **kwargs):
        super().__init__(**kwargs)
        self.deliver = deliver
        self.deliver_params = deliver_params

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(np.min(np.random.randint(low=1, high=self.num_residents)*self.deliver_params[-1], num_packages) + num_packages * self.deliver.rvs(*self.deliver_params[:-1]))

class ResidenceBuilding(Building):
    '''
    Apartment|4-Plex
    '''
    def __init__(self, num_floors, deliver, deliver_params, **kwargs):
        super().__init__(**kwargs)
        self.deliver = deliver
        self.deliver_params = deliver_params

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(num_packages * self.deliver.rvs(*self.deliver_params))

class PedestrianDesignated(Building):
    '''
    apartments
    condos

    with high density shopping underneath
    '''
    def __init__(self, num_floors, **kwargs):
        super().__init__(**kwargs)
        self.num_floors = num_floors

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(num_packages * self.deliver.rvs(*self.deliver_params))

