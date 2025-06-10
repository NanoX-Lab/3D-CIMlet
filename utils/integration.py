import math
from abc import ABC, abstractmethod
from utils.tsv_path import TSVPath
from utils.chiplet import Chiplet

class Integration(ABC):
    # Area
    @abstractmethod    
    def CalculateArea(self):
        pass

class Integration2D(Integration):
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semistatic_chiplet,num_used_dynamic_chiplet):
        
        self.total_IO_cell_area_40nm = 62.65 * 1E-12 * 8
        self.static_chiplet_technode = config.static_chiplet_technode
        self.dynamic_chiplet_technode = config.dynamic_chiplet_technode
        self.semistatic_chiplet_technode = config.semistatic_chiplet_technode

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_static_chiplet = num_used_static_chiplet

        self.semistatic_chiplet = Chiplet(config,chiplet_type='semi_static',memory_cell_type=config.semistatic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)

        self.num_semistatic_chiplet = num_used_semistatic_chiplet

        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = num_used_dynamic_chiplet

    def CalculateArea(self):

        print("static_chiplet area", self.static_chiplet.get_area() * 1E6, "mm2")
        print("semistatic_chiplet area", self.semistatic_chiplet.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static_chiplet.get_area() > 858E-06 or self.semistatic_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()

        area = (self.static_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.static_chiplet_technode, 2)/math.pow(40,2))) * self.num_static_chiplet + (self.semistatic_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.semistatic_chiplet_technode, 2)/math.pow(40,2))) * self.num_semistatic_chiplet + (self.dynamic_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.dynamic_chiplet_technode, 2)/math.pow(40,2))) * self.num_dynamic_chiplet 
        
        # add die-to-die spacing (assume trace len.: 300~500um)
        spacing_len = 300e-6
        num_die = self.num_static_chiplet + self.num_dynamic_chiplet
        num_die_spacing = math.ceil(math.sqrt(num_die)) - 1
        area += (num_die_spacing * spacing_len) * math.sqrt(area) * 2
        
        return area

class Integration2_5D(Integration):
    
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semistatic_chiplet, num_used_dynamic_chiplet):

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_static_chiplet = num_used_static_chiplet

        self.semistatic_chiplet = Chiplet(config,chiplet_type='semi_static',memory_cell_type=config.semistatic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_semistatic_chiplet = num_used_semistatic_chiplet
        
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = num_used_dynamic_chiplet
        
        self.min_memory_chip_area = min(self.static_chiplet.get_area(),self.semistatic_chiplet.get_area(),self.dynamic_chiplet.get_area())

    def CalculateArea(self):

        print("static_chiplet area", self.static_chiplet.get_area() * 1E6, "mm2")
        print("static_chiplet buffer size", self.static_chiplet.buffer_size)
        print("static_chiplet buffer area", self.static_chiplet.buffer.get_area() * 1E6, "mm2")
        print("semistatic_chiplet area", self.semistatic_chiplet.get_area() * 1E6, "mm2")
        print("semistatic_chiplet buffer area", self.semistatic_chiplet.buffer.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static_chiplet.get_area() > 858E-06 or self.semistatic_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()

        area = self.static_chiplet.get_area() * self.num_static_chiplet + self.semistatic_chiplet.get_area() * self.num_semistatic_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet 
        
        # add die-to-die spacing (assume trace len.: 300~500um)
        spacing_len = 300e-6
        num_die = self.num_static_chiplet + self.num_dynamic_chiplet
        num_die_spacing = math.ceil(math.sqrt(num_die)) - 1
        area += (num_die_spacing * spacing_len) * math.sqrt(area) * 2
        
        return area

class Integration3D(Integration):

    def __init__(self,config,maxnum_layer_in_bit):

        self.tsv = TSVPath()
        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)

        self.semistatic_chiplet = Chiplet(config,chiplet_type='semi_static',memory_cell_type=config.semistatic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)

        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit = maxnum_layer_in_bit)
        
        self.pitch_size_3d = config.pitch_size_3d
        self.num_tsv = self.logic_chiplet.buffer_mem_width
    
    def CalculateArea(self):
        print("static_chiplet area", self.static_chiplet.get_area() * 1E6, "mm2")
        
        print("semistatic_chiplet area", self.semistatic_chiplet.get_area() * 1E6, "mm2")
        print("semistatic_chiplet buffer area", self.semistatic_chiplet.buffer.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")
        print("logic_chiplet area", self.logic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static_chiplet.get_area() > 858E-06 or self.semistatic_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()
        
        self.area = max(self.static_chiplet.get_area(), self.semistatic_chiplet.get_area(), self.dynamic_chiplet.get_area())
        
        self.total_tsv_area = self.tsv.CalculateArea() * self.num_tsv
        self.area += self.total_tsv_area
        return self.area
