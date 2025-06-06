import numpy as np
import math,os,shutil

def generate_traces_nop(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, bus_width, netname, chiplet_size, scale):
    
    num_bits_nop_eachLayer = [[0 for _ in range(len(dest_layers))] for _ in range(len(dest_layers))]

    num_chiplets_used = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
    nop_mesh_size = math.ceil(math.sqrt(num_chiplets_used))
    
    dir_name = os.path.join(
    'Interconnect', 
    f'{netname}_NoP_traces',
    f'{num_chiplets_used}_chiplet_size_{chiplet_size}_scale_{scale}_bus_width_{bus_width}'
    )
    print("CHECK:",dir_name)        
    if (os.path.isdir(dir_name)):
        shutil.rmtree(dir_name)
    
    os.makedirs(dir_name, exist_ok=True)
    os.chdir(dir_name)
    
    # loop: src_layer, find if the dest_layers of each src_layer need NoP
    for layer_idx in range(len(num_chiplet_eachLayer)):
        # print("layer_idx:",layer_idx)
        for dest_layer in dest_layers[layer_idx]:
            
            # if the src_layer_begin_chip and dest_layer_begin_chip are not on same chip -> need NoP, or 
            # if src_layer_begin_chip and dest_layer_begin_chip are on same chip, and src_layer and dest_layer are both dynamic layers, and two layers need diff num of chips -> need NoP
            if ((layer_location_begin_chiplet[dest_layer] != layer_location_begin_chiplet[layer_idx]) | ((layer_location_begin_chiplet[dest_layer] == num_used_static_chiplet_all_layers) & (layer_location_begin_chiplet[layer_idx] == num_used_static_chiplet_all_layers) & (num_chiplet_eachLayer[layer_idx] != num_chiplet_eachLayer[dest_layer]))):

                trace = np.array([[0,0,0]])
                
                num_src_chiplet = num_chiplet_eachLayer[layer_idx]
                num_dst_chiplet = num_chiplet_eachLayer[dest_layer]
                
                src_chiplet_begin = layer_location_begin_chiplet[layer_idx]
                src_chiplet_end = src_chiplet_begin + num_src_chiplet - 1
                
                dst_chiplet_begin = layer_location_begin_chiplet[dest_layer]
                dst_chiplet_end = dst_chiplet_begin + num_dst_chiplet - 1
                
                num_activations_per_chiplet = math.ceil(num_in_eachLayer[dest_layer]*config.BitWidth_in/(num_src_chiplet*num_dst_chiplet*scale*bus_width))
                
                num_bits_nop_eachLayer[layer_idx][dest_layer] += num_in_eachLayer[dest_layer]*config.BitWidth_in

                timestamp = 1

                for packet_idx in range(1, num_activations_per_chiplet):
                    for dest_chiplet_idx in range(dst_chiplet_begin, dst_chiplet_end+1):
                        for src_chiplet_idx in range(src_chiplet_begin, src_chiplet_end+1):
                            # trace = [trace; src_chiplet_idx-1 dest_chiplet_idx-1 timestamp]
                            if src_chiplet_idx != dest_chiplet_idx: 
                                # if src_chip is dest_chip, then no need for nop
                                trace = np.append(trace, [[src_chiplet_idx, dest_chiplet_idx, timestamp]], axis=0)
                        if (dest_chiplet_idx != dst_chiplet_end):
                            timestamp = timestamp + 1
                        
                    timestamp = timestamp + 1
                    
                filename = 'trace_file_srcL_' + str(layer_idx) +'_destL_' + str(dest_layer) + '.txt'
                
                trace = np.delete(trace, 0, 0)
                np.savetxt(filename, trace, fmt='%i')

    np.savetxt('nop_mesh_size.csv', [nop_mesh_size], fmt='%i')
    os.chdir("../..")
    
    return num_bits_nop_eachLayer