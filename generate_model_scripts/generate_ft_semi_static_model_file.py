import pandas as pd
import re

# read original inference file path
file_path = 'BERT_base_inf_12layer_12head_128token.csv' 
df = pd.read_csv(file_path, header=None)

# Use regex to extract the part before "_<number>layer"
match = re.match(r'(.*)_\d+layer', file_path.split('/')[-1])

if match:
    model_type = match.group(1)
    
    # Replace "inf" with "ft"
    new_model_type = model_type.replace("inf", "ft_semi_static")
    
    # Generate the new file path
    output_file_path = file_path.replace(model_type, new_model_type)

# Initialize a new list to store bp data
new_data = []
first_row = ['input token length', 
             'input hidden dim', 
             'weight height',
             'weight hidden width',
             'output height',
             'output width',
             'operation type',
             'followed by softmax',
             'operation description'
             ]
new_data.append(first_row)

# Iterate over the penultimate line of the source file to generate the corresponding new line
# for new generated rows, if weights are stored in dynamic chip, row[6] is 1.
# each row: [0]input token length, [1]input hidden dim, [2]weight hidden dim height, [3]weight hidden dim width, 
#           [4]weight hidden dim height, [5]weight hidden dim width, [6]static(0)/dynamic(1)/semi-dynamic(2), [7]followed w/ softmax(1) or not(0), [8] operation description
for i in range(len(df)):
    # Get the data of the penultimate i+1 row
    row = df.iloc[-(i+1)]
    if (row[8] == "output weight projection,"):
        new_row_1 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_outputProjection,"]
        new_row_2 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_outputProjection,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "ff2,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_ff2,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_ff2,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "ff1,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_ff1,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_ff1,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "head concat,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_headConcat,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_headConcat,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "KQT softmax * V,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:V,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"BP:A,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "K.Q,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:K,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"BP:Q,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "K,Q,V projection,") :
        
        # Wv, which is the 3rd "K,Q,V projection,"
        if (df.iloc[-(i+2)][8] == "K,Q,V projection,") and (df.iloc[-(i+3)][8] == "K,Q,V projection,"):
            if (-(i+1) != -(len(df)-3)):
                new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_vProjection,"]
                new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_vProjection,"]
                new_data.append(new_row_1)
                new_data.append(new_row_2)
            else:
                new_row_1 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_vProjection,"]
                new_data.append(new_row_1)
        
        # Wq, which is the 2nd "K,Q,V projection,"
        elif (df.iloc[-(i+2)][8] == "K,Q,V projection,"):
            if (-(i+1) != -(len(df)-2)):
                new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_qProjection,"]
                new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_qProjection,"]
                new_data.append(new_row_1)
                new_data.append(new_row_2)
            else:
                new_row_1 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_qProjection,"]
                new_data.append(new_row_1)
        
        # Wk, which is the 1st "K,Q,V projection,"
        else:
            if (-(i+1) != -(len(df)-1)):
                new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_kProjection,"]
                new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_kProjection,"]
                new_data.append(new_row_1)
                new_data.append(new_row_2)
            else:
                new_row_1 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_kProjection,"]
                new_data.append(new_row_1)
        
    else:
        continue

bp_df = pd.DataFrame(new_data)
bp_df = bp_df.iloc[1:].reset_index(drop=True) # delete bp_df first row ("model_type,...")

# add "FP:" to 8th term of each row
df.iloc[1:, 8] = df.iloc[1:, 8].apply(lambda x: f"FP:{x}" if isinstance(x, str) else x)
# # Modify all the 6th column (static/dynamic), change to 1 (dynamic)
# df.iloc[1:, 6] = df.iloc[1:].apply(lambda row: 1 if isinstance(row[6], int) else row[6], axis=1)

cl_df = pd.concat([df, bp_df], axis=0, ignore_index=True)
cl_df.to_csv(output_file_path, index=False, header=False)

print(f"New file generated: {output_file_path}")

