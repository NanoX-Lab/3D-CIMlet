import math
from utils.pe import Pe
from utils.chiplet import Chiplet

# refresh times for dynamic operation: latency of this layer
# refresh times for static operation: latency of this all layers (read out weights of all layers from DRAM before start)

# get performance of layer 'row'
def get_layer_energy_latency(row,config,technode,chiplet_type,memory_cell_type):

    if chiplet_type == 'static':
        pe_height = config.static_pe_height
        pe_width = config.static_pe_width
        subarray_width = config.static_subarray_width
        subarray_height = config.static_subarray_height
        chiplet_size = config.static_chiplet_height * config.static_chiplet_width
    elif chiplet_type == 'semi_static':
        pe_height = config.semistatic_pe_height
        pe_width = config.semistatic_pe_width
        subarray_width = config.semistatic_subarray_width
        subarray_height = config.semistatic_subarray_height
        chiplet_size = config.semistatic_chiplet_height * config.semistatic_chiplet_width
    elif chiplet_type == 'dynamic':
        pe_height = config.dynamic_pe_height
        pe_width = config.dynamic_pe_width
        subarray_width = config.dynamic_subarray_width
        subarray_height = config.dynamic_subarray_height
        chiplet_size = config.dynamic_chiplet_height * config.dynamic_chiplet_width
    
    clk_freq = getattr(config, f'{memory_cell_type}_clk_freq')
    
    num_used_pe_row = (row[2] / (pe_height * subarray_height))
    num_used_pe_col = math.ceil(row[3]*config.BitWidth_weight / (pe_width * subarray_width))
    num_used_pe = num_used_pe_row * num_used_pe_col
    num_used_chiplet = math.ceil(num_used_pe / chiplet_size)

    # overall init
    this_layer_performance = []
    total_write_latency_input = 0
    total_write_energy_input = 0
    total_write_latency_weight = 0
    total_write_energy_weight = 0
    total_read_latency_output = 0
    total_read_energy_output = 0
    total_refresh_latency_weight = 0
    total_refresh_energy_weight = 0 
    # ----- htree breakdown
    total_write_latency_input_pe_htree = 0 # included in total_write_latency_input
    total_write_latency_weight_pe_htree = 0 # included in total_write_latency_weight
    total_write_energy_input_pe_htree = 0 # included in total_write_energy_input
    total_write_energy_weight_pe_htree = 0 # included in total_write_energy_weight
    total_read_latency_output_pe_htree = 0 # included in total_read_latency_output
    total_read_energy_output_pe_htree = 0 # included in total_read_energy_output
    

    # chiplet:
    this_layer_in_bit = row[0]*row[1]*config.BitWidth_in
    this_layer_weight_bit = row[2]*row[3]*config.BitWidth_weight
    this_layer_in_bit_for_one_chiplet = math.ceil(this_layer_in_bit / num_used_chiplet)
    this_layer_weight_bit_for_one_chiplet = math.ceil(this_layer_weight_bit / num_used_chiplet)
    chiplet = Chiplet(config,chiplet_type,memory_cell_type,max(this_layer_in_bit_for_one_chiplet,this_layer_weight_bit_for_one_chiplet))

    # chiplet: write latency and energy (chiplet buffer to PE buffer)
    # ----- write input
    write_latency_input_chiplet = this_layer_in_bit / chiplet.buffer.bandwidth
    write_energy_input_chiplet = this_layer_in_bit * chiplet.buffer.get_energy_per_bit(config)[1]
    # ----- write weight
    write_latency_weight_chiplet = this_layer_weight_bit / chiplet.buffer.bandwidth
    write_energy_weight_chiplet = this_layer_weight_bit * chiplet.buffer.get_energy_per_bit(config)[1]
    # ----- add to total
    # total_write_latency_input += write_latency_input_chiplet
    total_write_energy_input += write_energy_input_chiplet
    # total_write_latency_weight += write_latency_weight_chiplet
    total_write_energy_weight += write_energy_weight_chiplet

    # pe init:
    max_write_latency_input_pe = 0
    max_write_latency_weight_pe = 0
    max_read_latency_output_pe = 0
    max_refresh_latency_weight_pe = 0
    total_num_used_subarray = 0
    # --- htree breakdown
    max_write_latency_input_pe_htree = 0
    max_write_latency_weight_pe_htree = 0
    max_read_latency_output_pe_htree = 0

    # get all kinds of latency: pe level, assume all pes work simultaneously, get the max value of one pe.
    num_used_pe_row = math.ceil(num_used_pe_row)

    for pe_row_idx in range(num_used_pe_row):
        for pe_col_idx in range(num_used_pe_col):
            pe = Pe(config,technode,chiplet_type,memory_cell_type,chiplet.buffer_mem_height,chiplet.buffer_mem_width)
            
            if (pe_row_idx != num_used_pe_row -1) & (pe_col_idx != num_used_pe_col -1):
                pe.used_pe_height = pe.pe_height
                pe.used_pe_width = pe.pe_width
            elif (pe_row_idx != num_used_pe_row -1):
                pe.used_pe_height = pe.pe_height
                pe.used_pe_width = (row[3]*config.BitWidth_weight - subarray_width * pe_width *(num_used_pe_col-1)) / subarray_width
            elif (pe_col_idx != num_used_pe_col -1):
                pe.used_pe_width = pe.pe_width
                pe.used_pe_height = (row[2] - subarray_height * pe_height * (num_used_pe_row-1)) / subarray_height
            else: #(pe_row_idx == num_used_pe_row -1) & (pe_col_idx == num_used_pe_col -1)
                pe.used_pe_width = (row[3]*config.BitWidth_weight - subarray_width * pe_width *(num_used_pe_col-1)) / subarray_width
                pe.used_pe_height = (row[2] - subarray_height * pe_height * (num_used_pe_row-1)) / subarray_height
            
            num_used_subarray = pe.used_pe_height * pe.used_pe_width
            total_num_used_subarray += num_used_subarray
            
            # pe:
            # write input latency and energy (PE buffer to subarray)
            num_bit_input_write_pe = (pe.used_pe_height * pe.used_pe_width) * subarray_height
            # write_latency_input_pe = num_bit_input_write_pe / subarray_height * 1/clk_freq # write in subarray-by-subarray, write all wordlines in a subarray simultaneously
            write_latency_input_pe = 0
            write_energy_input_pe = num_bit_input_write_pe * pe.buffer.get_energy_per_bit(config)[1]
            write_latency_input_subarray = 0
            write_energy_input_subarray = num_bit_input_write_pe * pe.subarray.write_energy_per_bit
            write_energy_input_pe += write_energy_input_subarray
            write_latency_input_pe_htree = pe.htree.get_latency(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=0, numBitToLoadIn=num_bit_input_write_pe)
            # print("write_latency_input_pe_htree=",write_latency_input_pe_htree)
            # write_latency_input_pe += write_latency_input_pe_htree
            write_energy_input_pe_htree = pe.htree.get_energy(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=0, numBitToLoadIn=num_bit_input_write_pe)
            # print("write_energy_input_pe_htree=",write_energy_input_pe_htree)
            write_energy_input_pe += write_energy_input_pe_htree ### htree

            # write weight latency and energy (PE buffer to subarray)
            num_bit_weight_write_pe = (pe.used_pe_width * pe.used_pe_height) * (subarray_width * subarray_height)
            # write_latency_weight_pe = pe.used_pe_width * pe.used_pe_height * subarray_height * 1/clk_freq # write in subarray-by-subarray
            write_latency_weight_pe = subarray_height * 1/clk_freq # write in subarray-by-subarray
            write_energy_weight_pe = num_bit_weight_write_pe * pe.buffer.get_energy_per_bit(config)[1]
            write_latency_weight_subarray = 0
            write_energy_weight_subarray = num_bit_weight_write_pe * pe.subarray.write_energy_per_bit
            write_energy_weight_pe += write_energy_weight_subarray
            write_latency_weight_pe_htree = pe.htree.get_latency(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=0, numBitToLoadIn=num_bit_weight_write_pe)
            # print("write_latency_weight_pe_htree=",write_latency_weight_pe_htree)
            # write_latency_weight_pe += write_latency_weight_pe_htree ### htree
            write_energy_weight_pe_htree = pe.htree.get_energy(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=0, numBitToLoadIn=num_bit_weight_write_pe)
            # print("write_energy_weight_pe_htree=",write_energy_weight_pe_htree)
            write_energy_weight_pe += write_energy_weight_pe_htree ### htree

            # read output
            # num_bit_read_pe = pe.used_pe_width * subarray_width * row[0] * config.BitWidth_in
            num_bit_read_pe = pe.used_pe_width * subarray_width * row[0]
            num_bit_read_pe_for_energy = num_used_subarray * subarray_width * row[0]
            # -----read output latency
            read_latency_output_pe = 0
            # read_latency_output_subarrayArray = num_bit_read_pe / config.subarray_readout_mux * 1/clk_freq
            # read_latency_output_subarrayArray = row[0] * (subarray_height * config.BitWidth_in) * 1/clk_freq
            read_latency_output_subarrayArray = row[0] * ( config.BitWidth_in) * 1/clk_freq
            read_latency_output_subarrayShiftAdd = (row[0] * config.BitWidth_in) * 1/clk_freq
            read_latency_output_subarraytoPeBuffer = num_bit_read_pe / pe.buffer.bandwidth
            # read_latency_output_subarray = read_latency_output_subarrayArray + read_latency_output_subarrayShiftAdd + read_latency_output_subarraytoPeBuffer
            read_latency_output_subarray = read_latency_output_subarrayArray
            read_latency_output_peAcc = (row[0] * pe.used_pe_height * pe.used_pe_width * config.BitWidth_in) * 1/clk_freq
            read_latency_output_toPeBuffer = (row[0] * pe.used_pe_width * config.BitWidth_in) / pe.buffer.bandwidth
            read_latency_output_pe_htree = pe.htree.get_latency(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=num_bit_read_pe, numBitToLoadIn=0)
            # print("read_latency_output_pe_htree=",read_latency_output_pe_htree)
            # read_latency_output_pe += read_latency_output_subarray + read_latency_output_peAcc + read_latency_output_toPeBuffer
            read_latency_output_pe += read_latency_output_subarray
            # read_latency_output_pe += read_latency_output_pe_htree ### htree
            # -----read output energy
            read_energy_output_pe = 0
            read_energy_output_subarrayArray = num_bit_read_pe_for_energy * pe.subarray.read_energy_per_bit
            read_energy_output_subarrayShiftAdd = (row[0] * config.BitWidth_in) * pe.subarray.shiftadd.energy_per_bit
            read_energy_output_subarraytoPeBuffer = num_bit_read_pe_for_energy * pe.buffer.get_energy_per_bit(config)[0]
            read_energy_output_subarray = read_energy_output_subarrayArray + read_energy_output_subarrayShiftAdd + read_energy_output_subarraytoPeBuffer

            read_energy_output_peAcc = (row[0] * pe.used_pe_height * pe.used_pe_width * config.BitWidth_in) * pe.accumulator.energy_per_bit
            read_energy_output_toPeBuffer = (row[0] * pe.used_pe_width * config.BitWidth_in) * pe.buffer.get_energy_per_bit(config)[0]
            read_energy_output_pe_htree = pe.htree.get_energy(x_init=0, y_init=0, x_end=0, y_end=0, numBitToLoadOut=num_bit_read_pe, numBitToLoadIn=0)
            # print("read_energy_output_pe_htree=",read_energy_output_pe_htree)

            read_energy_output_pe += read_energy_output_subarray + read_energy_output_peAcc + read_energy_output_toPeBuffer
            read_energy_output_pe += read_energy_output_pe_htree ### htree

            # -----if read output need softmax, latency and energy
            if row[7]: # have softmax operation, need sfu
                read_latency_output_peSfu = (row[4]*row[5]) * pe.sfu.latency_per_byte
                read_energy_output_peSfu = (row[4]*row[5]) * pe.sfu.get_energy_per_byte() / (num_used_pe if num_used_pe > 1 else 1)
                # read_latency_output_pe += read_latency_output_peSfu
                read_energy_output_pe += read_energy_output_peSfu

            # refesh weight latency and energy (all subarrays in a PE)
            # only used if this layer is on dynamic chiplet: only refresh in this layer time duration
            refresh_retention_time = getattr(config, f'{memory_cell_type}_refresh_retention_time_{technode}nm')
            num_refresh_times_pe = math.floor(write_latency_input_pe + write_latency_weight_pe + read_latency_output_pe) / refresh_retention_time
            refresh_latency_weight_pe = write_latency_weight_pe * num_refresh_times_pe
            refresh_power_per_bit = getattr(config, f'{memory_cell_type}_refresh_power_per_bit_{technode}nm')
            refresh_energy_weight_pe = (num_bit_weight_write_pe * num_refresh_times_pe) * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
            
            # -----pe latency: take max., pe energy:add to total
            max_write_latency_input_pe = max(max_write_latency_input_pe,write_latency_input_pe)
            total_write_energy_input += write_energy_input_pe

            max_write_latency_weight_pe = max(max_write_latency_weight_pe,write_latency_weight_pe)
            total_write_energy_weight += write_energy_weight_pe

            max_read_latency_output_pe = max(max_read_latency_output_pe,read_latency_output_pe)
            total_read_energy_output += read_energy_output_pe

            max_refresh_latency_weight_pe = max(max_refresh_latency_weight_pe,refresh_latency_weight_pe)
            total_refresh_energy_weight += refresh_energy_weight_pe
            
            # TODO (done): all inside pe-level htree latency and energy is listed and printed as breakdown, added to pe-level result.
            # ---------- htree breakdown
            max_write_latency_input_pe_htree = max(max_write_latency_input_pe_htree,write_latency_input_pe_htree)
            total_write_energy_input_pe_htree += write_energy_input_pe_htree

            max_write_latency_weight_pe_htree = max(max_write_latency_weight_pe_htree,write_latency_weight_pe_htree)
            total_write_energy_weight_pe_htree += write_energy_weight_pe_htree

            max_read_latency_output_pe_htree = max(max_read_latency_output_pe_htree,read_latency_output_pe_htree)
            total_read_energy_output_pe_htree += read_energy_output_pe_htree
            

    total_write_latency_input += max_write_latency_input_pe
    total_write_latency_weight += max_write_latency_weight_pe
    total_read_latency_output += max_read_latency_output_pe
    total_refresh_latency_weight += max_refresh_latency_weight_pe
    # -----htree breakdown
    total_write_latency_input_pe_htree += max_write_latency_input_pe_htree
    total_write_latency_weight_pe_htree += max_write_latency_weight_pe_htree
    total_read_latency_output_pe_htree += max_read_latency_output_pe_htree

    # chiplet: read output latency and energy (PE buffer to chiplet buffer)
    if num_used_chiplet > 1:
        # -----read output latency
        read_latency_output_chipletAcc = num_used_pe_row * row[4]*row[5]*config.BitWidth_in / num_used_chiplet * 1/clk_freq
        read_latency_output_chipletBuffer = row[4]*row[5]*config.BitWidth_in / chiplet.buffer.bandwidth
        read_latency_output_chiplet = read_latency_output_chipletAcc + read_latency_output_chipletBuffer
        # -----read output energy
        read_energy_output_chipletAcc = num_used_pe_row * row[4]*row[5]*config.BitWidth_in * chiplet.accumulator.energy_per_bit
        read_energy_output_chipletBuffer = row[4]*row[5]*config.BitWidth_in * chiplet.buffer.get_energy_per_bit(config)[0]
        read_energy_output_chiplet = read_energy_output_chipletAcc + read_energy_output_chipletBuffer
        # ----- add to total
        # total_read_latency_output += read_latency_output_chiplet
        total_read_energy_output += read_energy_output_chiplet
        # ----- read & write latency / num_chipet used this layer
        # total_write_latency_input /= num_used_chiplet
        # total_write_latency_weight /= num_used_chiplet
        # total_read_latency_output /= num_used_chiplet
        # total_refresh_latency_weight /= num_used_chiplet
        # total_write_latency_input_pe_htree /= num_used_chiplet # included in total_write_latency_input
        # total_write_latency_weight_pe_htree /= num_used_chiplet # included in total_write_latency_weight
        # total_read_latency_output_pe_htree /= num_used_chiplet # included in total_read_latency_output

    this_layer_performance.append(total_write_latency_input) # [0]
    this_layer_performance.append(total_write_energy_input) # [1]

    this_layer_performance.append(total_write_latency_weight) # [2]
    this_layer_performance.append(total_write_energy_weight) # [3]

    this_layer_performance.append(total_read_latency_output) # [4]
    this_layer_performance.append(total_read_energy_output) # [5]
    #-----------refresh----------
    if row[6]== 1: # is dynamic layer
        this_layer_performance.append(total_refresh_latency_weight) # [6] # only used if this layer is on dynamic chiplet
        this_layer_performance.append(total_refresh_energy_weight) # [7] # only used if this layer is on dynamic chiplet
    else: # is static layer
        this_layer_performance.append(0) # [6] 
        this_layer_performance.append(0) # [7]

    # # TODO (done in main.py):
    # # refesh weight latency and energy (all subarrays in a PE)
    # # only used if this layer is on static chiplet: refresh in all-layer time duration
    # refresh_retention_time = math.floor(getattr(config, memory_cell_type + '_refresh_retention_time'))
    # num_refresh_times = all_layer_all_latency / refresh_retention_time
    # refresh_latency_weight = max(max_write_latency_weight of each layer) * num_refresh_times
    # refresh_energy_weight = (num_bit_weight_write_all_layers * num_refresh_times) * pe.subarray.write_energy_per_bit
    #-----------refresh end----------

    this_layer_performance.append(total_write_latency_input_pe_htree) # [8] 
    this_layer_performance.append(total_write_energy_input_pe_htree) # [9] 
    this_layer_performance.append(total_write_latency_weight_pe_htree) # [10] 
    this_layer_performance.append(total_write_energy_weight_pe_htree) # [11] 
    this_layer_performance.append(total_read_latency_output_pe_htree) # [12] 
    this_layer_performance.append(total_read_energy_output_pe_htree) # [13] 
    
    return num_used_chiplet,num_used_pe, total_num_used_subarray,this_layer_performance,pe.subarray.write_energy_per_bit

