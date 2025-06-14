from utils.peripheral import *
import math

class Subarray:
    def __init__(self,config,technode,chiplet_type,memory_cell_type):
        self.chiplet_type = chiplet_type # chiplet_type = dynamic, static, semi_static, acc_and_buffer
        self.technode = technode
        # self.buffer = Buffer(config,technode)
        self.subarray_height = None
        self.subarray_width = None
        self.cell_size = 0
        self.read_energy_per_bit = 0
        self.write_energy_per_bit = 0 # now, only used in refresh energy, how about write energy? write energy only include buffer_write energy
        if chiplet_type == 'static':
            self.subarray_height = config.static_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.static_subarray_width # num of cell cols in a subarray
        elif chiplet_type == 'semi_static':
            self.subarray_height = config.semistatic_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.semistatic_subarray_width # num of cell cols in a subarray
        elif chiplet_type == 'dynamic':
            self.subarray_height = config.dynamic_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.dynamic_subarray_width # num of cell cols in a subarray
        self.memory_cell_type = memory_cell_type # 'eDRAM', RRAM, none (acc_and_buffer)
        if memory_cell_type == 'eDRAM':
            if self.technode == 14:
                self.cell_size = config.eDRAM_cell_size_14nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_14nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_14nm
            elif self.technode == 16:
                self.cell_size = config.eDRAM_cell_size_16nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_16nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_16nm
            elif self.technode == 22:
                self.cell_size = config.eDRAM_cell_size_22nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_22nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_22nm
            elif self.technode == 28:
                self.cell_size = config.eDRAM_cell_size_28nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_28nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_28nm
            elif self.technode == 40:
                self.cell_size = config.eDRAM_cell_size_40nm
                self.read_energy_per_bit =  config.eDRAM_read_energy_per_bit_40nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_40nm
            elif self.technode == 65:
                self.cell_size = config.eDRAM_cell_size_65nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_65nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_65nm
            elif self.technode == 130:
                self.cell_size = config.eDRAM_cell_size_130nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_130nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_130nm
        if memory_cell_type == 'RRAM':
            if self.technode == 40:
                self.cell_size = config.RRAM_cell_size_40nm
                self.read_energy_per_bit =  config.RRAM_read_energy_per_bit_40nm
                self.write_energy_per_bit = config.RRAM_write_energy_per_bit_40nm
            elif self.technode == 130:
                self.cell_size = config.eDRAM_cell_size_130nm
                self.read_energy_per_bit =  config.eDRAM_read_energy_per_bit_130nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_130nm
            
        self.shiftadd = ShiftAdd(config,technode,self.memory_cell_type,self.subarray_width)
        
    
    def get_area(self):
        area = self.cell_size * self.subarray_height * self.subarray_width
        if self.memory_cell_type == 'eDRAM':
            area *= 2
        return area
    def get_size_height(self):
        return math.sqrt(self.get_area())
    def get_size_width(self):
        return math.sqrt(self.get_area())