import simpy

class Building():

    def __init__(self, env, num_residents):
        self.env = env
        self.num_residents = num_residents

    def process_delivery(self, num_packages, **kwargs):
        '''
        Generic Delivery Process: Make Delivery, Return to Vehicle
        '''
        self._deliver_packages(num_packages, **kwargs)

    def _deliver_packages(self, num_packages,**kwargs):
        pass
