import pandas as pd
import math

model_layer = 12
head = 12
token_len = 128
dim = 512
dim_ff = dim*4
dim_head = math.ceil(dim/head)
dim_ada = 32
dim_out = 2 # final classification
num_onelayer_row = 3+ head*2 +3 +4
num_file_row = num_onelayer_row * model_layer +1 # +1: final output weight after all layers
model_type = 'BERT_base_adapter_inf' #'BERT_small_adapter_inf','BERT_base_adapter_inf'
# Define the first line of customization
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

# Initialize an empty list for storing all rows
data = [first_row]

# each row: [0]input token length, [1]input hidden dim, [2]weight hidden dim height, [3]weight hidden dim width, 
#           [4]weight hidden dim height, [5]weight hidden dim width, [6]static(0)/dynamic(1)/semi-dynamic(2), [7]followed w/ softmax(1) or not(0), [8] operation description
for i in range(1, num_file_row+1):
    if ((i%num_onelayer_row == 1 and i != num_file_row) or i%num_onelayer_row == 2 or i%num_onelayer_row == 3):  # K,Q,V projection
        row = [token_len, dim, dim, dim, token_len, dim, 0, 0, "K,Q,V projection,"]
    elif ((3 < i%num_onelayer_row < num_onelayer_row-6) and (i%2 == 0)):  # KQ softmax
        row = [token_len, dim_head, dim_head, token_len, token_len, token_len, 1, 1, "K.Q,"]
    elif ((3 < i%num_onelayer_row < num_onelayer_row-6) and (i%2 == 1)):  # KQT softmax * V
        row = [token_len, token_len, token_len, dim_head, token_len, dim_head, 1, 0, "KQT softmax * V,"]
    elif (i%num_onelayer_row == num_onelayer_row-6):  # head concat
        row = [token_len, dim, dim, dim, token_len, dim, 0, 0, "head concat,"]
    elif (i%num_onelayer_row == num_onelayer_row-5):  # adapter 1-1
        row = [token_len, dim, dim, dim_ada, token_len, dim_ada, 0, 0, "adapter 1-1,"]
    elif (i%num_onelayer_row == num_onelayer_row-4):  # adapter 1-2
        row = [token_len, dim_ada, dim_ada, dim, token_len, dim, 0, 0, "adapter 1-2,"]
    elif (i%num_onelayer_row == num_onelayer_row-3):  # ff1
        row = [token_len, dim, dim, dim_ff, token_len, dim_ff, 0, 0, "ff1,"]
    elif (i%num_onelayer_row == num_onelayer_row-2):  # ff2
        row = [token_len, dim_ff, dim_ff, dim, token_len, dim, 0, 0, "ff2,"]
    elif (i%num_onelayer_row == num_onelayer_row-1):  # adapter 2-1
        row = [token_len, dim, dim, dim_ada, token_len, dim_ada, 0, 0, "adapter 2-1,"]
    elif (i%num_onelayer_row == 0 and i !=0):  # adapter 2-2
        row = [token_len, dim_ada, dim_ada, dim, token_len, dim, 0, 0, "adapter 2-2,"]
    elif (i%num_onelayer_row == 1 and i == num_file_row):  # final output weight projection
        row = [token_len, dim, dim, dim_out, token_len, dim_out, 0, 1, "output weight projection,"]
    data.append(row)

df = pd.DataFrame(data)

df.iloc[1:, :-1] = df.iloc[1:, :-1].astype(int)

# Saved as a new CSV file
output_file_path = 'models/' + model_type + '_' + str(model_layer) + 'layer' + '_' + str(head) + 'head' + '_' + str(token_len) + 'token' + '.csv'
df.to_csv(output_file_path, index=False, header=False)

print(f"New file generated: {output_file_path}")