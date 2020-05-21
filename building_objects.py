import simpy

class Buidling():

    def __init__(self, env, num_residents):
        self.env = env
        self.num_residents = num_residents

    def process_delivery(self, num_packages):
        '''
        Generic Delivery Process: Make Delivery, Return to Vehicle
        '''
        pass
