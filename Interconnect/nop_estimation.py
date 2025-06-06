import os

from Interconnect.generate_traces_nop import generate_traces_nop
from Interconnect.run_booksim_mesh_chiplet_nop import run_booksim_mesh_chiplet_nop

def nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, netname, chiplet_size, nop_clk_freq):
    
    scale = config.scale_nop
    bus_width = config.chiplet_bus_width_2D
    num_chiplets = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
    
    num_bits_nop_eachLayer = generate_traces_nop(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, bus_width, netname, chiplet_size, scale)

    print("n_bits_all_chiplets : ",sum(sum(row) for row in num_bits_nop_eachLayer))

    print('Trace generation for NoP is finished')
    print('Starting to simulate the NoP trace')
    
    # Get the project root directory /3D-CIMlet 
    base_dir = os.path.dirname(os.getcwd())

    # current directory
    interconnect_dir = os.getcwd()  # /3D-CIMlet/Interconnect

    results_dir = os.path.join(base_dir, 'Final_Results')

        
    # Build the directory path
    trace_directory_name = f'{num_chiplets}_chiplet_size_{chiplet_size}_scale_{scale}_bus_width_{bus_width}/'
    trace_directory_full_path = os.path.join(interconnect_dir, f'{netname}_NoP_traces', trace_directory_name)

    results_directory_name = trace_directory_name
    results_directory_full_path = os.path.join(results_dir, f'NoP_Results_{netname}', results_directory_name)

    run_booksim_mesh_chiplet_nop(config,nop_clk_freq,trace_directory_full_path, bus_width)

    if not os.path.exists(results_directory_full_path):
        os.makedirs(results_directory_full_path)

    os.system(f'rm -rf {os.path.join(results_directory_full_path, "logs_NoP")}')
    os.system(f'mv {os.path.join(interconnect_dir, "logs_NoP")} {results_directory_full_path}')
    
    print('finish simulate the NoP trace')

    # return area (not used)
    area = 0.0
    nop_area_file_path = os.path.join(results_directory_full_path, 'logs_NoP', 'Area_chiplet.csv')

    with open(nop_area_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoP area is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    area += float(parts[1])
    area *= 1e-12 # get m2

    print("Total area from booksim nop_area_file_path:", area)

    # return latency (not used)
    latency_list = []
    nop_latency_file_path = os.path.join(results_directory_full_path, 'logs_NoP', 'Latency_chiplet.csv')

    with open(nop_latency_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoP latency is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    latency_list.append(float(parts[1]))
    latency_list = [latency * scale for latency in latency_list]
    total_latency = sum(latency_list)

    print("Total latency from booksim nop_latency_file_path:", total_latency)
    

    # return latencyCycle_eachLayer (used)
    # NoP_LatencyCycle_eachLayer.csv
    # ('NoP latency for layer' +'\t' + str(run_id) + '\t'+'is' +'\t' + str(latency) +'\t' + 'cycles' + '\n')
    num_layers = len(num_in_eachLayer)
    latencyCycle_eachLayer_list = [[0 for _ in range(num_layers)] for _ in range(num_layers)]
    nop_latency_eachlayer_file_path = os.path.join(results_directory_full_path, 'logs_NoP', 'NoP_LatencyCycle_eachLayer.csv')

    with open(nop_latency_eachlayer_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("NoP latency for layer"):
                parts = line.split('\t')
                if len(parts) > 4:
                    latency = int(parts[3])
                    # extract src_layer_idx and dest_layer_idx
                    run_info = parts[1]  # e.g.'3_to_5'
                    src_layer_idx, dest_layer_idx = map(int, run_info.split('_to_'))
                    
                    latencyCycle_eachLayer_list[src_layer_idx][dest_layer_idx] = latency
    latencyCycle_eachLayer_list = [latency * scale for latency in latencyCycle_eachLayer_list]

    # return energy (not used)
    power_list = []
    nop_power_file_path = os.path.join(results_directory_full_path, 'logs_NoP', 'Energy_chiplet.csv')

    with open(nop_power_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Total NoP power is"):
                parts = line.split('\t')
                if len(parts) > 1:
                    power_list.append(float(parts[1]))
    
    if len(latency_list) != len(power_list):
        raise ValueError("The length of latency_list and power_list must be the same.")
    energy = sum(l * p for l, p in zip(latency_list, power_list))

    print("Total energy from booksim nop_energy_file_path:", energy)

    os.chdir("..") # back to /3D-CIMlet from /3D-CIMlet/Interconnect
    
    return area, total_latency, energy, num_bits_nop_eachLayer, latencyCycle_eachLayer_list
            
    
                    
