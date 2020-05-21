import simpy

class DeliverySchedule():
    def __init__(self, locations, buildings, num_packages):
        self.locations = locations
        self.buildings = buildings
        self.num_packages  = num_packages

        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= len(self.locations):
            raise StopIteration
        else:
            self.current_index += 1
            return self.locations[self.current_index-1], self.buildings[self.current_index-1], self.num_packages[self.current_index-1]

class AgentPool():
    '''
    Creates a pool of delivery agents to mimic a finite resource
    '''
    def __init__(self, env, num_agents):
        self.env = env
        self.num_agents = simpy.Resource(env, num_agents)

class Agent():

    def __init__(self, env, delivery_schedule, current_location, delivery_hub_location):
        self.env = env
        self.delivery_schedule = delivery_schedule
        self.current_location = current_location
        self.delivery_hub_location = delivery_hub_location
        pass

    def make_deliveries(self):
        '''
        General Process: Drive to delivery site, call building object make delivery, repeat until no packages left
        '''
        # Deliver all carried packages
        for location, building, num_packages in self.delivery_schedule:
            self._drive(location)
            self._park(building)
            self._deliver(num_packages, building)

        # Go back and grab more deliveries
        self._drive(self.delivery_hub_location)
                

    def _drive(self, location):
        '''
        TODO: Create timeout for driving time based on drive distribution and speed
        '''
        pass

    def _park(self, building):
        '''
        TODO: Create timeout for parking time based on building type
        '''
        pass

    def _deliver(self, num_packages, building):
        '''
        TODO: Create timeout for package delivery time based on num_packages and building type
        '''
        pass