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
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _deliver_packages(self, num_packages):
        pass

class LowRise(Building):
    '''
    multi-row townhouse
    '''
    def __init__(self, num_houses, **kwargs):
        super().__init__(**kwargs)
        self.num_houses = num_houses

    def _deliver_packages(self, num_packages):
        pass

class NeighborhoodCommercial(Building):
    '''
    apartments
    condos
    '''
    def __init__(self, num_floors, **kwargs):
        super().__init__(**kwargs)
        self.num_floors = num_floors

    def _deliver_packages(self, num_packages):
        pass

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
        pass
