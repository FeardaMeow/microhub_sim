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
    def __init__(self, env, num_agents, agent, base_params, package_dist, package_params, turnaround_time, turnaround_params):
        self.env = env

        # Agent params
        self.num_agents = simpy.Resource(env, num_agents)
        self.agent = agent
        self.base_params = base_params

        # Num packages per agent tour params
        self.package_dist = package_dist
        self.package_params = package_params

        # Turnaround time parameters
        self.turnaround_time = turnaround_time
        self.turnaround_params = turnaround_params # List

    def process_deliveries(self, locations, buildings):
        '''
        Input:
            locations = list of location in sorted order 
            buildings = list of buildings in sorted order based on location
        '''
        # Process all deliveries till empty
        while len(locations) > 0:
            with self.num_agents.request() as request:
<<<<<<< HEAD
                # Wait till a deliverh agent is available
                yield request
                temp_param = self.base_params

                # Process into correct format for simulation
=======
                # Process into correcty format for simulation
>>>>>>> 8111f70e40e84247341667ed416a9b0b0652bbc8
                locations_list = []
                buildings_list = []
                num_packages_list = []

                num_packages_temp = np.min(self._num_packages(), len(locations))

                for i in range(num_packages_temp):
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

                # Wait till a deliverh agent is available
                yield request
                temp_param = self.base_params
                
                # Turnaround time to pack up new deliveries and return to delivering
                yield self.env.timeout(self._turnaround_time(num_packages_temp))

                # Update parameters and create delivery agent
                temp_param.update({'delivery_schedule':DeliverySchedule(locations_list, buildings_list, num_packages_list), 'env':self.env})
                delivery_agent = self.agent(**temp_param)
                self.env.process(delivery_agent.make_deliveries())

    def _num_packages(self):
        return self.package_dist.rvs(*self.package_params)

    def _turnaround_time(self, num_packages):
        return num_packages * self.turnaround_time.rvs(*self.turnaround_params[:-1]) + self.turnaround_params[-1]

class Agent():
    def __init__(self, env, delivery_schedule, current_location, delivery_hub_location, speed, speed_params, parking, parking_params):
        self.env = env
        self.delivery_schedule = delivery_schedule
        self.current_location = current_location
        self.delivery_hub_location = delivery_hub_location

        # Drive Parameters
        self.speed = speed
        self.speed_params = speed_params

        # Performance metrics
        self.distance = 0

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
        distance = 0
        for i,j in zip(location, self.current_location):
            distance += np.abs(i-j)

        self.distance += distance
        yield self.env.timeout(distance/self.speed.rvs(*self.speed_params))

    def _park(self, building):
        '''
        TODO: Create timeout for parking time based on building type
        '''
        pass

    def _deliver(self, num_packages, building):
        building.process_delivery(num_packages)

class Electric_Bike(Agent):
    def __init__(self, parking, parking_params, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking
        self.parking_params = parking_params

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(self.parking.rvs(*self.parking_params))

class Courier_Van(Agent):
    def __init__(self, parking, parking_params, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking
        self.parking_params = parking_params

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(self.parking[building.name].rvs(*self.parking_params[building.name]))

class Courier_Car(Agent):
    def __init__(self, parking, parking_params, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking
        self.parking_params = parking_params

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(self.parking[building.name].rvs(*self.parking_params[building.name]))