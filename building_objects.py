import simpy
import numpy as np

class Building():

    def __init__(self, env, num_residents, name):
        self.env = env
        self.num_residents = num_residents
        self.name = name

    def process_delivery(self, num_packages):
        '''
        Generic Delivery Process: Make Delivery, Return to Vehicle
        '''
        self._deliver_packages(num_packages)

    def _deliver_packages(self, num_packages):
        pass

class SingleFamily(Building):
    '''
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
        yield self.env.timeout(self.deliver.rvs(*self.deliver_params)*num_packages)

class LowRise(Building):
    '''
    multi-row townhouse

    Init:
        deliver = random distribution that follows scipy api
        deliver_params = list(parameters for deliver distribution, constant for delivering to multiple houses)
    '''
    def __init__(self, num_houses, deliver, deliver_params, **kwargs):
        super().__init__(**kwargs)
        self.num_houses = num_houses
        self.deliver = deliver
        self.deliver_params = deliver_params

    def _deliver_packages(self, num_packages):
        yield self.env.timeout(np.min(np.random.randint(low=1, high=self.num_houses)*self.deliver_params[-1], num_packages) + num_packages * self.deliver.rvs(*self.deliver_params[:-1]))

class NeighborhoodCommercial(Building):
    '''
    apartments
    condos
    '''
    def __init__(self, num_floors, **kwargs):
        super().__init__(**kwargs)
        self.num_floors = num_floors

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
