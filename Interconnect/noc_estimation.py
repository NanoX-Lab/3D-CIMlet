import os

from Interconnect.generate_traces_noc import generate_traces_noc
from Interconnect.run_booksim_noc import run_booksim_noc

def interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,chiplet_static_type,num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers, layer_location_begin_chiplet, netname, chiplet_size):
    
    scale = config.scale_noc
    
    num_chiplets = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
 
    generate_traces_noc(config, num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers, layer_location_begin_chiplet, netname, chiplet_size, num_chiplets, scale)

    print('Trace generation for NoC is finished')
    print('Starting to simulate the NoC trace')

    # Get the project root directory /3D-CIMlet 
    base_dir = os.path.dirname(os.getcwd())

    # current directory
    interconnect_dir = os.getcwd()  # /3D-CIMlet/Interconnect

    results_dir = os.path.join(base_dir, 'Final_Results')

        
    # Build the directory path
    trace_directory_name = f'{num_chiplets}_chiplet_size_{chiplet_size}_scale_{scale}/'
    trace_directory_full_path = os.path.join(interconnect_dir, f'{netname}_NoC_traces', trace_directory_name)

    results_directory_name = trace_directory_name
    results_directory_full_path = os.path.join(results_dir, f'NoC_Results_{netname}', results_directory_name)

    run_booksim_noc(config, trace_directory_full_path, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type)

    if not os.path.exists(results_directory_full_path):
        os.makedirs(results_directory_full_path)

    os.system(f'rm -rf {os.path.join(results_directory_full_path, "logs")}')
    os.system(f'mv {os.path.join(interconnect_dir, "logs")} {results_directory_full_path}')

    print('finish simulate the NoC trace')

    # return area
    area = 0.0
    noc_area_file_path = os.path.join(results_directory_full_path, 'logs', 'Area_chiplet.csv')

    with open(noc_area_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoC area is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    area += float(parts[1])
    area *= 1e-12 # get m2

    print("Total area from booksim noc_area_file_path:", area)

    # return latency
    latency_list = []
    noc_latency_file_path = os.path.join(results_directory_full_path, 'logs', 'Latency_chiplet.csv')

    with open(noc_latency_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoC latency is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    latency_list.append(float(parts[1]))
    latency_list = [latency * scale for latency in latency_list]
    latency = sum(latency_list)

    print("Total latency from booksim noc_latency_file_path:", latency)

    # return energy
    power_list = []
    noc_power_file_path = os.path.join(results_directory_full_path, 'logs', 'Energy_chiplet.csv')

    with open(noc_power_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoC power is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    power_list.append(float(parts[1]))
    
    if len(latency_list) != len(power_list):
        print("latency_list len:",latency_list)
        print("power_list len:",power_list)
        raise ValueError("The length of latency_list and power_list must be the same.")
    energy = sum(l * p for l, p in zip(latency_list, power_list))

    print("Total energy from booksim noc_energy_file_path:", energy)
    
    os.chdir("..") # back to /3D-CIMlet from /3D-CIMlet/Interconnect

    return area, latency, energy
