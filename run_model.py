import simpy
import numpy as np
import demand_sim_2 as demand
import building_objects as bo
import deliver_agents as da
import json
from scipy.stats import poisson, norm

def main():
    env = simpy.Environment()
    np.random.seed(9999)

    #### DEMAND ####
    neighborhood_size = [100,100] # Num buildings x num buildings
    microhub_location = [np.random.randint(0,100),np.random.randint(0,100)]

    # Building Params
    building_size = 1/50 # 100 feet but in miles
    building_classes = [bo.SingleFamily, bo.MultiStory] # List of the buildings classes in the sim model
    building_params = [{'deliver':norm(1/120,1/120),'name':'SingleFamily'},{'deliver':norm(1/120,1/120),'deliver_params':1/120, 'name':'MultiStory'}] # List of dictionary parameter templates
    building_num_residents = [poisson(1), poisson(100)] # List of poisson RVs to simulate different number of residents per lot
    building_distribution = [0.7] # A list of floats with len(class-1) with the last class taking the rest

    # Package Params
    package_dist = poisson(2) # A poisson RV to simulate the number of packages that will be delivered to a household

    sim_data = demand.demand_generator(env=env, neighborhood_size=neighborhood_size, microhub_location=microhub_location, building_size=building_size, 
                                building_classes=building_classes, building_params=building_params, building_num_residents=building_num_residents, 
                                building_distribution=building_distribution, package_dist=package_dist)
    #### DEMAND ####

    #### AGENT POOLS ####
    microhub_miles = [microhub_location[0]*building_size, microhub_location[1]*building_size]
    base_params_eb = {
        'current_location': microhub_miles,
        'delivery_hub_location': microhub_miles,
        'speed': 10,
        'parking':norm(1/60,1/720)
        }

    base_params_van = {
        'current_location': [0,0],
        'delivery_hub_location': [0,20],
        'speed': 20,
        'parking':{'SingleFamily':norm(2/60,1/120), 'MultiStory':norm(5/60,1/60)}
        }

    base_params_veh = {
        'current_location': [0,0],
        'delivery_hub_location': [0,20],
        'speed': 20,
        'parking':{'SingleFamily':norm(2/60,1/120), 'MultiStory':norm(5/60,1/60)}
        }

    electric_bike_pool = da.AgentPool(env=env, num_agents=20, agent=da.Electric_Bike, package_dist=poisson(30), turnaround_time=norm(1/120,1/720), turnaround_params=1.0/12, base_params=base_params_eb)
    courier_van_pool = da.AgentPool(env=env, num_agents=2, agent=da.Courier_Van, package_dist=poisson(300), turnaround_time=norm(1/120,1/720),turnaround_params=1, base_params=base_params_van)
    courier_vehicle_pool = da.AgentPool(env=env, num_agents=10, agent=da.Courier_Car, package_dist=poisson(50), turnaround_time=norm(1/120,1/720),turnaround_params=1, base_params=base_params_veh)

    #### AGENT POOLS ####

    #### RUN SIM ####
    location, building = sim_data.generate_demand(1000)
    env.process(electric_bike_pool.process_deliveries(location, building))
    location, building = sim_data.generate_demand(1000)
    env.process(courier_van_pool.process_deliveries(location, building, to_hub=True))
    location, building = sim_data.generate_demand(1000)
    env.process(courier_vehicle_pool.process_deliveries(location, building, to_hub=True))

    env.run(until=8)

    #### RUN SIM ####

    #### CHECK METRICS ####
    print(microhub_location)
    print(electric_bike_pool.throughput, electric_bike_pool.distance)
    print(courier_van_pool.throughput, courier_van_pool.distance)
    print(courier_vehicle_pool.throughput, courier_vehicle_pool.distance)

if __name__ == "__main__":
    main()