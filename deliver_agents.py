import simpy
import numpy as np

class DeliverySchedule():
    def __init__(self, locations, buildings, num_packages):
        '''
            Assumption the locations are in order of delivery route
        '''
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
    def __init__(self, env, num_agents, agent, base_params, package_dist, package_params):
        self.env = env
        self.num_agents = simpy.Resource(env, num_agents)
        self.agent = agent
        self.base_params = base_params
        self.package_dist = package_dist
        self.package_params = package_params

    def process_deliveries(self, locations, buildings):
        '''
        Input:
            locations = list of location in sorted order 
            buildings = list of buildings in sorted order based on location
        '''
        # Process all deliveries till empty
        while len(locations) > 0:
            with self.num_agents.request() as request:
                # Wait till a deliverh agent is available
                yield request
                temp_param = self.base_params

                # Process into correct format for simulation
                locations_list = []
                buildings_list = []
                num_packages_list = []
                for i in range(np.min(self._num_packages(), len(locations))):
                    loc_i = locations.pop(0)
                    building_i = buildings.pop(0)
                    if i == 0:
                        locations_list.append(loc_i)
                        buildings_list.append(building_i)
                        num_packages_list.append(1)
                    else:
                        if locations_list[-1] == loc_i:
                            num_packages_list[-1] += 1
                        else:
                            locations_list.append(loc_i)
                            buildings_list.append(building_i)
                            num_packages_list.append(1)

                # Update parameters and create delivery agent
                temp_param.update({'delivery_schedule':DeliverySchedule(locations_list, buildings_list, num_packages_list), 'env':self.env})
                delivery_agent = self.agent(**temp_param)
                self.env.process(delivery_agent.make_deliveries())

    def _num_packages(self):
        return self.package_dist.rvs(*self.package_params)

                

class Agent():
    def __init__(self, env, delivery_schedule, current_location, delivery_hub_location, speed, parking_time):
        self.env = env
        self.delivery_schedule = delivery_schedule
        self.current_location = current_location
        self.delivery_hub_location = delivery_hub_location

        # Drive Parameters
        self.speed = speed

        # Parking Parameters
        self.parking_time = parking_time

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
        building.park()

    def _deliver(self, num_packages, building):
        '''
        TODO: Create timeout for package delivery time based on num_packages and building type
        '''
        building.process_delivery(num_packages)

class Electric_Bike(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        pass

    def _drive(self, location):
        '''
        TODO: 1. Call 'yield env.timeout()'
        TODO: 2. Update self.current_location = delivery location
        '''
        pass