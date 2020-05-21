import simpy

class Agent():

    def __init__(self, delivery_schedule):
        self.delivery_schedule = delivery_schedule
        pass

    def make_deliveries(self):
        '''
        General Process: Drive to delivery site, call building object make delivery, repeat until no packages left
        '''
        pass

    def _drive(self):
        pass

    def _park(self):
        pass