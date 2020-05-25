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
    def __init__(self, env, num_agents, agent, base_params, package_dist, turnaround_time, turnaround_params):
        self.env = env

        # Agent params
        self.num_agents = simpy.Resource(env, num_agents)
        self.agent = agent # Agent object
        self.base_params = base_params

        # Num packages per agent tour params
        self.package_dist = package_dist

        # Turnaround time parameters
        self.turnaround_time = turnaround_time
        self.turnaround_params = turnaround_params # constant

        #Metrics
        self.throughput = 0
        self.distance = 0


    def process_deliveries(self, locations, buildings, **kwargs):
        '''
        Input:
            locations = list of location in sorted order 
            buildings = list of buildings in sorted order based on location
        '''
        # Process all deliveries till empty
        while len(locations) > 0:
            with self.num_agents.request() as request:
                # Process into correct format for simulation
                locations_list = []
                buildings_list = []
                num_packages_list = []

                num_packages_temp = np.min([self._num_packages(), len(locations)])

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

                # Update parameters and create delivery agent
                temp_param.update({'delivery_schedule':DeliverySchedule(locations_list, buildings_list, num_packages_list), 'env':self.env})
                delivery_agent = self.agent(**temp_param)
                yield self.env.process(delivery_agent.make_deliveries(self._update_metric, **kwargs))

                # Turnaround time to pack up new deliveries and return to delivering
                yield self.env.timeout(self._turnaround_time(num_packages_temp))

    def _num_packages(self):
        return self.package_dist.rvs()

    def _turnaround_time(self, num_packages):
        return num_packages * np.max([self.turnaround_time.rvs(),1/120]) + self.turnaround_params

    def _update_metric(self, metric, value):
        if metric == 'distance':
            self.distance += value
        elif metric == 'throughput':
            self.throughput += value

class Agent():
    def __init__(self, env, delivery_schedule, current_location, delivery_hub_location, speed):
        self.env = env
        self.delivery_schedule = delivery_schedule
        self.current_location = current_location
        self.delivery_hub_location = delivery_hub_location

        # Drive Parameters
        self.speed = speed

    def make_deliveries(self, metric_update_func, **kwargs):
        '''
        General Process: Drive to delivery site, call building object make delivery, repeat until no packages left
        '''
        # Deliver all carried packages
        for location, building, num_packages in self.delivery_schedule:
            yield self.env.process(self._drive(location, metric_update_func))
            yield self.env.process(self._park(building))
            yield self.env.process(self._deliver(num_packages, building, metric_update_func))

        # Go back and grab more deliveries
        self._drive(self.delivery_hub_location, metric_update_func, **kwargs)

    def _drive(self, location, metric_update_func, **kwargs):
        '''
        TODO: Create timeout for driving time based on drive distribution and speed
        '''
        distance = 0
        for i,j in zip(location, self.current_location):
            distance += np.abs(i-j)

        yield self.env.timeout(distance/self.speed)
        self.current_location = location
        if 'to_hub' not in kwargs:
            metric_update_func('distance', distance)

    def _park(self, building):
        '''
        TODO: Create timeout for parking time based on building type
        '''
        pass

    def _deliver(self, num_packages, building, metric_update_func):
        yield self.env.process(building.process_delivery(num_packages))
        metric_update_func('throughput', num_packages)

class Electric_Bike(Agent):
    def __init__(self, parking, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(np.max([self.parking.rvs(),1/360]))

class Courier_Van(Agent):
    def __init__(self, parking, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(np.max([self.parking[building.name].rvs(), 1/360]))

class Courier_Car(Agent):
    def __init__(self, parking, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(np.max([self.parking[building.name].rvs(), 1/360]))