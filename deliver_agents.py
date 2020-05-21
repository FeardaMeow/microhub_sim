import simpy

class DeliverySchedule():
    def __init__(self):
        pass

class AgentPool():
    '''
    Creates a pool of delivery agents to mimic a finite resource
    '''
    def __init__(self, env, num_agents):
        self.env = env
        self.num_agents = simpy.Resource(env, num_machines)

class Agent():

    def __init__(self, env, delivery_schedule):
        self.env = env
        self.delivery_schedule = delivery_schedule
        pass

    def make_deliveries(self):
        '''
        General Process: Drive to delivery site, call building object make delivery, repeat until no packages left
        '''
        # Deliver packages till shift ends
        while True:
            # Deliver all carried packages
            for i in self.delivery_schedule:
                pass

    def _drive(self):
        pass

    def _park(self):
        pass