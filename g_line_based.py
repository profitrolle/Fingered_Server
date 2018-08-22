'''
Created on Feb 22, 2018

@author: profitrolle
'''

import math as m

class LineBased():
    '''
    classdocs
    '''


    def __init__(self, p_width, p_height):
        '''
        Constructor
        '''
        pass

class Line():
    
    def __init__(self, p_y , p_x, p_height, p_width, p_hole_list, p_z_pass, p_tool_diameter, p_safe_xy):
        self.x = p_x 
        self.y = p_y
        self.height = p_height
        self.width = p_width
        self.x_end = self.x + p_width
        self.hole_list = p_hole_list
        self.current_depth = 0
        self.z_path = p_z_pass
        self.tool_diameter = p_tool_diameter
        self.safe_xy = p_safe_xy
        self.position_list = []

    def get_max_common_depth(self, hole_list):
        max_common_depth = hole_list[0].depth
        for hole in hole_list:
            if hole.depth < max_common_depth:
                max_common_depth = hole.depth
        self.max_common_depth = max_common_depth
        return max_common_depth
    
    def compute_line_x_depl_top(self, hole_list):
        x_end = hole_list[-1].x + hole_list[-1].width
        self.go_to_xy(x_end, self.y, 'r', 't')
 
    def compute_top_down(self, hole_list):
        x_end = hole_list[-1].x + hole_list[-1].width
        y_down = self.y - self.height + m.tan(hole_list[-1].angle) * self.current_depth
        self.go_to_xy(x_end, y_down, 'r', 'b')
        
    def compute_line_x_depl_down(self, hole_list):
        for next_hole in hole_list[-2::-1]:
            # Check if current y position is different than the one to have on the next hole
            next_y = self.y - self.height + self.get_y_offset(next_hole)
            next_x = next_hole.x + next_hole.width
            if next_y > self.current_y:
                self.go_to_xy(next_x, self.current_y, 'l', 'b')
                self.go_to_xy(next_x, next_y, 'l', 'b')
            elif next_y < self.current_y:
                self.go_to_xy(next_x, self.current_y, 'r', 'b')
                self.go_to_xy(next_x, next_y, 'r', 'b')
        next_y = self.y - self.height + self.get_y_offset(hole_list[0])
        self.go_to_xy(hole_list[0].x, next_y, 'l', 'b')
            
    
    def compute_points(self):
        # Make the comple line common
#         self.make_common_list(self.hole_list, 0)
#TEMP TODO JUST CORRECTION BAAAD
        new_list = []
        hole_1 = self.hole_list[0]
        hole_1.width += self.tool_diameter/2
        new_list.append(hole_1)
        for hole in self.hole_list[1:-1]:
            hole.x -= self.tool_diameter/2
            hole.width += self.tool_diameter
            new_list.append(hole)
        if self.hole_list > 1:
            hole_last = self.hole_list[-1]
            hole_last.x -= self.tool_diameter/2
            new_list.append(hole_last)
        for hole in new_list:
            self.make_hole(hole)
        return self.position_list

    def make_common_list(self, hole_list, last_z):
        max_depth_for_cut = self.get_max_common_depth(hole_list)
        self.make_common(hole_list, max_depth_for_cut, last_z)
        common_hole_list = self.get_hole_common_list_split(hole_list, max_depth_for_cut)
        for sublist in common_hole_list:
            if len(sublist)> 0:
                self.make_common_list(sublist, max_depth_for_cut)
        
    def get_hole_common_list_split(self, hole_list, max_common_depth):
        common_hole_list = []
        new_hole_list = []
        for hole in hole_list:
            if hole.depth > max_common_depth:
                new_hole_list.append(hole)
            else:
                common_hole_list.append(new_hole_list)
                new_hole_list = []
        if new_hole_list:
            common_hole_list.append(new_hole_list)
        return common_hole_list
        
    def make_common(self, hole_list, max_common_depth, z_start):
        self.go_to_xy_line_common_safe(hole_list)
        self.go_to_z(['z_c', z_start])
        self.go_to_xy_line_start(hole_list)
        while (self.current_depth < max_common_depth):
            self.go_to_z(['z_pass'])
            self.compute_line_x_depl_top(hole_list)
            self.compute_top_down(hole_list)
            self.compute_line_x_depl_down(hole_list)
            self.go_to_xy_line_start(hole_list)
            self.go_to_xy_line_start_bot(hole_list)
            self.go_to_xy_line_start(hole_list)
        self.go_to_xy_line_common_safe(hole_list)
        last_z = self.current_depth
        self.go_to_z(['z_safe'])
        return last_z

    def make_hole(self, hole):
        self.go_to_xy(hole.x + self.safe_xy, self.y - self.safe_xy, 'l', 't')
        self.go_to_z(['z_c', 0])
        self.go_to_xy(hole.x, self.y, 'l', 't')
        while (self.current_depth < hole.depth):
            self.go_to_z(['z_pass'])
            next_y = self.y - self.height + self.get_y_offset(hole)
            self.go_to_xy(hole.x + hole.width, self.y, 'r', 't')
            self.go_to_xy(hole.x + hole.width, next_y, 'r', 'b')
            self.go_to_xy(hole.x, next_y, 'l', 'b')
            self.go_to_xy(hole.x, self.y, 'l', 't')            
        self.go_to_xy_line_common_safe([hole])
        self.go_to_z(['z_safe'])
    
    def go_to_xy_line_common_safe(self, hole_list):
        self.go_to_xy(hole_list[0].x + self.safe_xy*5, self.y - self.safe_xy, 'l', 't')
    
    def go_to_xy_line_start(self, hole_list):
        self.go_to_xy(hole_list[0].x, self.y, 'l', 't')
        
    def go_to_xy_line_start_bot(self, hole_list):
        self.go_to_xy(hole_list[0].x, self.y - self.height + self.get_y_offset(hole_list[0]), 'l', 'b')
    
    def get_last_y(self):
        return self.position_list[-1][-1]
    
    def get_y_offset(self, hole):
        return m.tan(hole.angle) * self.current_depth
    
    def go_to_xy(self, x, y, rl, tb):
        self.current_x = x
        self.current_y = y
        if rl == 'r':
            x -= self.tool_diameter / 2
        else:
            x += self.tool_diameter / 2
        if tb == 't':
            y -= self.tool_diameter / 2
        else:
            y += self.tool_diameter / 2
        self.position_list.append([x, y])
    
    def go_to_z(self, z_data):
        if z_data[0] == 'z_pass':
            self.position_list.append(['z', 'z_pass'])
            self.current_depth += self.z_path
        elif z_data[0] == 'z_safe':
            self.position_list.append(['z', 'z_safe'])
            self.current_depth = 0
        elif z_data[0] == 'z_c':
            self.position_list.append(['z', 'z_go', z_data[1]])
            self.current_depth = z_data[1]

class Hole():
    
    def __init__(self, p_line, p_x_start, p_width, p_depth, p_angle):
        self.line = p_line
        self.x = p_x_start
        self.width = p_width
        self.depth = p_depth
        self.angle = p_angle
        self.check_angle()
    
    def check_angle(self):
        if self.angle > m.atan2(17, self.depth):
            print('WARNING, ANGLE FOR HOLE LINE TOO BIG')
            print('Hole at line ', self.line, 'with angle ', self.angle, '@ position', self.x)

class Separator():
    
    def __init__(self, p_line, p_x):
        self.line = p_line
        self.x = p_x
