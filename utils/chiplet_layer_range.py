import math,re
import numpy as np

def get_static_chiplet_layer_range(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer):
    static_chiplet_size = config.static_chiplet_size

    # get layers in each static chiplet (chiplet_layer_range list :layer?~? in chiplet i)
    chiplet_availability = [static_chiplet_size] * config.num_static_chiplet  # Initialize all chiplets' unmapped PE to be static_chiplet_size
    chiplet_layer_range = np.full((config.num_static_chiplet, 2), -1)  # Initialize to be -1，have not placed any layer
    layer_location_begin_chiplet = [-1 for _ in range(len(Num_StaticPE_eachLayer))] # tell this layer is on which chiplet
    
    last_chiplet_used = 0  # Used to record the last used chiplet index

    for layer_idx, layer in enumerate(range(len(Num_StaticPE_eachLayer))):
        # print("layer:", layer)
        required_pes = Num_StaticPE_eachLayer[layer]
        # print("required_pes:", required_pes)
        if required_pes == 0:  # is dynamic layer，skip layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        # num_static_chiplet_this_layer = ceil(required_pes / static_chiplet_size)
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        # Split the PE requirements for this layer equally across multiple chiplets
        if num_static_chiplet_this_layer >1:
            pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
            last_chiplet_used += 1 # the layer need more than 1 chiplet, then start with a new chiplet
            for i in range(num_static_chiplet_this_layer):
                chiplet_availability[last_chiplet_used + i] -= pe_used_per_chiplet

                # update chiplet_layer_range list
                if chiplet_layer_range[last_chiplet_used + i, 0] == -1:
                    chiplet_layer_range[last_chiplet_used + i, 0] = layer
                chiplet_layer_range[last_chiplet_used + i, 1] = layer
            
            layer_location_begin_chiplet[layer_idx] = last_chiplet_used # tell this layer is on which chiplet
            
            last_chiplet_used = last_chiplet_used + num_static_chiplet_this_layer # update next chiplet index

        else: # num_static_chiplet_this_layer ==1
            while required_pes > 0 and last_chiplet_used + num_static_chiplet_this_layer <= config.num_static_chiplet:
                chiplet_index = last_chiplet_used
                available_pe = chiplet_availability[chiplet_index]
                print("chiplet_index:", chiplet_index)
                print("required_pes:", required_pes)
                print("available_pe:", available_pe)
                
                if required_pes <= available_pe:
                    chiplet_availability[chiplet_index] -= required_pes
                    required_pes -= required_pes
                    
                    # update chiplet_layer_range
                    if chiplet_layer_range[chiplet_index, 0] == -1:
                        chiplet_layer_range[chiplet_index, 0] = layer
                    chiplet_layer_range[chiplet_index, 1] = layer
                    
                    # tell this layer is on which chiplet
                    layer_location_begin_chiplet[layer_idx] = last_chiplet_used

                else:
                    print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                    last_chiplet_used += 1
        
        if (last_chiplet_used + 1) > config.num_static_chiplet:
            print(f"Layer {layer} requires more chiplets than available.")
            break
    
    num_used_chiplet = last_chiplet_used + 1
    # print("last_chiplet_used:", last_chiplet_used)
    
    # discard unused chiplets (which are filled with -1)
    chiplet_layer_range = chiplet_layer_range[0:num_used_chiplet]
    
    # discard chiplets without inner-chip NoC (will fill with -1)
    for chip_idx in range(len(chiplet_layer_range)):
        # if in this chip, only have 1 layer or have 2 consecutive layer, no discard.
        if (chiplet_layer_range[chip_idx][0]==chiplet_layer_range[chip_idx][1])|((chiplet_layer_range[chip_idx][1]==chiplet_layer_range[chip_idx][0]+1)):
            continue
        # if in this chip, only have more than 2 layers, and if any of the layers is on dynamic chip or is not on this static chip, discard (fill this chip's begin_layer and end_layer with -1, and process in generate_noc_trace).
        else:
            for layer in range(chiplet_layer_range[chip_idx][0],chiplet_layer_range[chip_idx][1]):
                if (layer_location_begin_chiplet[layer] == -1)|(layer_location_begin_chiplet[layer]!= chip_idx):
                    chiplet_layer_range[chip_idx][0] = -1
                    chiplet_layer_range[chip_idx][1] = -1
        
    
    print("chiplet_layer_range:", chiplet_layer_range)
    
    print("layer_location_begin_chiplet:",layer_location_begin_chiplet)
    
    return chiplet_layer_range, chiplet_availability, num_used_chiplet,layer_location_begin_chiplet

def get_static_chiplet_layers(config,net_structure,net_structure_layer_def,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer):
    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width

    # get layers in each static chiplet (chiplet_layer_range list :layer?~? in chiplet i)
    chiplet_availability = [static_chiplet_size] * config.num_static_chiplet  # Initialize all chiplets' unmapped PE to 'static_chiplet_size'
    chiplet_layers = [[] for _ in range(config.num_static_chiplet)]
    layer_location_begin_chiplet = [-1 for _ in range(len(Num_StaticPE_eachLayer))] # tell this layer is on which chiplet
    
    last_chiplet_used = 0  # Used to record the index of last used chiplet
    chiplet_index = 0
    num_used_chiplet = 0
    
    # go through static layers (weights - pretrained but not learned)
    for layer_idx, layer in enumerate(net_structure):
            
        required_pes = Num_StaticPE_eachLayer[layer_idx]
        if required_pes == 0:  # is dynamic layer，skip this layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        if (layer[6] == 0) and (net_structure_layer_def[layer_idx] not in('adapter 1-1,','adapter 1-2,','adapter 2-1,','adapter 2-2,','output weight projection,', 'FP:adapter 1-1,','FP:adapter 1-2,','FP:adapter 2-1,','FP:adapter 2-2,','FP:output weight projection,')): # is static layer
            # Split the PE requirements for this layer equally across multiple chiplets
            if num_static_chiplet_this_layer >1:
                pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
                if last_chiplet_used != 0:
                    chiplet_index = last_chiplet_used + 1 # the layer need more than 1 chiplet, then start with a new chiplet
                for i in range(num_static_chiplet_this_layer):
                    chiplet_availability[chiplet_index + i] -= pe_used_per_chiplet

                    # update chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index + i].append(layer_idx)
                
                layer_location_begin_chiplet[layer_idx] = chiplet_index # tell this layer is on which chiplet
                
                last_chiplet_used = chiplet_index + num_static_chiplet_this_layer-1 # update next chiplet index
                
                num_used_chiplet = last_chiplet_used + 1

            else: # num_static_chiplet_this_layer == 1
                while required_pes > 0 and num_used_chiplet + num_static_chiplet_this_layer <= config.num_static_chiplet:
                    if (layer_idx != 0) and (num_static_chiplet_eachLayer[layer_idx-1]>1):
                        chiplet_index = last_chiplet_used + 1
                    else:
                        chiplet_index = last_chiplet_used
                    available_pe = chiplet_availability[chiplet_index]
                    
                    if required_pes <= available_pe:
                        chiplet_availability[chiplet_index] -= required_pes
                        required_pes -= required_pes
                        
                        # update chiplet_layers of this chiplet
                        chiplet_layers[chiplet_index].append(layer_idx)
                        
                        # tell this layer is on which chiplet
                        layer_location_begin_chiplet[layer_idx] = chiplet_index
                        
                        # update last_chiplet_used
                        last_chiplet_used = chiplet_index

                    else:
                        # print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                        last_chiplet_used += 1
                        num_used_chiplet += 1
            
            if (last_chiplet_used + 1) > config.num_static_chiplet:
                print(f"Layer {layer_idx} requires more chiplets than available.")
                break
            if num_used_chiplet != (last_chiplet_used + 1):
                num_used_chiplet = (last_chiplet_used + 1)

    # for chiplet_index in range(num_used_chiplet,config.num_static_chiplet):
    #     chiplet_availability[chiplet_index] = config.static_chiplet_height * config.static_chiplet_width
    
    # go through static layers (weights - learned)
    for layer_idx, layer in enumerate(net_structure):
            
        required_pes = Num_StaticPE_eachLayer[layer_idx]
        if required_pes == 0:  # is dynamic layer，skip this layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        if layer[6] == 0 and (net_structure_layer_def[layer_idx] in('adapter 1-1,','adapter 1-2,','adapter 2-1,','adapter 2-2,','output weight projection,', 'FP:adapter 1-1,','FP:adapter 1-2,','FP:adapter 2-1,','FP:adapter 2-2,','FP:output weight projection,')): # is static layer
            # Split the PE requirements for this layer equally across multiple chiplets
            # print("test_layer_idx:",layer_idx)
            if num_static_chiplet_this_layer >1:
                pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
                if last_chiplet_used != 0:
                    chiplet_index = last_chiplet_used + 1 # the layer need more than 1 chiplet, then start with a new chiplet
                for i in range(num_static_chiplet_this_layer):
                    chiplet_availability[chiplet_index + i] -= pe_used_per_chiplet

                    # update chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index + i].append(layer_idx)
                
                layer_location_begin_chiplet[layer_idx] = chiplet_index # tell this layer is on which chiplet
                
                last_chiplet_used = chiplet_index + num_static_chiplet_this_layer-1 # update next chiplet index
                
                num_used_chiplet = last_chiplet_used + 1

            else: # num_static_chiplet_this_layer == 1
                while required_pes > 0 and num_used_chiplet + num_static_chiplet_this_layer <= config.num_static_chiplet:
                    if (layer_idx != 0) and (num_static_chiplet_eachLayer[layer_idx-1]>1):
                        chiplet_index = last_chiplet_used + 1
                    # if this chip has mapped static layers (pretrained weights), this static layer (learned weights) mapped to a new chip
                    elif any((net_structure[layer_index][6] == 0 and net_structure_layer_def[layer_index] not in ('adapter 1-1,', 'adapter 1-2,', 'adapter 2-1,', 'adapter 2-2,', 'output weight projection,')) for layer_index in chiplet_layers[last_chiplet_used]):
                        chiplet_index = last_chiplet_used + 1 ######
                    else:
                        chiplet_index = last_chiplet_used
                    available_pe = chiplet_availability[chiplet_index]
                    
                    if required_pes <= available_pe:
                        chiplet_availability[chiplet_index] -= required_pes
                        required_pes -= required_pes
                        
                        # update chiplet_layers of this chiplet
                        chiplet_layers[chiplet_index].append(layer_idx)
                        
                        # tell this layer is on which chiplet
                        layer_location_begin_chiplet[layer_idx] = chiplet_index
                        
                        # update last_chiplet_used
                        last_chiplet_used = chiplet_index

                    else:
                        # print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                        last_chiplet_used += 1
                        num_used_chiplet += 1
            
            if (last_chiplet_used + 1) > config.num_static_chiplet:
                print(f"Layer {layer_idx} requires more chiplets than available.")
                break
            if num_used_chiplet != (last_chiplet_used + 1):
                num_used_chiplet = (last_chiplet_used + 1)
    
    chiplet_availability[num_used_chiplet:] = [config.semistatic_chiplet_height * config.semistatic_chiplet_width] * (len(chiplet_availability) - num_used_chiplet) # update chip size for semi-static chip
    
    # go through semi-static layers
    for layer_idx, layer in enumerate(net_structure):
            
        required_pes = Num_StaticPE_eachLayer[layer_idx]
        if required_pes == 0:  # is dynamic layer，skip this layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        if layer[6] == 2: # is semi-static layer

            chiplet_availability[num_used_chiplet:] = [config.semistatic_chiplet_height * config.semistatic_chiplet_width] * (len(chiplet_availability) - num_used_chiplet) # update chip size for semi-static chip

            # Split the PE requirements for this layer equally across multiple chiplets
            if num_static_chiplet_this_layer >1:
                pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
                if last_chiplet_used != 0:
                    chiplet_index = last_chiplet_used + 1 # the layer need more than 1 chiplet, then start with a new chiplet
                
                for i in range(num_static_chiplet_this_layer):
                    if chiplet_index + i < len(chiplet_availability):
                        chiplet_availability[chiplet_index + i] = config.semistatic_chiplet_height * config.semistatic_chiplet_width # update chip size for semi-static chip
                        chiplet_availability[chiplet_index + i] -= pe_used_per_chiplet
                    else:
                        print(f"Warning: Layer {layer_idx} need {num_static_chiplet_this_layer} chip, i= {i}, chiplet_index {chiplet_index + i} out of range.")

                    # update chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index + i].append(layer_idx)
                
                layer_location_begin_chiplet[layer_idx] = chiplet_index # tell this layer is on which chiplet
                
                last_chiplet_used = chiplet_index + num_static_chiplet_this_layer-1 # update next chiplet index
                
                num_used_chiplet = last_chiplet_used + 1

            else: # num_static_chiplet_this_layer == 1
                while required_pes > 0 and num_used_chiplet + num_static_chiplet_this_layer <= config.num_static_chiplet:
                    # if last layer use more than 1 chip, this layer mapped to a new chip 
                    if (layer_idx != 0) and (net_structure[layer_idx-1][6]==2) and (num_static_chiplet_eachLayer[layer_idx-1]>1):
                        chiplet_index = last_chiplet_used + 1
                    # if this chip has mapped static layers, this semi-static layer mapped to a new chip
                    elif any(net_structure[layer_index][6] == 0 for layer_index in chiplet_layers[last_chiplet_used]):
                        chiplet_index = last_chiplet_used + 1
                    else:
                        chiplet_index = last_chiplet_used
                    
                    available_pe = chiplet_availability[chiplet_index]
          
                    if required_pes <= available_pe:
                        chiplet_availability[chiplet_index] -= required_pes
                        available_pe -= required_pes
                        # print("available_pe:", available_pe)
                        required_pes -= required_pes
                        
                        # update chiplet_layers of this chiplet
                        chiplet_layers[chiplet_index].append(layer_idx)
                        
                        # tell this layer is on which chiplet
                        layer_location_begin_chiplet[layer_idx] = chiplet_index
                        
                        # update last_chiplet_used
                        last_chiplet_used = chiplet_index

                    else:
                        print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                        last_chiplet_used += 1
                        num_used_chiplet += 1
            
            if (last_chiplet_used + 1) > config.num_static_chiplet:
                print(f"Layer {layer_idx} requires more chiplets than available.")
                break
            if num_used_chiplet != (last_chiplet_used + 1):
                num_used_chiplet = (last_chiplet_used + 1)

    # discard unused chiplets (which are filled with -1)
    chiplet_layers = chiplet_layers[0:num_used_chiplet]
    print("chiplet_layers:", chiplet_layers)
    
    # mark the static chip type to semi-static or not: static:0, semi-static:2. 
    chiplet_static_type = [0] * len(chiplet_layers)
    for chiplet_idx in range(len(chiplet_layers)):
        for layer_idx in chiplet_layers[chiplet_idx]:
            if net_structure[layer_idx][6] == 2:
                chiplet_static_type[chiplet_idx] = 2
    print("chiplet_static_type:",chiplet_static_type)

    num_used_static_chiplet = 0
    num_used_semi_static_chiplet = 0
    for chiplet_type in chiplet_static_type:
        if chiplet_type == 0:
            num_used_static_chiplet += 1
        elif chiplet_type == 2:
            num_used_semi_static_chiplet += 1
    print("num_used_static_chiplet :", num_used_static_chiplet)
    print("num_used_semi_static_chiplet :", num_used_semi_static_chiplet)
    
    # Only for adapter-inf, mark the static chip (with learned weight) to 1 in static_chip_learned_list
    num_used_static_chip_learned = 0
    static_chip_learned_list = [0] * num_used_static_chiplet
    for chiplet_idx in range(len(chiplet_layers)):
        for layer_idx in chiplet_layers[chiplet_idx]:
            if net_structure[layer_idx][6] == 0 and (net_structure_layer_def[layer_idx] in ('adapter 1-1,','adapter 1-2,','adapter 2-1,','adapter 2-2,','output weight projection,')):
                static_chip_learned_list[chiplet_idx] = 1
    print("static_chip_learned_list:",static_chip_learned_list)
    num_used_static_chip_learned = sum(static_chip_learned_list)
    print("num_used_static_chip_learned :",num_used_static_chip_learned)

    # update each dynamic layer's beginning chiplet from -1 to the first dynamic chiplet.
    for i in range(len(layer_location_begin_chiplet)):
        if layer_location_begin_chiplet[i] == -1:
            layer_location_begin_chiplet[i] = num_used_chiplet  # update the begin chiplet idx of ith layer
    print("layer_location_begin_chiplet:",layer_location_begin_chiplet)

    chiplet_availability = np.array(chiplet_availability[:num_used_chiplet])
    chiplet_availability_ratio = np.zeros(num_used_chiplet)
    chiplet_availability_ratio[:num_used_static_chiplet] = chiplet_availability[:num_used_static_chiplet] / (config.static_chiplet_height * config.static_chiplet_width)
    chiplet_availability_ratio[num_used_static_chiplet:num_used_chiplet] = chiplet_availability[num_used_static_chiplet:num_used_chiplet] / (config.semistatic_chiplet_height * config.semistatic_chiplet_width)
    
    return chiplet_layers, chiplet_availability_ratio, num_used_chiplet, num_used_static_chiplet, num_used_semi_static_chiplet, chiplet_static_type, layer_location_begin_chiplet

def get_dest_layers(config,net_structure,netStructure_layer_def):
    num_T_head = config.num_T_head
    if any(keyword in config.model_filename for keyword in ("Transformer_inf", "BERT_base_inf","BERT_small_inf")):
        num_layers_per_T_layer = 3+ num_T_head*2 +3
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
        for layer in range(len(net_structure)):
            # generate K,Q
            if ((layer % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or (layer % num_layers_per_T_layer == 1):
                for head in range(num_T_head):
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if (layer % num_layers_per_T_layer == 2):
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==0):
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==1):
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-3)
            # head concat, ff1
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-3) or (layer % num_layers_per_T_layer == num_layers_per_T_layer-2):
                dest_layers[layer].append(layer+1)
            # ff2, then to next Transformer layer or final output classification
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-1):
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if (layer % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)
    
    # if any(keyword in config.model_filename for keyword in ("Gpt2_inf")):
    if config.model_filename.startswith("Gpt2_inf"):
        num_layers_per_T_layer = 3+ num_T_head*2 +3 # w/ head concat layer
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
        for layer in range(len(net_structure)):
            # generate K,Q
            if ((layer % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or (layer % num_layers_per_T_layer == 1):
                for head in range(num_T_head):
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if (layer % num_layers_per_T_layer == 2):
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==0):
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==1):
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-2)
            # ff1
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-2):
                dest_layers[layer].append(layer+1)
            # ff2, then to next Transformer layer or final output classification
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-1):
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if (layer % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)   
    
    # if any(keyword in config.model_filename for keyword in ("DeiT_inf")):
    if config.model_filename.startswith("DeiT_inf"):
        num_layers_per_T_layer = 3+ num_T_head*2 +3
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
        for layer in range(len(net_structure)):
            #generate token
            if (layer == 0):
                dest_layers[layer].append(layer+1)
            # generate K,Q
            if (((layer-1) % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or ((layer-1) % num_layers_per_T_layer == 1):
                for head in range(num_T_head):
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if ((layer-1) % num_layers_per_T_layer == 2):
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= (((layer-1) % num_layers_per_T_layer)-3)/2 <num_T_head) and ( (((layer-1) % num_layers_per_T_layer)-3)%2 ==0):
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= (((layer-1) % num_layers_per_T_layer)-3)/2 <num_T_head) and ( (((layer-1) % num_layers_per_T_layer)-3)%2 ==1):
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-3)
            # head concat, ff1
            if ((layer-1) % num_layers_per_T_layer == num_layers_per_T_layer-3) or ((layer-1) % num_layers_per_T_layer == num_layers_per_T_layer-2):
                dest_layers[layer].append(layer+1)
            # ff2, then to next Transformer layer or final output classification
            if ((layer-1) % num_layers_per_T_layer == num_layers_per_T_layer-1):
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if ((layer-1) % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)
    
    elif any(keyword in config.model_filename for keyword in ("Transformer_adapter_inf", "BERT_base_adapter_inf","BERT_small_adapter_inf")):
        num_layers_per_T_layer = 3+ num_T_head*2 +3 +4
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
        for layer in range(len(net_structure)):
            # generate K,Q
            if ((layer % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or (layer % num_layers_per_T_layer == 1):
                for head in range(num_T_head):
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if (layer % num_layers_per_T_layer == 2):
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==0):
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==1):
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-7)
            # head concat, adapter1-1,adapter1-2,ff1,ff2,adapter2-1,adapter2-2,
            if ( num_layers_per_T_layer-7 <= layer % num_layers_per_T_layer <= num_layers_per_T_layer-1):
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if (layer % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)
    
    elif any(keyword in config.model_filename for keyword in ("Transformer_adapter_cl", "BERT_base_adapter_cl","BERT_small_adapter_cl")):
        
        match = re.search(r'_(\d+)layer', config.model_filename)
        if match:
            T_layer = int(match.group(1))
        else:
            print("No match for T_layer found")
        
        fp_num_layers_per_T_layer = 3+ num_T_head*2 +3 +4
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))]
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))]
        
        for layer in range(len(net_structure)):
            # if src layer is from FP:
            if 'FP' in netStructure_layer_def[layer]:
                # FP: generate K
                if (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] == 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer
                        dest_layers[layer].append(output_dest_layer)

                # FP: generate Q
                elif (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] != 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP
                        bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:Q,']
                        bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head +head]

                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: generate V
                elif (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] != 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] != 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 2+head*2 + layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP
                        bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:V,']
                        bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head +head]

                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: K.QT        
                elif netStructure_layer_def[layer] == 'FP:K.Q,':
                    # to fp
                    dest_layers[layer].append(layer+1)
                
                # FP: K.QT * V
                elif netStructure_layer_def[layer] == 'FP:KQT softmax * V,':
                    # to FP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:head concat,']
                    out_dest_layer = min(index for index in indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: FP:head concat
                
                # FP: head concat
                elif netStructure_layer_def[layer] == 'FP:head concat,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: adapter1-1
                elif netStructure_layer_def[layer] == 'FP:adapter 1-1,':
                    # to FP
                    output_dest_layer = layer+1
                    dest_layers[layer].append(output_dest_layer)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: adapter1-2
                elif netStructure_layer_def[layer] == 'FP:adapter 1-2,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: ff1
                elif netStructure_layer_def[layer] == 'FP:ff1,':
                    # to FP
                    dest_layers[layer].append(layer+1)

                # FP: ff2
                elif netStructure_layer_def[layer] == 'FP:ff2,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: adapter2-1
                elif netStructure_layer_def[layer] == 'FP:adapter 2-1,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: adapter2-2
                elif netStructure_layer_def[layer] == 'FP:adapter 2-2,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]

                # FP: output weight projection
                elif netStructure_layer_def[layer] == 'FP:output weight projection,':
                    # to BP
                    bp_dest_layer = layer+1
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][0] * net_structure[bp_dest_layer][1] # to: W Gradient:weight_outputProjection
                    # to BP
                    bp_dest_layer = layer+2
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3] # to: BP:weight_outputProjection
                    
            # if src layer is from BP:
            elif 'BP' in netStructure_layer_def[layer] or 'W Gradient' in netStructure_layer_def[layer]:
                
                # W Gradient:weight_outputProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_outputProjection,']:
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:output weight projection,'] # should only have 1 element
                    dest_layers[layer].append(indexes[0]) # to: FP:output weight projection
                
                # BP:weight_outputProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_outputProjection,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_ff2
                    dest_layers[layer].append(layer+2) # to: W Gradient:weight_ff2
                
                # BP:weight_adapter2-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-2,']:
                    dest_layers[layer].append(layer+2) # to: BP:weight_adapter2-1
                    dest_layers[layer].append(layer+3) # to: W Gradient:weight_adapter2-1
                
                # W Gradient:weight_adapter2-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-2,']:
                    if layer in indexes:
                        fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:adapter 2-2,']

                        out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                        dest_layers[layer].append(out_dest_layer) # to: FP:adapter 2-2
                
                # BP:weight_adapter2-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-1,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_ff2
                
                # W Gradient:weight_adapter2-1
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-1,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:adapter 2-1,']

                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:adapter 2-1

                # BP:weight_ff2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff2,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_ff1
                
                # BP:weight_ff1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff1,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_adapter1-2
                    dest_layers[layer].append(layer+2) # to: W Gradient:weight_adapter1-2
                
                # BP:weight_adapter1-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-2,']:
                    dest_layers[layer].append(layer+2) # to: BP:weight_adapter1-1
                    dest_layers[layer].append(layer+3) # to: W Gradient:weight_adapter1-1
                
                # W Gradient:weight_adapter1-2
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-2,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:adapter 1-2,']

                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:adapter 1-2
                
                # BP:weight_adapter1-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-1,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_headConcat
                
                # W Gradient:weight_adapter1-1
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-1,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:adapter 1-1,']

                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:adapter 1-1

                # BP:weight_headConcat
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headConcat,'] and layer != max([i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headConcat,']):
                    for head in range(num_T_head):
                        dest_layers[layer].append(layer+1 + head*2) # to: BP:V
                
                # BP:V
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:V,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    dest_layers[layer].append(layer+1) # to: BP:Q
                
                # BP:Q
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:Q,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    kProjection_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,']
                    out_dest_layer = min(index for index in kProjection_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: BP:weight_kProjection
                
                # BP:weight_kProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,'] and (layer != len(net_structure)-1):
                    dest_layers[layer].append(layer+1) # to: BP:weight_adapter2-2
                    dest_layers[layer].append(layer+2) # to: W Gradient:weight_adapter2-2
    
    elif any(keyword in config.model_filename for keyword in ("Transformer_ft", "BERT_base_ft","BERT_small_ft")):
        match = re.search(r'_(\d+)layer', config.model_filename)
        if match:
            T_layer = int(match.group(1))
        else:
            print("No match for T_layer found")
        
        fp_num_layers_per_T_layer = 3+ num_T_head*2 +3
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))]
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))]
        
        for layer in range(len(net_structure)):
            # if src layer is from FP:
            if 'FP' in netStructure_layer_def[layer]:
                # FP: generate K
                if (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] == 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP 
                        bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:K,']
                        bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head +head]

                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                    # to BP
                    bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,']
                    
                    idx = T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer)
                    if idx < len(bp_indexes): 
                        bp_dest_layer = bp_indexes[idx]
                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: generate Q
                elif (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] != 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP
                        bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:Q,']
                        bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head +head]

                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                    # to BP
                    bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_qProjection,']
                    
                    idx = T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer)
                    if idx < len(bp_indexes): 
                        bp_dest_layer = bp_indexes[idx]
                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: generate V
                elif (netStructure_layer_def[layer] == 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+1] != 'FP:K,Q,V projection,') and (netStructure_layer_def[layer+2] != 'FP:K,Q,V projection,'):
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 2+head*2 + layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP
                        bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:V,']
                        bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head +head]

                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                    # to BP
                    bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_vProjection,']
                    
                    idx = T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer)
                    if idx < len(bp_indexes): 
                        bp_dest_layer = bp_indexes[idx]
                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: K.QT        
                elif netStructure_layer_def[layer] == 'FP:K.Q,':
                    # to fp
                    dest_layers[layer].append(layer+1)
                
                # FP: K.QT * V
                elif netStructure_layer_def[layer] == 'FP:KQT softmax * V,':
                    # to FP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:head concat,']
                    out_dest_layer = min(index for index in indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: FP:head concat
                    # to BP
                    # for head in range(num_T_head):
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:KQT softmax * V,']
                    pos_fp = fp_indexes.index(layer)
                    
                    bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:A,']
                    bp_dest_layer = bp_indexes[(T_layer -1 - math.floor(layer / fp_num_layers_per_T_layer))*num_T_head + (T_layer -1 - pos_fp %  num_T_head)]

                    to_bp_dest_layers[layer].append(bp_dest_layer) 
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: head concat
                elif netStructure_layer_def[layer] == 'FP:head concat,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_ff1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headConcat,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: ff1
                elif netStructure_layer_def[layer] == 'FP:ff1,':
                    # to FP
                    output_dest_layer = layer+1
                    dest_layers[layer].append(output_dest_layer)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_ff2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: ff2
                elif netStructure_layer_def[layer] == 'FP:ff2,':
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    if (layer == max([i for i, item in enumerate(netStructure_layer_def) if item == 'FP:ff2,'])):
                        indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_outputProjection,'] # should only have 1 element
                        bp_dest_layer = indexes[0]
                        to_bp_dest_layers[layer].append(bp_dest_layer)
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    else:
                        indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_kProjection,' or item == 'W Gradient:weight_qProjection,' or item == 'W Gradient:weight_vProjection,']
                        if (T_layer -1 - math.ceil(layer / fp_num_layers_per_T_layer)>=0):
                            bp_idx = T_layer -1 - math.ceil(layer / fp_num_layers_per_T_layer)

                            bp_dest_layer = indexes[bp_idx*3]
                            to_bp_dest_layers[layer].append(bp_dest_layer)
                            num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]

                            bp_dest_layer = indexes[bp_idx*3 +1]
                            to_bp_dest_layers[layer].append(bp_dest_layer)
                            num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]

                            bp_dest_layer = indexes[bp_idx*3 +2]
                            to_bp_dest_layers[layer].append(bp_dest_layer)
                            num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: output weight projection
                elif netStructure_layer_def[layer] == 'FP:output weight projection,':
                    # to BP
                    bp_dest_layer = layer+1
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][0] * net_structure[bp_dest_layer][1] # to: W Gradient:weight_outputProjection
                    # to BP
                    bp_dest_layer = layer+2
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3] # to: BP:weight_outputProjection
            
            # if src layer is from BP:
            elif 'BP' in netStructure_layer_def[layer] or 'W Gradient' in netStructure_layer_def[layer]:
                
                # W Gradient:weight_outputProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_outputProjection,']:
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:output weight projection,'] # should only have 1 element
                    dest_layers[layer].append(indexes[0]) # to: FP:output weight projection
                
                # BP:weight_outputProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_outputProjection,']:
                    dest_layers[layer].append(layer+1) # to: BP:weight_ff2
                    dest_layers[layer].append(layer+2) # to: W Gradient:weight_ff2
                
                # BP:weight_ff2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff2,']:
                    dest_layers[layer].append(layer+2) # to: BP:weight_ff1
                    dest_layers[layer].append(layer+3) # to: W Gradient:weight_ff1 
                    
                # W Gradient:weight_ff2
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_ff2,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:ff2,']

                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:ff2
                
                # BP:weight_ff1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff1,']:
                    dest_layers[layer].append(layer+2) # to: BP:weight_headConcat
                    dest_layers[layer].append(layer+3) # to: W Gradient:weight_headConcat
                    
                # W Gradient:weight_ff1
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_ff1,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:ff1,']
                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:ff1
                
                # BP:weight_headConcat
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headConcat,']:
                    for head in range(num_T_head):
                        dest_layers[layer].append(layer+2 + head*4) # to: BP:V
                        dest_layers[layer].append(layer+3 + head*4) # to: BP:A'
                
                # W Gradient:weight_headConcat
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_headConcat,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:head concat,']
                    out_dest_layer = fp_indexes[T_layer -1 - (indexes.index(layer))]
                    dest_layers[layer].append(out_dest_layer) # to: FP:head concat
                    
         
                # BP:V
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:V,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    dest_layers[layer].append(layer+2) # to: BP:K
                    dest_layers[layer].append(layer+3) # to: BP:Q
                
                # BP:A
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:A,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    vProjection_bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_vProjection,']
                    out_dest_layer = min(index for index in vProjection_bp_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: BP:weight_vProjection

                    vProjection_wg_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_vProjection,']
                    out_dest_layer = min(index for index in vProjection_wg_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: W Gradient:weight_vProjection
                
                # BP:K
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:K,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    qProjection_bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_qProjection,']
                    out_dest_layer = min(index for index in qProjection_bp_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: BP:weight_qProjection

                    qProjection_wg_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_qProjection,']
                    out_dest_layer = min(index for index in qProjection_wg_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: W Gradient:weight_qProjection
                
                # BP:Q
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:Q,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    kProjection_bp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,']
                    out_dest_layer = min(index for index in kProjection_bp_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: BP:weight_kProjection

                    kProjection_wg_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_kProjection,']
                    out_dest_layer = min(index for index in kProjection_wg_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer) # to: W Gradient:weight_kProjection
                
                # BP:weight_vProjection
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_vProjection,']
                if layer in indexes and (layer != len(net_structure)-3):
                    dest_layers[layer].append(layer+6) # to: BP:weight_ff2
                    dest_layers[layer].append(layer+7) # to: W Gradient:weight_ff2
                
                # W Gradient:weight_vProjection
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_vProjection,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:K,Q,V projection,']
                    out_dest_layer = fp_indexes[(T_layer -1 - (indexes.index(layer)))*3 +2]
                    dest_layers[layer].append(out_dest_layer) # to: FP:K,Q,V projection (V)
                
                # BP:weight_qProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_qProjection,'] and (layer != len(net_structure)-2):
                    dest_layers[layer].append(layer+4) # to: BP:weight_ff2
                    dest_layers[layer].append(layer+5) # to: W Gradient:weight_ff2
                
                # W Gradient:weight_qProjection
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_qProjection,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:K,Q,V projection,']
                    out_dest_layer = fp_indexes[(T_layer -1 - (indexes.index(layer)))*3 +1]
                    dest_layers[layer].append(out_dest_layer) # to: FP:K,Q,V projection (Q)
                    
                
                # BP:weight_kProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,'] and (layer != len(net_structure)-1):
                    dest_layers[layer].append(layer+2) # to: BP:weight_ff2
                    dest_layers[layer].append(layer+3) # to: W Gradient:weight_ff2
                
                # W Gradient:weight_kProjection
                # to FP
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_kProjection,']
                if layer in indexes:
                    fp_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'FP:K,Q,V projection,']
                    out_dest_layer = fp_indexes[(T_layer -1 - (indexes.index(layer)))*3 +0]
                    dest_layers[layer].append(out_dest_layer) # to: FP:K,Q,V projection (K)
    
    return dest_layers, to_bp_dest_layers, num_to_bp_transfer_byte_to_layer

def generate_chip2chip_num_bit(config,num_used_chiplets, num_used_static_chiplet_all_layers, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer):
    
    num_bits_nop_eachLayer = [[0 for _ in range(len(dest_layers))] for _ in range(len(dest_layers))]
    num_bits_src_chip_to_dest_chip = [[0 for _ in range(num_used_chiplets)] for _ in range(num_used_chiplets)]
    
    # loop: src_layer, find if the dest_layers of each src_layer need NoP
    for layer_idx in range(len(num_chiplet_eachLayer)):
        # print("layer_idx:",layer_idx)
        for dest_layer in dest_layers[layer_idx]:
            
            # if the src_layer_begin_chip and dest_layer_begin_chip are not on same chip -> need NoP, or 
            # if src_layer_begin_chip and dest_layer_begin_chip are on same chip, and src_layer and dest_layer are both dynamic layers, and two layers need diff num of chips -> need NoP
            if (dest_layer < len(layer_location_begin_chiplet) and
                dest_layer < len(num_chiplet_eachLayer)) and (
                (layer_location_begin_chiplet[dest_layer] != layer_location_begin_chiplet[layer_idx]) |
                ((layer_location_begin_chiplet[dest_layer] == num_used_static_chiplet_all_layers) and
                (layer_location_begin_chiplet[layer_idx] == num_used_static_chiplet_all_layers) and
                (num_chiplet_eachLayer[layer_idx] != num_chiplet_eachLayer[dest_layer]))
            ):

                trace = np.array([[0,0,0]])
                
                num_src_chiplet = num_chiplet_eachLayer[layer_idx]
                num_dst_chiplet = num_chiplet_eachLayer[dest_layer]
                
                src_chiplet_begin = layer_location_begin_chiplet[layer_idx]
                src_chiplet_end = src_chiplet_begin + num_src_chiplet - 1
                
                dst_chiplet_begin = layer_location_begin_chiplet[dest_layer]
                dst_chiplet_end = dst_chiplet_begin + num_dst_chiplet - 1
                
                num_bits_per_chiplet = math.ceil(num_in_eachLayer[dest_layer]*config.BitWidth_in/(num_src_chiplet*num_dst_chiplet))
                
                num_bits_nop_eachLayer[layer_idx][dest_layer] += num_in_eachLayer[dest_layer]*config.BitWidth_in

                for dest_chiplet_idx in range(dst_chiplet_begin, dst_chiplet_end+1):
                    for src_chiplet_idx in range(src_chiplet_begin, src_chiplet_end+1):
                        # trace = [trace; src_chiplet_idx-1 dest_chiplet_idx-1 timestamp]
                        if src_chiplet_idx != dest_chiplet_idx: 
                            # if src_chip is dest_chip, then no need for nop
                            trace = np.append(trace, [[src_chiplet_idx, dest_chiplet_idx, num_bits_per_chiplet]], axis=0)
    
                            # # get a two-dimension list: num_bits of every src_chip to every dest_chip
                            num_bits_src_chip_to_dest_chip[src_chiplet_idx][dest_chiplet_idx] += num_bits_per_chiplet
                            
                trace = np.delete(trace, 0, 0)
    return num_bits_nop_eachLayer, num_bits_src_chip_to_dest_chip