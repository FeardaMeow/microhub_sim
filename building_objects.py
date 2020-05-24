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
        self._deliver_packages(num_packages)

    def _deliver_packages(self, num_packages):
        pass

class Apartment(Building):
    '''
    Duplex|Single|Townhouse|Triplex
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _deliver_packages(self, num_packages):
        pass

class Condo(Building):
    '''
    Condominium
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _deliver_packages(self, num_packages):
        pass

class ResidenceBuilding(Building):
    '''
    Apartment|4-Plex
    '''
    def __init__(self, num_floors, **kwargs):
        super().__init__(**kwargs)
        self.num_floors = num_floors

    def _deliver_packages(self, num_packages):
        pass

