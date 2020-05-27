import simpy
import pandas as pd
import numpy as np
import demand_sim_2 as demand
import building_objects as bo
import deliver_agents as da
import json
from scipy.stats import poisson, norm
import os
from tqdm import tqdm

# Initialize Variables
microhub_miles = 0

def model_runner(param_folder, output_folder, seed):
    np.random.seed(seed)
    
    files = [d for d in os.listdir(param_folder) if d.endswith('.json')]
    outer = tqdm(total=len(files), desc='Paramater Files', position=0)

    # shows only the description
    param_log = tqdm(total=0, position=1, bar_format='{desc}')


    for f_name in files:
        with open(os.path.join(param_folder,f_name), "rb") as f:
            ### LOOP BELOW HERE FOR MULTIPLE SIM RUNS ###
            # Load model parameters
            model_params = json.load(f)
        
        # Convert model params to proper types
        model_params = parse_json(model_params)

        microhub_miles = [model_params['demand']['microhub_location'][0]*model_params['demand']['building_size'],model_params['demand']['microhub_location'][1]*model_params['demand']['building_size']]
        model_params['sim']['agent_gen']['agent_params'][0].update({"current_location":microhub_miles,"delivery_hub_location":microhub_miles})

        # Create dataframe to store performance metrics and pre-allocate memory
        df_sim_data = pd.DataFrame(index=[f_name.split('.')[0]]*model_params["sim"]["num_runs"], columns=['run_num', 
                                            'eb_throughput', 'eb_miles','eb_stops','eb_routes','eb_num_agents',
                                            'van_throughput', 'van_miles', 'van_stops','van_routes','van_num_agents',
                                            'car_throughput', 'car_miles','car_stops','car_routes','car_num_agents'])
        #print("Simulation Experiment " + f_name.split('.')[0], end='\r')
        inner = tqdm(total=model_params["sim"]["num_runs"], desc='Sim Runs', position=2)
        param_log.set_description_str(f'Current parameter file: {f_name}')
        for sim_run_i in range(model_params["sim"]["num_runs"]):
            # Create model
            env = simpy.Environment()
            
            # Create sim data generator
            sim_data = demand.demand_generator(env=env, **model_params['demand'])

        
            # Create agent pools
            electric_bike_pool = da.AgentPool(env=env, **model_params['agentpool']['electric_bike'])
            courier_van_pool = da.AgentPool(env=env, **model_params['agentpool']['courier_van'])
            courier_vehicle_pool = da.AgentPool(env=env, **model_params['agentpool']['courier_vehicle'])

            # Create sim runner params
            sim_params = {"num_agents":[model_params['agentpool'][i]['num_agents'] for i in model_params['agentpool']]}
            sim_params['agent_pools'] = [electric_bike_pool, courier_van_pool, courier_vehicle_pool]
            sim_params.update(model_params["sim"]["agent_gen"])

            #### RUN SIM ####
            env.process(agent_gen(env=env, sim_data_gen=sim_data, **sim_params))

            env.run(until=model_params['sim']['sim_time'])
            #### RUN SIM ####

            #### COLLECT PERFORMANCE METRICS ####
            df_sim_data.iloc[sim_run_i] = [sim_run_i, electric_bike_pool.throughput, electric_bike_pool.distance, electric_bike_pool.stops, electric_bike_pool.routes, model_params['agentpool']["electric_bike"]['num_agents'],
                                            courier_van_pool.throughput, courier_van_pool.distance, courier_van_pool.stops, courier_van_pool.routes, model_params['agentpool']["courier_van"]['num_agents'],
                                            courier_vehicle_pool.throughput, courier_vehicle_pool.distance, courier_vehicle_pool.stops, courier_vehicle_pool.routes, model_params['agentpool']["courier_vehicle"]['num_agents']]
            #### COLLECT PERFORMANCE METRICS ####
            inner.update(1)
        df_sim_data.to_csv(os.path.join(output_folder, f_name.split('.')[0] + '.csv'), index_label='expr_id')
        outer.update(1)
                
                    

def agent_gen(env, num_agents, route_length, agents, agent_params, agent_pools, package_dist, sim_data_gen):
    # Seed the model with initial agents
    packages_to_deliver = [sim_data_gen.generate_demand(route_length) for i in range(len(num_agents))]
    for i in range(len(num_agents)):
        for _ in range(num_agents[i] + 5):
            locations = [] 
            buildings = []
            num_packages = np.min([package_dist[i].rvs(), len(packages_to_deliver[i][0])]) # Generate number of packages this agent will hold
            #locations, buildings = sim_data_gen.generate_demand(num_packages) # Generate simulated data route
            for _ in range(num_packages):
                locations.append(packages_to_deliver[i][0].pop(0))
                buildings.append(packages_to_deliver[i][1].pop(0))
            delivery_schedule = da.DeliverySchedule(locations, buildings)

            temp_params = {'delivery_schedule':delivery_schedule, 'env':env} # Update agent parameters
            temp_params.update(agent_params[i])

            #agents[i](**temp_params)
            if i == 0:
                env.process(agent_pools[i].process_deliveries(agents[i](**temp_params), num_packages))
            else:
                env.process(agent_pools[i].process_deliveries(agents[i](**temp_params), num_packages, to_hub=1))

    # Continuously generate demand
    while True:
        for i in range(len(agent_pools)):
            if len(agent_pools[i].num_agents.queue) < 5:
                for _ in range(5-len(agent_pools[i].num_agents.queue)):
                    locations = [] 
                    buildings = []
                    num_packages = np.min([package_dist[i].rvs(), len(packages_to_deliver[i][0])]) # Generate number of packages this agent will hold
                    #locations, buildings = sim_data_gen.generate_demand(num_packages) # Generate simulated data route
                    for _ in range(num_packages):
                        locations.append(packages_to_deliver[i][0].pop(0))
                        buildings.append(packages_to_deliver[i][1].pop(0))
                    delivery_schedule = da.DeliverySchedule(locations, buildings)
                    #locations, buildings = sim_data_gen.generate_demand(num_packages) # Generate simulated data route
                    delivery_schedule = da.DeliverySchedule(locations, buildings)

                    temp_params = {'delivery_schedule':delivery_schedule, 'env':env} # Update agent parameters
                    temp_params.update(agent_params[i])

                    #agents[i](**temp_params)

                    if i == 0:
                        env.process(agent_pools[i].process_deliveries(agents[i](**temp_params), num_packages))
                    else:
                        env.process(agent_pools[i].process_deliveries(agents[i](**temp_params), num_packages, to_hub=1))

        yield env.timeout(1/12) # Wait 5 minutes before checking again

def parse_json(json):
    for key in json:
        if isinstance(json[key], dict):
            json[key] = parse_json(json[key])
        elif isinstance(json[key], list):
            for i in range(len(json[key])):
                if isinstance(json[key][i], str):
                    json[key][i] = eval(json[key][i])
                elif isinstance(json[key][i], dict):
                    json[key][i] = parse_json(json[key][i])
        elif isinstance(json[key], str):
            json[key] = eval(json[key])
        
    return json


def main():
    model_runner('sim_params', 'sim output', 322)

if __name__ == "__main__":
    main()

'''
TODO: Create agent generation outside of pool, but add logic to limit generation to num_agents

'''