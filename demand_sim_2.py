import simpy
import building_objects as bo 
import numpy as np
from scipy.stats import poisson, norm
from tqdm import tqdm

class demand_generator():
    def __init__(self, env, neighborhood_size, microhub_location, building_size, building_classes, building_params, building_num_residents, building_distribution, package_dist):
        self.env = env
        self.neighborhood_size = neighborhood_size # Num buildings x num buildings
        self.microhub_location = microhub_location

        # Building Params
        self.building_size = 1/50 # 100 feet but in miles
        self.building_classes = building_classes # List of the buildings classes in the sim model
        self.building_params = building_params # List of dictionary parameter templates
        self.building_num_residents = building_num_residents # List of poisson RVs to simulate different number of residents per lot
        self.building_distribution = building_distribution # A list of floats with len(class-1) with the last class taking the rest

        # Package Params
        self.package_dist = package_dist # A poisson RV to simulate the number of packages that will be delivered to a household

        self._create_neighborhood()

    def _create_neighborhood(self):
        # Generate random locations based on density for each building
        neighborhood_size = self.neighborhood_size[0] * self.neighborhood_size[1]
        neighborhood_key = [np.repeat(i,int(j*neighborhood_size)) for i,j in zip(range(len(self.building_distribution)),self.building_distribution)]
        neighborhood_key.append(np.repeat(len(self.building_distribution), neighborhood_size-len(neighborhood_key)))
        neighborhood_key = np.concatenate(neighborhood_key)
        np.random.shuffle(neighborhood_key)

        # Create building objects for the neighborhood
        self.neighborhood = [None] * neighborhood_size
        for i in range(neighborhood_size):
            building_index = int(neighborhood_key[i])
            num_residents = self.building_num_residents[building_index].rvs()
            param_dict = self.building_params[building_index]
            self.neighborhood[i] = self.building_classes[building_index](**param_dict, env=self.env, num_residents=num_residents)

    def _create_route(self, n):
        # Random Starting Point
        current_loc = [np.random.randint(low=0, high=self.neighborhood_size[0]), np.random.randint(low=0, high=self.neighborhood_size[1])]
        locations = [None] * n
        buildings = [None] * n

        count_i = 0

        while count_i < n:
            num_packages = np.min([self.package_dist.rvs(), n-count_i])
            for _ in range(num_packages):
                locations[count_i] = [j*self.building_size for j in current_loc]
                buildings[count_i] = self.neighborhood[current_loc[0]*self.neighborhood_size[0] + current_loc[1]]

                count_i += 1
            # Stepping
            cl_index = int(np.random.randint(low=0, high=2))
            current_loc[cl_index] += np.random.choice([-1,1])

            # Check if outside bounds, if so reflect
            if current_loc[cl_index] >= self.neighborhood_size[cl_index]:
                current_loc[cl_index] = self.neighborhood_size[cl_index]-2
            elif current_loc[cl_index] < 0:
                current_loc[cl_index] = 1

        return locations, buildings

    def generate_demand(self, n):
        # Can add logic for multiple demands at once
        return self._create_route(n)

def main():
    env = simpy.Environment()
    neighborhood_size = [100,100] # Num buildings x num buildings
    microhub_location = [np.random.randint(0,100),np.random.randint(0,100)]

    # Building Params
    building_size = 1/50 # 100 feet but in miles
    building_classes = [bo.SingleFamily, bo.MultiStory] # List of the buildings classes in the sim model
    building_params = [{'deliver':norm(1/120,1/120),'name':'SingleFamily'},{'deliver':norm(1/60,1/120),'deliver_params':1/120, 'name':'MultiStory'}] # List of dictionary parameter templates
    building_num_residents = [poisson(1), poisson(100)] # List of poisson RVs to simulate different number of residents per lot
    building_distribution = [0.7] # A list of floats with len(class-1) with the last class taking the rest

    # Package Params
    package_dist = poisson(2) # A poisson RV to simulate the number of packages that will be delivered to a household

    sim_data = demand_generator(env=env, neighborhood_size=neighborhood_size, microhub_location=microhub_location, building_size=building_size, 
                                building_classes=building_classes, building_params=building_params, building_num_residents=building_num_residents, 
                                building_distribution=building_distribution, package_dist=package_dist)
    location, building = sim_data.generate_demand(300)
    print(location)
    print(len(location))
    

if __name__ == "__main__":
    main()