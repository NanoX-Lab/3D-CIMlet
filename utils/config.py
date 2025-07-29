import csv,sys,re,os
import math

class Config:
	def __init__(self):
		self.model_filename = os.path.join('models', 'BERT_base_adapter_cl_semi_static_12layer_12head_128token.csv')
		self.net_name = os.path.splitext(os.path.basename(self.model_filename))[0]
		self.num_T_head = int(re.findall(r'(\d+)head', self.model_filename)[0])
		self.train_batch_size = 16
		self.train_pipeline_parallel = 0
		self.NetStructure = []
		self.NetStructure_layer_def = []
		self.clk_freq = 800e6
		self.eDRAM_clk_freq = 200e6
		self.RRAM_clk_freq = 800e6
		self.nop_clk_freq_2d = 12.5E09 
		self.nop_clk_freq_3d = 0.2E09 
		self.nop_clk_freq_2_5d = 32.75E09
		self.Packaging_dimension = 3 # 2, 2.5, 3
		self.pitch_size_2_5d = 40E-06 
		self.pitch_size_3d = 9E-06

		self.ebit_2d = 6.6e-12
		self.ebit_2_5d = 0.26e-12
		self.ebit_3d = 0.015e-12

		self.semistatic_chip_sram_buffer_ratio = 1/math.pow(2,4) # pow(2,4), pow(2,6), pow(2,8), pow(2,10), pow(2,12)

		# eDRAM calibrated data, cell size include peripheral

		self.eDRAM_cell_size_14nm = 5.60E-14
		self.eDRAM_read_energy_per_bit_14nm = 1.72E-18
		self.eDRAM_write_energy_per_bit_14nm = 1.81E-18
		self.eDRAM_refresh_power_per_bit_14nm = 1.93E-10
		self.eDRAM_refresh_retention_time_14nm = 5.39E-05

		self.eDRAM_cell_size_16nm = 8.00E-14
		self.eDRAM_read_energy_per_bit_16nm = 2.46E-18
		self.eDRAM_write_energy_per_bit_16nm = 2.58E-18
		self.eDRAM_refresh_power_per_bit_16nm = 2.76E-10
		self.eDRAM_refresh_retention_time_16nm = 7.70E-05

		self.eDRAM_cell_size_22nm = 2.42E-13
		self.eDRAM_read_energy_per_bit_22nm = 7.89E-16
		self.eDRAM_write_energy_per_bit_22nm = 1.58E-15
		self.eDRAM_refresh_power_per_bit_22nm = 4.73E-07
		self.eDRAM_refresh_retention_time_22nm = 1.09E-04

		self.eDRAM_cell_size_28nm = 3.46E-13
		self.eDRAM_read_energy_per_bit_28nm = 1.13E-15
		self.eDRAM_write_energy_per_bit_28nm = 2.25E-15 
		self.eDRAM_refresh_power_per_bit_28nm = 6.76E-07
		self.eDRAM_refresh_retention_time_28nm = 1.55E-04

		self.eDRAM_cell_size_40nm = 1.76E-12
		self.eDRAM_read_energy_per_bit_40nm = 5.00E-14
		self.eDRAM_write_energy_per_bit_40nm = 1.00E-13
		self.eDRAM_refresh_power_per_bit_40nm = 3.00E-05
		self.eDRAM_refresh_retention_time_40nm = 2.00E-05

		self.eDRAM_cell_size_65nm = 1.96E-12
		self.eDRAM_read_energy_per_bit_65nm = 1.88E-12
		self.eDRAM_write_energy_per_bit_65nm = 3.75E-12
		self.eDRAM_refresh_power_per_bit_65nm = 1.13E-03
		self.eDRAM_refresh_retention_time_65nm = 4.00E-05

		self.eDRAM_cell_size_130nm = 4.19E-12
		self.eDRAM_read_energy_per_bit_130nm = 1.88E-12
		self.eDRAM_write_energy_per_bit_130nm = 3.75E-12
		self.eDRAM_refresh_power_per_bit_130nm = 1.13E-03
		self.eDRAM_refresh_retention_time_130nm = 4.00E-05

		# RRAM calibrated data, cell size include peripheral
		self.RRAM_cell_size_40nm = 6.34e04 * 1e-12 / (256*256)
		self.RRAM_read_energy_per_bit_40nm = 0.14e-12
		self.RRAM_write_energy_per_bit_40nm = 2.3e-12
		self.RRAM_refresh_power_per_bit_40nm = 0
		self.RRAM_refresh_retention_time_40nm = 1e6

		self.RRAM_cell_size_130nm = 3.03 * 1e-6 / (0.0625*1e6)
		self.RRAM_read_energy_per_bit_130nm = 1.36e-12
		self.RRAM_write_energy_per_bit_130nm = 10e-12
		self.RRAM_refresh_power_per_bit_130nm = 0
		self.RRAM_refresh_retention_time_130nm = 1e6
		

		# -----subarray-----
		self.static_subarray_height = 256 # num of cell rows in a subarray
		self.static_subarray_width = 256 # num of cell cols in a subarray
		self.static_subarray_size = self.static_subarray_height * self.static_subarray_width
		self.semistatic_subarray_height = 256 # num of cell rows in a subarray
		self.semistatic_subarray_width = 256 # num of cell cols in a subarray
		self.dynamic_subarray_height = 128 # num of cell rows in a subarray
		self.dynamic_subarray_width = 128 # num of cell cols in a subarray
		self.dynamic_subarray_size = self.dynamic_subarray_height * self.dynamic_subarray_width

		self.subarray_readout_mux = 8

		# -----pe-----
		self.static_pe_height = 8 # num of subarray rows in a pe
		self.static_pe_width = 8 # num of subarray cols in a pe
		self.static_pe_size = self.static_pe_height * self.static_pe_width
		self.semistatic_pe_height = 16 # num of subarray rows in a pe
		self.semistatic_pe_width = 8 # num of subarray cols in a pe
		self.dynamic_pe_height = 8 # num of subarray rows in a pe
		self.dynamic_pe_width = 8 # num of subarray cols in a pe
		self.dynamic_pe_size = self.dynamic_pe_height * self.dynamic_pe_width

		# -----chiplet-----
		# -----static chiplet-----
		self.static_chiplet_technode = 40 # 40, 130
		self.static_chiplet_memory_cell_type = 'RRAM'
		self.num_static_chiplet = 500
		self.static_chiplet_height = 4 # num of PE rows in a chiplet
		self.static_chiplet_width = 4 # num of PE cols in a chiplet
		self.static_chiplet_size = self.static_chiplet_height * self.static_chiplet_width
  
		# -----dynamic chiplet-----
		self.dynamic_chiplet_technode = 14 # 14,16,22,28,40,65,130
		self.dynamic_chiplet_memory_cell_type = 'eDRAM'
		self.num_dynamic_chiplet = 100
		self.dynamic_chiplet_height = 1 # num of PE rows in a chiplet
		self.dynamic_chiplet_width = 1 # num of PE cols in a chiplet
		self.dynamic_chiplet_size = self.dynamic_chiplet_height * self.dynamic_chiplet_width
  
		# -----semistatic chiplet-----
		self.semistatic_chiplet_technode = 40 # 14,16,22,28,40,65,130
		self.semistatic_chiplet_memory_cell_type = 'eDRAM'
		self.semistatic_chiplet_height = 4 # num of PE rows in a chiplet
		self.semistatic_chiplet_width = 8 # num of PE cols in a chiplet
		
		# -----logic chiplet-----
		self.logic_chiplet_technode = 40
		self.global_buffer_core_height = 128 # global buffer only in logic chiplet
		self.global_buffer_core_width = 128 # global buffer only in logic chiplet
		self.chip_buffer_core_height = 128
		self.chip_buffer_core_width = 128
		self.pe_buffer_core_height = 32 
		self.pe_buffer_core_width = 32

		self.BitWidth_in = 8
		self.BitWidth_weight = 8

		self.pe_bus_width_2D = 256
		self.chiplet_bus_width_2D = 32
		self.scale_noc = 10000 # used in booksim, change to a larger number if NOC simulation is slow.
		self.scale_nop = 100 # used in booksim, change to a larger number if NOP simulation is slow.
		
		AR = 0
		Rho = 0
		self.wireWidth = 0 
		memcelltype = 'RRAM' 
		accesstype = 1  
		self.temp = 300   # Temperature (K)
		self.technode = 22 
		self.featureSize = 40e-9    # Wire width for subArray simulation

		heightInFeatureSizeSRAM = 10  
		widthInFeatureSizeSRAM = 10   
		heightInFeatureSize1T1R = 10  
		widthInFeatureSize1T1R = 10   
		heightInFeatureSizeCrossbar = 10  
		widthInFeatureSizeCrossbar = 10   

		# Initialize interconnect wires
		if self.technode == 130:
			self.wireWidth = 175
			self.featureSize = 175e-9
			self.vdd = 1.3
			AR = 1.60
			Rho = 2.20e-8
		elif self.technode == 90:
			self.wireWidth = 110
			self.featureSize = 110e-9 
			self.vdd = 1.2
			AR = 1.60
			Rho = 2.52e-8
		elif self.technode == 65:
			self.wireWidth = 105
			self.featureSize = 105e-9
			self.vdd = 1.1
			AR = 1.70
			Rho = 2.68e-8
		elif self.technode == 45:
			self.wireWidth = 80
			self.featureSize = 80e-9 
			self.vdd = 1.0
			AR = 1.70
			Rho = 3.31e-8
		elif self.technode == 40:
			self.wireWidth = 70 
			self.featureSize = 70e-9 
			self.vdd = 0.9
			AR = 1.75 
			Rho = 3.50e-8
		elif self.technode == 32:
			self.wireWidth = 56
			self.featureSize = 56e-9 
			self.vdd = 0.9
			AR = 1.80
			Rho = 3.70e-8
		elif self.technode == 28:
			self.wireWidth = 50 
			self.featureSize = 50e-9 
			self.vdd = 0.9
			AR = 1.80 
			Rho = 3.80e-8 
		elif self.technode == 22:
			self.wireWidth = 40
			self.featureSize = 40e-9 
			self.vdd = 0.85
			AR = 1.90
			Rho = 4.03e-8
		elif self.technode == 16:
			self.wireWidth = 30
			self.featureSize = 30e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.30e-8
		elif self.technode == 14:
			self.wireWidth = 25
			self.featureSize = 25e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.08e-8
		elif self.technode == 10:
			self.vdd = 0.75
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		elif self.technode == 7:
			self.vdd = 0.7
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		else:
			self.wireWidth = -1 # Ignore wire resistance or user define
			print("technode:",self.technode)
			sys.exit("Wire width out of range")

		# get wireLengthRow, wireLengthCol
		heightInFeatureSizeSRAM = 10        # SRAM Cell height in feature size  
		widthInFeatureSizeSRAM = 28        # SRAM Cell width in feature size 
		heightInFeatureSize1T1R = 4        # 1T1R Cell height in feature size
		widthInFeatureSize1T1R = 12         # 1T1R Cell width in feature size
		heightInFeatureSizeCrossbar = 2    # Crossbar Cell height in feature size
		widthInFeatureSizeCrossbar = 2     # Crossbar Cell width in feature size
		
		if memcelltype == 'SRAM':
			wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSizeSRAM
			wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSizeSRAM
		elif memcelltype == 'RRAM':
			if accesstype == 1:
				wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSize1T1R
				wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSize1T1R
			else:
				wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSizeCrossbar
				wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSizeCrossbar
		else: #'eDRAM'
			pass
			

		# get resistance
		Rho *= (1 + 0.00451 * abs(self.temp - 300))
		if self.wireWidth == -1:
			self.unitLengthWireResistance = 1.0  # Use a small number to prevent numerical error
			wireResistanceRow = 0
			wireResistanceCol = 0
		else:
			self.unitLengthWireResistance = Rho / (self.wireWidth * 1e-9 * self.wireWidth * 1e-9 * AR)
			wireResistanceRow = self.unitLengthWireResistance * wireLengthRow
			wireResistanceCol = self.unitLengthWireResistance * wireLengthCol

	def update_params(self, technode):
		if technode == 130:
			self.wireWidth = 175
			self.featureSize = 175e-9
			self.vdd = 1.3
			AR = 1.60
			Rho = 2.20e-8
		elif technode == 90:
			self.wireWidth = 110
			self.featureSize = 110e-9 
			self.vdd = 1.2
			AR = 1.60
			Rho = 2.52e-8
		elif technode == 65:
			self.wireWidth = 105
			self.featureSize = 105e-9
			self.vdd = 1.1
			AR = 1.70
			Rho = 2.68e-8
		elif technode == 45:
			self.wireWidth = 80
			self.featureSize = 80e-9 
			self.vdd = 1.0
			AR = 1.70
			Rho = 3.31e-8
		elif technode == 40:
			self.wireWidth = 70 
			self.featureSize = 70e-9 
			self.vdd = 0.9
			AR = 1.75 
			Rho = 3.50e-8
		elif technode == 32:
			self.wireWidth = 56
			self.featureSize = 56e-9 
			self.vdd = 0.9
			AR = 1.80
			Rho = 3.70e-8
		elif technode == 28:
			self.wireWidth = 50 
			self.featureSize = 50e-9 
			self.vdd = 0.9
			AR = 1.80 
			Rho = 3.80e-8 
		elif technode == 22:
			self.wireWidth = 40
			self.featureSize = 40e-9 
			self.vdd = 0.85
			AR = 1.90
			Rho = 4.03e-8
		elif technode == 16:
			self.wireWidth = 30
			self.featureSize = 30e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.30e-8
		elif technode == 14:
			self.wireWidth = 25
			self.featureSize = 25e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.08e-8
		elif technode == 10:
			self.vdd = 0.75
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		elif technode == 7:
			self.vdd = 0.7
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		else:
			self.wireWidth = -1 # Ignore wire resistance or user define
			print("technode:",technode)
			sys.exit("Wire width out of range")	
	
	def load_model(self):
		try:
			with open(self.model_filename, mode='r', newline='') as file:
				csv_reader = csv.reader(file)
				first_row = next(csv_reader)  # Read the first line to determine the model type
				if any(keyword in self.model_filename for keyword in(
        				"Transformer_inf","Transformer_adapter_inf","Transformer_adapter_cl","Transformer_ft",
                        "BERT_base_inf","Gpt2_inf","Gpt2_inf","DeiT_inf",
                        "BERT_base_adapter_inf","BERT_base_adapter_cl","BERT_small_adapter_inf","BERT_small_adapter_cl",
						"BERT_base_ft")):
					for row in csv_reader:
						row = row[:-1]
						converted_row = [int(item) for item in row]
						self.NetStructure.append(converted_row)  # Add each row to the NetStructure list
			return self.NetStructure
		
		except FileNotFoundError:
			print(f"File '{self.model_filename}' not found.")
		except Exception as e:
			print(f"An error occurred: {str(e)}")
	
	def load_model_layer_def(self):
		try:
			with open(self.model_filename, mode='r', newline='') as file:
				csv_reader = csv.reader(file)
				first_row = next(csv_reader)  # Read the first line to determine the model type
				if any(keyword in self.model_filename for keyword in ("Transformer_inf", "Transformer_adapter_inf", "Transformer_adapter_cl","Transformer_ft",
                "BERT_base_inf","Gpt2_inf","Gpt2_inf","DeiT_inf",
                "BERT_base_adapter_inf","BERT_base_adapter_cl","BERT_small_adapter_inf","BERT_small_adapter_cl",
				"BERT_base_ft")):
					for row in csv_reader:
						row_def = row[-1]
						self.NetStructure_layer_def.append(row_def)  # Add each row to the NetStructure_layer_def list
			return self.NetStructure_layer_def
		
		except FileNotFoundError:
			print(f"File '{self.model_filename}' not found.")
		except Exception as e:
			print(f"An error occurred: {str(e)}")
