import simpy
import numpy as np

class DeliverySchedule():
    def __init__(self, locations, buildings):
        '''
            Assumption the locations are in order of delivery route
        '''
        self.locations = []
        self.buildings = []
        self.num_packages = []
        self._convert(locations, buildings)

        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= len(self.locations):
            raise StopIteration
        else:
            self.current_index += 1
            return self.locations[self.current_index-1], self.buildings[self.current_index-1], self.num_packages[self.current_index-1]

    def _convert(self, locations,buildings):
        for i,j in zip(locations, buildings):
            if len(self.locations) == 0:
                self.locations.append(i)
                self.buildings.append(j)
                self.num_packages.append(1)
            else:
                if self.locations[-1] == i:
                    self.num_packages[-1] += 1
                else:
                    self.locations.append(i)
                    self.buildings.append(j)
                    self.num_packages.append(1)

class AgentPool():
    '''
    Creates a pool of delivery agents to mimic a finite resource
    '''
    def __init__(self, env, num_agents, turnaround_time, turnaround_params):
        self.env = env

        # Agent params
        self.num_agents = simpy.Resource(env, num_agents)

        # Turnaround time parameters
        self.turnaround_time = turnaround_time
        self.turnaround_params = turnaround_params # constant

        #Metrics
        self.throughput = 0
        self.distance = 0
        self.stops = 0
        self.routes = 0


    def process_deliveries(self, agent, num_packages, **kwargs):
        '''
        Input:
            locations = list of location in sorted order 
            buildings = list of buildings in sorted order based on location
        '''

        with self.num_agents.request() as request:
            # Wait till a deliverh agent is available
            yield request

            # Turnaround time to pack up deliveries and return to delivering
            yield self.env.timeout(self._turnaround_time(num_packages))

            yield self.env.process(agent.make_deliveries(self._update_metric, **kwargs))

    def _turnaround_time(self, num_packages):
        return num_packages * np.max([self.turnaround_time.rvs(),1/360]) + self.turnaround_params

    def _update_metric(self, metric, value):
        if metric == 'distance':
            self.distance += value
        elif metric == 'throughput':
            self.throughput += value
        elif metric == 'routes':
            self.routes += value
        else:
            self.stops += value

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
        metric_update_func('routes', 1)
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
        metric_update_func('throughput', num_packages)
        metric_update_func('stops', 1)
        yield self.env.process(building.process_delivery(num_packages))

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
        else:
            distance = 0
            for i,j in zip([0,0], self.current_location):
                distance += np.abs(i-j)
            self.current_location = [0,0]
            yield self.env.timeout(distance/self.speed)

class Courier_Car(Agent):
    def __init__(self, parking, **kwargs):
        super().__init__(**kwargs)
        self.parking = parking

    def _park(self, building):
        '''
        TODO: 1. Call 'yield env.timeout()' on parking
        '''
        yield self.env.timeout(np.max([self.parking[building.name].rvs(), 1/360]))

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
        else:
            distance = 0
            for i,j in zip([0,0], self.current_location):
                distance += np.abs(i-j)
            self.current_location = [0,0]
            yield self.env.timeout(distance/self.speed)