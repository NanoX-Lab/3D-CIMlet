import math

class ShiftAdd:
	def __init__(self,config,technode,memory_cell_type,subarray_width):
		self.technode = technode
		self.clk_freq = getattr(config, memory_cell_type + '_clk_freq')
		self.latency = 0
		self.area = 0
		self.latency_per_bit = 0
		self.power_40nm = (270e-6 / 800e8 * self.clk_freq) / 256 * subarray_width
		if self.technode == 130:
			self.power = self.power_40nm * 6.31
		elif self.technode == 90:
			self.power = self.power_40nm * 3.70
		elif self.technode == 65:
			self.power = self.power_40nm * 2.25
		elif self.technode == 45:
			self.power = self.power_40nm * 1.25
		elif self.technode == 40:
			self.power = self.power_40nm
		elif self.technode == 32:
			self.power = self.power_40nm * 7.41E-01
		elif self.technode == 28:
			self.power = self.power_40nm * 6.5E-01
		elif self.technode == 22:
			self.power = self.power_40nm * 4.54E-01
		elif self.technode == 16:
			self.power = self.power_40nm * 3.00E-01
		elif self.technode == 14:
			self.power = self.power_40nm * 2.56E-01
		elif self.technode == 10:
			self.power = self.power_40nm * 1.61E-01
		elif self.technode == 7:
			self.power = self.power_40nm * 9.84E-02
		self.energy_per_bit = self.power / self.clk_freq / subarray_width
	def get_area(self):
		return 0
class Accumulator:
	def __init__(self,config,technode,memory_cell_type='eDRAM',array_width=1024):
		self.technode = technode
		self.clk_freq = getattr(config, memory_cell_type + '_clk_freq')
		self.power = (10e-6/ 800e8 * self.clk_freq) / 256 * array_width
		self.latency = 0
		self.area = 0
		self.latency_per_bit = 0
		self.energy_per_bit = 2.7e-12 # depends on clk_freq
		self.area_22nm = 4.89E-09
	def get_area(self):
		if self.technode == 130:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(130, 2)
		elif self.technode == 90:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(90, 2)
		elif self.technode == 65:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(65, 2)
		elif self.technode == 45:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(45, 2)
		elif self.technode == 40:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(40, 2)
		elif self.technode == 32:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(32, 2)
		elif self.technode == 28:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(28, 2)
		elif self.technode == 22:
			self.area = self.area_22nm
		elif self.technode == 16:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(16, 2)
		elif self.technode == 14:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(14, 2)
		elif self.technode == 10:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(10, 2)
		elif self.technode == 7:
			self.area = self.area_22nm / math.pow(22, 2) * math.pow(7, 2)
		return self.area

class SoftmaxUnit:
	def __init__(self,config,technode,memory_cell_type):
		self.technode = technode
		self.clk_freq = getattr(config, memory_cell_type + '_clk_freq')
		self.latency_per_byte = 7e-7 /512 # input values: 512, 45nm
		self.power_45nm = 8e-3 # input values: 512
		self.energy_per_byte_45nm = self.latency_per_byte * self.power_45nm # depends on clk_freq
		self.energy_per_byte = 0
		self.area_45nm = 3.00E-07 # input values: 512
	def get_area(self):
		if self.technode == 130:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(130, 2)
		elif self.technode == 90:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(90, 2)
		elif self.technode == 65:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(65, 2)
		elif self.technode == 45:
			self.area = self.area_45nm
		elif self.technode == 40:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(40, 2)
		elif self.technode == 32:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(32, 2)
		elif self.technode == 28:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(28, 2)
		elif self.technode == 22:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(22, 2)
		elif self.technode == 16:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(16, 2)
		elif self.technode == 14:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(14, 2)
		elif self.technode == 10:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(10, 2)
		elif self.technode == 7:
			self.area = self.area_45nm / math.pow(45, 2) * math.pow(7, 2)
		return self.area
	def get_energy_per_byte(self):
		if self.technode == 130:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 6.31
		elif self.technode == 90:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 3.70
		elif self.technode == 65:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 2.25
		elif self.technode == 45:
			self.energy_per_byte = self.energy_per_byte_45nm
		elif self.technode == 40:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 1
		elif self.technode == 32:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 7.41E-01
		elif self.technode == 28:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 6.5E-01
		elif self.technode == 22:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 4.54E-01
		elif self.technode == 16:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 3.00E-01
		elif self.technode == 14:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 2.56E-01
		elif self.technode == 10:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 1.61E-01
		elif self.technode == 7:
			self.energy_per_byte = self.energy_per_byte_45nm /1.25 * 9.84E-02
		return self.energy_per_byte

class Buffer: # sram / edram
	def __init__(self,config,technode,memory_type,mem_width=128,mem_height=128):
		self.technode = technode
		config.update_params(technode)
		config.technode = self.technode
		self.featureSize = config.featureSize
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
		self.energy_per_bit = 0 # depends on clk_freq
		self.memory_type = memory_type
		self.mem_width = mem_width
		self.mem_height = mem_height
		self.leak_power_per_cell = 0
		self.bandwidth = self.mem_width * self.clk_freq
	def get_area(self):
		if self.memory_type == 'SRAM':
			if self.technode == 130:
				cellSize = 9.56E-12
			elif self.technode == 65:
				cellSize = 1.48E-12
			elif self.technode == 40:
				cellSize = 8.20E-13
			elif self.technode == 28:
				cellSize = 3.60E-13
			elif self.technode == 22:
				cellSize = 200 * math.pow(self.technode*1e-9, 2)
			elif self.technode == 16:
				cellSize = 300 * math.pow(self.technode*1e-9, 2)
			elif self.technode == 14:
				cellSize = 300 * math.pow(self.technode*1e-9, 2)
			self.area = 1.3* self.mem_width * self.mem_height * cellSize
		elif self.memory_type == 'eDRAM':
			if self.technode == 130:
				cellSize = 4.19E-12
			elif self.technode == 65:
				cellSize = 7.46E-13
			elif self.technode == 40:
				cellSize = 4.30E-13
			elif self.technode == 28:
				cellSize = 2.86E-13
			elif self.technode == 22:
				cellSize = 9.00E-14
			elif self.technode == 16:
				cellSize = 8.00E-14
			elif self.technode == 14:
				cellSize = 5.60E-14
			self.area = 1.3* self.mem_width * self.mem_height * cellSize
		return self.area
	def get_energy_per_bit(self,config):
		if self.memory_type == 'SRAM':
			if self.technode == 130:
				read_energy_per_bit = 4.41E-13
				write_energy_per_bit = 3.66E-13
			elif self.technode == 90:
				read_energy_per_bit = 2.59E-13
				write_energy_per_bit = 1.64E-13
			elif self.technode == 65:
				read_energy_per_bit = 1.58E-13
				write_energy_per_bit = 1.18E-13
			elif self.technode == 45:
				read_energy_per_bit = 9.01E-14
				write_energy_per_bit = 6.37E-14
			elif self.technode == 40:
				read_energy_per_bit = 7E-14
				write_energy_per_bit = 5.7E-14
			elif self.technode == 32:
				read_energy_per_bit = 5.19E-14
				write_energy_per_bit = 3.53E-14
			elif self.technode == 28:
				read_energy_per_bit = 4E-14
				write_energy_per_bit = 3E-14
			elif self.technode == 22:
				read_energy_per_bit = 3.18E-14
				write_energy_per_bit = 2.08E-14
			elif self.technode == 16:
				read_energy_per_bit = 2.10E-14
				write_energy_per_bit = 1.45E-14
			elif self.technode == 14:
				read_energy_per_bit = 1.79E-14
				write_energy_per_bit = 1.26E-14
			elif self.technode == 10:
				read_energy_per_bit = 1.13E-14
				write_energy_per_bit = 8.21E-15
			elif self.technode == 7:
				read_energy_per_bit = 6.89E-15
				write_energy_per_bit = 5.43E-15
		elif self.memory_type == 'eDRAM':
			if self.technode == 130:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_130nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_130nm
			elif self.technode == 65:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_65nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_65nm
			elif self.technode == 40:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_40nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_40nm
			elif self.technode == 28:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_28nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_28nm
			elif self.technode == 22:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_22nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_22nm
			elif self.technode == 16:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_16nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_16nm
			elif self.technode == 14:
				read_energy_per_bit = config.eDRAM_read_energy_per_bit_14nm
				write_energy_per_bit = config.eDRAM_write_energy_per_bit_14nm
		return read_energy_per_bit, write_energy_per_bit
	def get_leak_power(self):
		if self.memory_type == 'SRAM':
			if self.technode == 130:
				self.leak_power_per_cell = 7.00E-11
			elif self.technode == 90:
				self.leak_power_per_cell = 2.05E-11
			elif self.technode == 65:
				self.leak_power_per_cell = 6.45E-12
			elif self.technode == 45:
				self.leak_power_per_cell = 8.54E-12
			elif self.technode == 40:
				self.leak_power_per_cell = 1.03E-12
			elif self.technode == 32:
				self.leak_power_per_cell = 5.46E-12
			elif self.technode == 28:
				self.leak_power_per_cell = 3.00E-13
			elif self.technode == 22:
				self.leak_power_per_cell = 3.55E-12
			elif self.technode == 16:
				self.leak_power_per_cell = 1.30E-12
			elif self.technode == 14:
				self.leak_power_per_cell = 1.00E-12
			elif self.technode == 10:
				self.leak_power_per_cell = 3.56E-12
			elif self.technode == 7:
				self.leak_power_per_cell = 3.33E-12
		elif self.memory_type == 'eDRAM':
			if self.technode == 130:
				self.leak_power_per_cell = 3.85E-10
			elif self.technode == 65:
				self.leak_power_per_cell = 4.88E-10
			elif self.technode == 40:
				self.leak_power_per_cell = 3.78E-10
			elif self.technode == 28:
				self.leak_power_per_cell = 2.20E-10
			elif self.technode == 22:
				self.leak_power_per_cell = 1.54E-10
			elif self.technode == 16:
				self.leak_power_per_cell = 1.05E-10
			elif self.technode == 14:
				self.leak_power_per_cell = 7.35E-11
		leak_power = self.leak_power_per_cell * self.mem_width * self.mem_height
		return leak_power
class Noc:
	def __init__(self,config,technode,chiplet_type):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return 0

class Htree:
	def __init__(self,config,technode, numRow, numCol, busWidth, unitHeight, unitWidth, foldedratio=16):
		self.clk_freq = config.clk_freq
		self.energy = 0
		self.latency = 0
		self.area = 0
		self.technode = technode
		config.update_params(technode)
		config.technode = self.technode
		self.vdd = config.vdd
		self.featureSize = config.featureSize
		self.wireWidth = config.wireWidth
		self.temp = config.temp
		self.numRow = numRow # = pe hight
		self.numCol = numCol # = pe width

		self.busWidth = busWidth # =subarray_height 
		self.unitHeight = unitHeight 
		self.unitWidth = unitWidth 
		self.foldedratio = foldedratio

		self.numStage = 2*math.ceil(math.log2(max(self.numRow, self.numCol)))+1   # vertical has N stage, horizontal has N+1 stage
		unitLengthWireResistance = config.unitLengthWireResistance
		self.unitLengthWireCap = 0.2e-15/1e-6   # 0.2 fF/mm

		#*** define center point ***#
		self.x_center = math.floor(math.log2(min(self.numRow, self.numCol)))
		self.y_center = math.floor(math.log2(min(self.numRow, self.numCol)))
		orc = 1    # over-routing constraint: (important for unbalanced tree) avoid routing outside chip boundray
		
		if (self.numCol-self.x_center < orc): 
			self.x_center -= orc

		if (self.numRow-self.y_center < orc):
			self.y_center -= orc  # redefine center point: try to slightly move to the actual chip center
		
		self.find_stage = 0   # assume the top stage as find_stage = 0
		self.hit = 0
		self.skipVer = 0
		self.totalWireLength = 0
  
		if self.technode == 130:
			# technode=130,featuresize=175e-9,wirewidth=175
			self.minDist = 0.00169359
			self.resOnRep = 51213.8
			self.capInvInput = 1.16469e-13
			self.capInvOutput = 9.6562e-15
			self.wInv = 7.41e-06
			self.hInv = 3.64e-06
		elif self.technode == 90:
			# technode=90,featuresize=110e-9,wirewidth=110
			self.minDist = 0.000633206
			self.resOnRep = 68149
			self.capInvInput = 3.82481e-14
			self.capInvOutput = 6.99952e-15
			self.wInv = 6.498e-06
			self.hInv = 2.52e-06
		elif self.technode == 65:
			# technode=65,featuresize=105e-9,wirewidth=105
			self.minDist = 0.000681535
			self.resOnRep = 74884.6
			self.capInvInput = 4.66195e-14
			self.capInvOutput = 3.48939e-15
			self.wInv = 3.952e-06
			self.hInv = 1.82e-06
		elif self.technode == 45:
			# technode=45,featuresize=80e-9,wirewidth=80
			self.minDist = 0.000367558
			self.resOnRep = 78635.2
			self.capInvInput = 2.44254e-14
			self.capInvOutput = 2.32216e-15
			self.wInv = 2.565e-06
			self.hInv = 1.26e-06
		if self.technode == 40: 
			# technode=40,featuresize=70e-9,wirewidth=70
			self.minDist = 0.00030
			self.resOnRep = 80000
			self.capInvInput = 1.8e-14
			self.capInvOutput = 2.0e-15
			self.wInv = 2.0e-06
			self.hInv = 1.0e-06
		elif self.technode == 32:
			# technode=32,featuresize=56e-9,wirewidth=56
			self.minDist = 0.000199978
			self.resOnRep = 82941.1
			self.capInvInput = 1.29872e-14
			self.capInvOutput = 1.38083e-15
			self.wInv = 1.5808e-06
			self.hInv = 8.96e-07
		elif self.technode == 28:
			# technode=28,featuresize=50e-9,wirewidth=50
			self.minDist = 0.000175
			self.resOnRep = 83800
			self.capInvInput = 1.15e-14
			self.capInvOutput = 1.20e-15
			self.wInv = 1.45e-06
			self.hInv = 8.30e-07
		elif self.technode == 22:
			# technode=22,featuresize=40e-9,wirewidth=40
			self.minDist = 0.000108832
			self.resOnRep = 86357.3
			self.capInvInput = 6.85804e-15
			self.capInvOutput = 7.14011e-16
			self.wInv = 1.0032e-06
			self.hInv = 6.16e-07
		elif self.technode == 16:
			# technode=16,featuresize=30e-9,wirewidth=30
			self.minDist = 6.25839e-05
			self.resOnRep = 63262.7
			self.capInvInput = 4.81607e-15
			self.capInvOutput = 5.27723e-16
			self.wInv = 6.87e-07
			self.hInv = 5.04e-07
		elif self.technode == 14:
			# technode=14,featuresize=25e-9,wirewidth=25
			self.minDist = 4.21745e-05
			self.resOnRep = 40168.1
			self.capInvInput = 2.77409e-15
			self.capInvOutput = 3.41535e-16
			self.wInv = 3.71e-07
			self.hInv = 3.92e-07
		elif self.technode == 10:
			# technode=10,featuresize=18e-9,wirewidth=18
			self.minDist = 2.44525e-05
			self.resOnRep = 35326.8
			self.capInvInput = 1.69542e-15
			self.capInvOutput = 1.23934e-16
			self.wInv = 2.12e-07
			self.hInv = 2.8e-07
		elif self.technode == 7:
			# technode=7,featuresize=18e-9,wirewidth=18
			self.minDist = 2.23175e-05
			self.resOnRep = 28330.8
			self.capInvInput = 1.4951e-15
			self.capInvOutput = 1.16067e-16
			self.wInv = 1.113e-07
			self.hInv = 1.96e-07

	
	def get_area(self):
		wInv=self.wInv
  
		MAX_TRANSISTOR_HEIGHT = 28
		MAX_TRANSISTOR_HEIGHT_FINFET = 34
		hInv=self.hInv
		if (self.featureSize <= 14 * 1e-9):  # finfet
			hInv *= (MAX_TRANSISTOR_HEIGHT_FINFET/MAX_TRANSISTOR_HEIGHT)

		
		area = 0
		self.totalWireLength = 0
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)/2   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)/2    # first horizontal stage (despite of main bus)
		wireWidV = 0
		wireWidH = 0
		numRepeater = 0
		
		for i in range(1, (self.numStage - 1) // 2):   # start from center point, consider both vertical and horizontal stage at each time, ignore last stage, assume it overlap with unit's layout
			wireWidth, unitLengthWireResistance = 0.0,0.0

			#*** vertical stage ***#
			wireLengthV /= 2   # wire length /2 
			wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthV)
			numRepeater = math.ceil(wireLengthV/self.minDist)
			if (numRepeater > 0):
				wireWidV += self.busWidth*wInv/self.foldedratio   # which ever stage, the sum of wireWidth should always equal to busWidth (main bus width)
			else:
				wireWidV += self.busWidth*wireWidth/self.foldedratio
			
			area += wireWidV*wireLengthV/2
			
			#*** horizontal stage ***#
			wireLengthH /= 2   # wire length /2 
			wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthH)
			numRepeater = math.ceil(wireLengthH/self.minDist)
			if (numRepeater > 0):
				wireWidH += self.busWidth*hInv/self.foldedratio   # which ever stage, the sum of wireWidth should always equal to busWidth (main bus width)
			else:
				wireWidH += self.busWidth*wireWidth/self.foldedratio
			area += wireWidH*wireLengthH/2
			
			#*** count totalWireLength ***#
			self.totalWireLength += wireLengthV + wireLengthH
		
		self.totalWireLength += min(self.numCol-self.x_center, self.x_center)*self.unitWidth
		area += (self.busWidth*hInv/self.foldedratio)*min(self.numCol-self.x_center, self.x_center)*self.unitWidth   # main bus: find the way nearest to the boundray as source
		self.area = area

		return self.area

	def GetUnitLengthRes(self,wireLength):
		AR = 0
		Rho = 0
		unitLengthWireResistance = 0

		if wireLength / self.featureSize >= 100000:
			wireWidth = 4 * self.wireWidth
		elif 10000 <= wireLength / self.featureSize <= 100000:
			wireWidth = 2 * self.wireWidth
		else:
			wireWidth = 1 * self.wireWidth

		if wireWidth >= 175:
			AR = 1.6
			Rho = 2.20e-8
		elif 110 <= wireWidth < 175:
			AR = 1.6
			Rho = 2.52e-8
		elif 105 <= wireWidth < 110:
			AR = 1.7
			Rho = 2.68e-8
		elif 80 <= wireWidth < 105:
			AR = 1.7
			Rho = 3.31e-8
		elif 56 <= wireWidth < 80:
			AR = 1.8
			Rho = 3.70e-8
		elif 40 <= wireWidth < 56:
			AR = 1.9
			Rho = 4.03e-8
		elif 25 <= wireWidth < 40:
			AR = 2.0
			Rho = 5.08e-8
		else:
			AR = 2.0
			Rho = 6.35e-8

		Rho *= (1 + 0.00451 * (self.temp - 300))

		# get unitLengthWireResistance
		if wireWidth == -1:
			unitLengthWireResistance = 1.0  # Use a small number to prevent numerical error
		else:
			unitLengthWireResistance = Rho / (wireWidth * 1e-9 * wireWidth * 1e-9 * AR)
		return wireWidth, unitLengthWireResistance



	def get_latency(self, x_init, y_init, x_end, y_end, numBitToLoadOut, numBitToLoadIn):
		numRead = (numBitToLoadOut+numBitToLoadIn)/self.busWidth
		readLatency = 0
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)    # first horizontal stage (despite of main bus)
		numRepeater = 0

		if (((not x_init) & (not y_init)) | ((not x_end) & (not y_end))): # root-leaf communicate (fixed addr)
			for i in range(1, (self.numStage - 1) // 2): # ignore main bus here, but need to count until last stage (diff from area calculation)
				wireWidth, unitLengthWireResistance = 0.0,0.0
			
				#*** vertical stage ***#
				wireLengthV /= 2   # wire length /2 
				wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthV)
				unitLatencyRep = 0.7*(self.resOnRep*(self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)+0.5*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist+unitLengthWireResistance*self.minDist*self.capInvInput)/self.minDist
				unitLatencyWire = 0.7*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist/self.minDist
				numRepeater = math.ceil(wireLengthV/self.minDist)
				if (numRepeater > 0):
					readLatency += wireLengthV*unitLatencyRep
				else:
					readLatency += wireLengthV*unitLatencyWire
				
				#*** horizontal stage ***#
				wireLengthH /= 2   # wire length /2 
				wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthH)
				unitLatencyRep = 0.7*(self.resOnRep*(self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)+0.5*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist+unitLengthWireResistance*self.minDist*self.capInvInput)/self.minDist
				unitLatencyWire = 0.7*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist/self.minDist
				numRepeater = math.ceil(wireLengthH/self.minDist)
				if (numRepeater > 0):
					readLatency += wireLengthH*unitLatencyRep
				else:
					readLatency += wireLengthH*unitLatencyWire
			
			#*** main bus ***#
			if (self.numStage - 1) // 2 <=1: # did not go into for loop above
				unitLatencyRep = 0
			readLatency += min(self.numCol-self.x_center, self.x_center)*self.unitWidth*unitLatencyRep
		readLatency *= numRead
		self.latency = readLatency

		return self.latency
	def get_energy(self, x_init, y_init, x_end, y_end, numBitToLoadOut,numBitToLoadIn):

		numBitAccess = self.busWidth
		numRead = (numBitToLoadOut+numBitToLoadIn)/self.busWidth
		readDynamicEnergy = 0

		unitLengthEnergyRep = (self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)*self.vdd*self.vdd/self.minDist*0.25
		unitLengthEnergyWire = (self.unitLengthWireCap*self.minDist)*self.vdd*self.vdd/self.minDist*0.25
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)/2   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)/2    # first horizontal stage (despite of main bus)
		
		if (((not x_init) & (not y_init)) | ((not x_end) & (not y_end))):
      	# root-leaf communicate (fixed addr)
			for i in range(1, (self.numStage - 1) // 2): # ignore main bus here, but need to count until last stage (diff from area calculation)
				#*** vertical stage ***#
				wireLengthV /= 2   # wire length /2 
				numRepeater = math.ceil(wireLengthV/self.minDist)
				if (numRepeater > 0):
					readDynamicEnergy += wireLengthV*unitLengthEnergyRep
				else:
					readDynamicEnergy += wireLengthV*unitLengthEnergyWire
				
				#*** horizontal stage ***#
				wireLengthH /= 2   # wire length /2 
				numRepeater = math.ceil(wireLengthH/self.minDist)
				if (numRepeater > 0):
					readDynamicEnergy += wireLengthH*unitLengthEnergyRep
				else:
					readDynamicEnergy += wireLengthH*unitLengthEnergyWire
	
			#*** main bus ***#
			readDynamicEnergy += min(self.numCol-self.x_center, self.x_center)*self.unitWidth*unitLengthEnergyRep
			readDynamicEnergy *= numBitAccess  
		readDynamicEnergy *= numRead
		self.energy = readDynamicEnergy
		return self.energy

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.    
class ClkTree:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return self.area

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.
class Controller:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return self.area
