'''
Created on Nov 20, 2016

@author: profitrolle
'''

import json
from g_logging import *
import g_line_based as glb
import math as m
from g_hole_config import Hole
import os

g_logger = logging.Logger('g_logger')
g_logger.setLevel(logging.DEBUG)
g_logger.addHandler(console_handler)


def sign(x):
    if x >= 0:
        return 1
    return -1


class G_Objects(object):

    '''
    classdocs
    '''

    def __init__(self, machine_configuration_file="./configuration/g_machine_default_conf.json",
                 output_file='g_code.gco',
                 do_by_in_out='on_line', p_approach=None, p_approach_radius=6,
                 output_round_file='round.gco', p_add_round=False, p_path=""):
        '''
        Constructor
        '''
        g_logger.info('Initialization of G_Objects.')
        self.init_machine(machine_configuration_file)
        self.gcode_file_name = output_file
        self.path = p_path
        self.gcode_file_abs_name = self.path + self.gcode_file_name
        self.current_command = 1
        # Initialize coordinate
        self.current_z = 0
        self.current_x = 0
        self.current_y = 0
        # Approach param
        self.approach = p_approach
        self.approach_radius = p_approach_radius
        # multiplier and divider for slopes
        self.multiplier = 1
        self.divider = 2
        # Adding round at the end
        self.add_round = p_add_round
        self.output_round_file = output_round_file
        self.a_round = 5
        self.r_round = 5
        # Empty list hole
        self.list_holes = {}
        # Add hole methods
        self.hole_method = {
            'x_hole': self.make_x_finger_hole,
            'x_slope': self.make_x_slope,
            'line_hole':self.make_line_hole,
        }

    def init_machine(self, p_conf_file):
        with open(p_conf_file) as f:
            conf_data = json.load(f)
        
        self.origin = [conf_data["origin_coord"]["x_origin"],
                       conf_data["origin_coord"]["x_origin"]]
        self.x_end = self.origin[0] + conf_data["max_x_distance"]
        self.y_end = self.origin[1] + conf_data["max_y_distance"]
        self.speed_fast = conf_data["fast_displacement_speed"]
        self.speed_mill = conf_data["milling_speed"]
        self.speed_z = conf_data["milling_z_speed"]
        self.safe_z = conf_data["safe_z"]
        self.z_pass = conf_data["z_pass"]
        self.tool_diameter = conf_data["tool_diameter"]
        self.do_by_in_out = conf_data["do_by_in_out"]

    def init_gcode_file(self):
        # Create G file
        with open(self.gcode_file_abs_name, 'w+') as f:
            f.write('( This is a automatically generated file, do not edit. )\' \n \
                (or do it, i\'m just a freaking algorithm, \
                i won\'t bite you)\n ')
        if self.add_round:
            with open(self.output_round_file, 'w+') as f:
                f.write('( This is a automatically generated file, do not edit. )\' \n \
                    (or do it, i\'m just a freaking algorithm, \
                    i won\'t bite you)\nG21\n')
        os.chmod(self.gcode_file_abs_name, 0o666)
        self.print_g_file('G21', '', [])

    def set_gcode_path(self, path):
        self.path = path
        self.gcode_file_abs_name = self.path + self.gcode_file_name

    def set_gcode_file_name(self, name):
        self.gcode_file_name = name
        self.gcode_file_abs_name = self.path + self.gcode_file_name
        self.init_gcode_file()

    def make_holes(self, p_list_holes=None):
        self.list_holes = p_list_holes
        if p_list_holes:
            self.list_holes = p_list_holes
        for json_hole in self.list_holes:
            hole = Hole(**json_hole)
            if hole.hole_type == 'x_slope':
                self.hole_method[hole.hole_type](
                    hole.depth, hole.x_position, hole.y_position, hole.length, hole.angle,
                    hole.is_left_occupied, hole.is_right_occupied)
            elif hole.hole_type == 'x_hole':
                self.hole_method[hole.hole_type](
                    hole.depth, hole.x_position, hole.y_position, hole.length, hole.height)
            elif hole.hole_type == 'line_hole':
                self.hole_method[hole.hole_type](
                    hole.position_list)
            else:
                self.hole_method[hole.hole_type](
                    hole.depth, hole.x_position, hole.y_position, hole.height)

    def make_x_finger_hole(self, p_depth, p_x, p_y, p_length, p_height):
        if self.tool_diameter == p_height:
            self.do_line_to_depth(p_depth, p_x, p_y, p_length)
        else:
            self.do_func_to_depth(
                self.rectangle,
                p_depth, p_x, p_y,
                p_length,
                p_height)

    def make_line_hole(self, p_line_position_list):
        self.convert_line_based(p_line_position_list)

    def make_x_slope(self, p_depth, p_x, p_y, p_length, p_angle, is_left_occupied, is_right_occupied):
        """
        The slope is defined as :

            -o is x, y origin
            -x [degree]
            -one hand length
        ____________________
           xxxxxxx
           oxxxxxx
             length

        ____________________
        """
#         self.do_plane_to_depth_with_slope(
#             self.depth, p_x, p_y + self.tool_diameter,
#             p_length,
#             self.depth *
#             m.tan(
#                 p_angle) + self.tool_diameter, 0,
#             p_angle, 0, 0)
        self.do_slope_top(
            self.depth, p_x, p_y,
            p_length,
            self.depth * 
            m.tan(
                p_angle),
            p_angle, is_left_occupied, is_right_occupied)
        
    def line(self, x, y):
        self.print_g_file('G1', 'XYF', [x, y, self.speed_mill])

    def circle_at(self, x0, y0, center_x, center_y):
        x_diff = x0 - center_x
        y_diff = y0 - center_y
        self.print_g_file(
            'G2', 'IJF', [x_diff, y_diff, self.speed_mill])

    def arc_at(self, x0, y0, center_x, center_y, angle):
        x_diff = center_x - x0
        y_diff = center_y - y0
        radius = m.sqrt((x_diff) ** 2 + (y_diff) ** 2)
        x_end = x0 + sign(-y_diff) * (radius * m.sin(angle))
        y_end = y0 - sign(-y_diff) * (radius * (1 - m.cos(angle)))
        self.print_g_file(
            'G2', 'XYIJF', [round(x_end, 2),
                           round(y_end, 2),
                           x_diff, y_diff, self.speed_mill])

    def rectangle(self, x0, y0, lx, ly):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        self.line(x0 + lx, y0)
        self.line(x0 + lx, y0 - ly)
        self.line(x0, y0 - ly)
        self.line(x0, y0)
    
    def rectangle_tilt(self, x0, y0, lx, ly, angle):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        self.line(x0 + lx, y0 + lx * m.tan(angle))
        self.line(x0 + lx, y0 + lx * m.tan(angle) - ly)
        self.line(x0, y0 - ly)
        self.line(x0, y0)

    def plane(self, x0, y0, lx, ly):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        y_cur = y0
        y_end = y0 - ly
        idx = 0
        if ly > self.tool_diameter:
            while y_cur > y_end:
                if idx % 2 == 0:
                    self.line(x0 + lx, y_cur)
                    y_cur -= min([self.tool_diameter, (y_cur - y_end)])
                    self.line(x0 + lx, y_cur)
                if idx % 2 == 1:
                    self.line(x0, y_cur)
                    y_cur -= min([self.tool_diameter, (y_cur - y_end)])
                    self.line(x0, y_cur)
                idx += 1
        # Make rectable at end to have nice contour
        self.line(x0, y0)
        self.rectangle(x0, y0, lx, ly)

    def round_rectangle(self, x0, y0, lx, ly, r):
        if r > lx / 2 or r > ly / 2:
            g_logger.error('Radius too big for round rectangle.')
            return
        self.line(x0 + lx - 2 * r, y0)
        self.arc_at(x0 + lx - 2 * r, y0, x0 + lx - 2 * r, y0 + r, m.pi / 2)
        self.line(x0 + lx - r, y0 + ly - r)
        self.arc_at(
            x0 + lx - r, y0 + ly - r, x0 + lx - 2 * r, y0 + ly - r, m.pi / 2)
        self.line(x0, y0 + ly)
        self.arc_at(x0, y0 + ly, x0, y0 + ly - r, m.pi / 2)
        self.line(x0 - r, y0 - r)
        self.arc_at(x0 - r, y0 - r, x0, y0 + r, m.pi / 2)

    def round_end_rectangle(self, x0, y0, lx, ly):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        if lx < ly:
            g_logger.error('Radius too big for round rectangle.')
            return
        self.line(x0 + lx - ly, y0)
        self.arc_at(x0 + lx - ly, y0, x0 + lx - ly, y0 - ly / 2, m.pi)
        self.line(x0, y0 - ly)
        self.arc_at(x0, y0 - ly, x0, y0 - ly / 2, m.pi)

    def round_end_rectangle_pocket(self, x0, y0, lx, ly):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        x_cur = x0
        y_cur = y0
        lx_cur = lx
        ly_cur = ly
        # Move to x0 yo
        self.go_to(x0, y0)
        # Only apply corrrection once.
        # Save strategy for restoring later
        bu_do_by_in_out = self.do_by_in_out
        self.do_by_in_out = 'on_line'
        while ly_cur > 0 and lx_cur > 0:
            self.round_end_rectangle(x_cur, y_cur, lx_cur, ly_cur)
            y_cur -= self.tool_diameter
            ly_cur -= 2 * self.tool_diameter
            lx_cur -= 2 * self.tool_diameter
            self.line(x_cur, y_cur)
        self.do_by_in_out = bu_do_by_in_out

    def do_plane_to_depth_with_slope(self, depth, x0, y0, lx, ly,
                                     slope_up, slope_down,
                                     slope_left, slope_right):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        x_cur = x0
        y_cur = y0
        x_cur_end = x0 + lx
        y_cur_end = y0 - ly
        z_cur = 0
        self.go_z_safe()
        self.go_to(x0, y0)
        bu_do_by_in_out = self.do_by_in_out
        self.do_by_in_out = 'on_line'
        z_diff = self.z_pass * self.multiplier
        while self.current_z >= -depth + 1:
            self.go_to_z(z_cur)
            self.plane(
                x_cur, y_cur, abs(x_cur_end - x_cur), abs(y_cur_end - y_cur))
            z_cur -= z_diff
            # Update parameter
            x_cur += abs(m.tan(slope_left) * z_diff)
            y_cur -= abs(m.tan(slope_up) * z_diff)
            x_cur_end -= abs(m.tan(slope_right) * z_diff)
            y_cur_end += abs(m.tan(slope_down) * z_diff)
            self.line(x_cur, y_cur)
        self.go_z_safe()
        # Be more precise about the slope
#         if slope_down != 0:
#             self.finish_slope_down(depth, x0, y0 - ly, lx, slope_down)
        self.go_to(x0, y0)
        self.do_by_in_out = bu_do_by_in_out

    def finish_slope(self, depth, x0, y0, lx, ly,
                     slope_up, slope_down,
                     slope_left, slope_right):
        x_cur = x0
        y_cur = y0
        x_cur_end = x0 + lx
        y_cur_end = y0 - ly
        z_cur = 0
        self.go_z_safe()
        self.go_to(x0, y0)
        z_diff = self.z_pass / self.divider
        while self.current_z >= -depth + 1:
            self.go_to_z(z_cur)
            self.rectangle(
                x_cur, y_cur, abs(x_cur_end - x_cur), abs(y_cur_end - y_cur))
            z_cur -= z_diff
            # Update parameter
            x_cur += abs(m.tan(slope_left) * z_diff)
            y_cur -= abs(m.tan(slope_up) * z_diff)
            x_cur_end -= abs(m.tan(slope_right) * z_diff)
            y_cur_end += abs(m.tan(slope_down) * z_diff)
            self.line(x_cur, y_cur)
        self.go_z_safe()
        self.go_to(x0, y0)

    def finish_slope_down(self, depth, x0, y0, lx, slope_down):
        x_start = x0
        x_end = x0 + lx
        x = x_end
        z_cur = 0
        self.go_z_safe()
        self.go_to(x0, y0)
        z_diff = self.z_pass / self.divider
        while self.current_z >= -depth + 1:
            # Mill
            self.go_to_z(z_cur)
            self.line(x, y0)
            # Update params
            z_cur -= z_diff
            y0 += abs(m.tan(slope_down) * z_diff)
            self.line(x, y0)
            # Update parameter
            if x == x_start:
                x = x_end
            else:
                x = x_start
        self.go_z_safe()
        self.go_to(x0, y0)

    def finish_slope_up(self, depth, x0, y0, lx, slope_up):
        x_start = x0
        x_end = x0 + lx
        x = x_start
        z_cur = 0
        self.go_z_safe()
        self.go_to(x0, y0)
        z_diff = self.z_pass / self.divider
        while self.current_z >= -depth + 1:
            self.go_to_z(z_cur)
            self.line(x, y0)
            self.current_z -= z_diff
            # Update parameter
            if x == x_start:
                x = x_end
            else:
                x = x_start
            y0 -= abs(m.tan(slope_up) * z_diff)
            self.line(x, y0)
        self.go_z_safe()
        self.go_to(x0, y0)
        
    def do_slope_top(self, depth, x0, y0, lx, ly, slope, is_left_occupied, is_right_occupied):
        # Do not do routine for inside/outside -> particular stuff.
        bu_do_by_in_out = self.do_by_in_out
        self.do_by_in_out = 'on_line'
        # y is 'online' top and 'inline' bottom
        ly -= self.tool_diameter / 2
        # x is 'inline' if the side is occupied with a smaller slope
        if is_left_occupied:
            x0 = x0 + self.tool_diameter / 2
            lx = lx - self.tool_diameter / 2
        if is_right_occupied:
            lx = lx - self.tool_diameter / 2
        y_cur = y0
        y_cur_end = y0 - ly
        ly_cur = abs(y_cur_end - y_cur)
        z_cur = 0
        self.go_z_safe()
        self.go_to(x0, y0)
        z_diff = self.z_pass * self.multiplier
        # Do the slope until the width of the rectangle is smaller than 
        # the cutting tool diameter/2
        while ly_cur >= self.tool_diameter / 2:
            self.go_to_z(z_cur)
            # Make a rectagle to have nice sides
            self.rectangle(
                x0, y_cur, lx, ly_cur)
            # Make plane inside the previous rectangle if the width is bigger than 3/2 tool diameter
            if ly_cur > 3 / 2 * self.tool_diameter:
                self.plane(
                    x0 + self.tool_diameter / 2, y_cur - self.tool_diameter / 2, lx - self.tool_diameter, ly_cur - self.tool_diameter)
            z_cur -= z_diff
            # Update parameter
            y_cur_end += abs(m.tan(slope) * z_diff)
            ly_cur = abs(y_cur_end - y_cur)
            # Go back to starting point
            self.line(x0, y_cur)
        # When the width is small enough, just go for lines
        while self.current_z > -depth:
            self.go_to_z(z_cur)
            # Make a line
            self.line(x0 + lx, y_cur_end)
            # Update parameter
            y_cur_end += abs(m.tan(slope) * z_diff)
            z_cur -= z_diff
            # Move to corect y
            self.line(x0 + lx, y_cur_end)
            if self.current_z > -depth:
                # Go down and come back
                self.go_to_z(z_cur)
                self.line(x0, y_cur_end)
                # Update parameter
                y_cur_end += abs(m.tan(slope) * z_diff)
                z_cur -= z_diff
                # Move to corect y
                self.line(x0, y_cur_end)

        self.go_z_safe()
        self.go_to(x0, y0)
        self.do_by_in_out = bu_do_by_in_out

    def finish_round(self, a, r, x0, y0, lx, ly):
        x0, y0, lx, ly = self.change_rectangle_param(x0, y0, lx, ly)
        self.go_z_safe()
        diff = a + 1
        self.go_to(x0, y0 - diff)
        self.go_to_z(-r + 1)
        # Only apply corrrection once.
        # Save strategy for restoring later
        bu_do_by_in_out = self.do_by_in_out
        self.do_by_in_out = 'on_line'
        self.round_end_rectangle(x0, y0 - diff, lx - diff * 2, ly - diff * 2)
        self.go_z_safe()
        self.go_to(x0, y0)
        self.do_by_in_out = bu_do_by_in_out

    def do_line_to_depth(self, depth, x0, y0, lx):
        x0, y0, lx, _ = self.change_rectangle_param(x0, y0, lx, 0)
        self.go_z_safe()
        self.go_to(x0, y0)
        z_cur = 0
        z_diff = self.z_pass * self.multiplier
        self.go_to_z(z_cur)
        index = 0
        while self.current_z > -depth:
            self.go_to_z(z_cur)
            # Make a line
            if index % 2 == 0 :
                self.line(x0 + lx, y0)
            else:
                self.line(x0, y0)
            # Update parameter
            z_cur -= z_diff
            index += 1

        self.go_z_safe()
        self.go_to(x0, y0)

    def do_func_to_depth(self, func, depth, x0, y0, *arg):
        x, y, lx, ly = self.change_rectangle_param(x0, y0, arg[0], arg[1])        
        if self.approach == 'round':
            self.add_round_approach(
                self.approach_radius, x, y, lx, ly)
        else:
            self.go_to(x, y)
            self.go_to_z(0)
        while self.current_z >= -depth:
            self.go_to_z(self.current_z - self.z_pass)
            func(x0, y0, *arg)
        # Go back to the middle of the element for safety
        if func == self.rectangle:
            x_mid = x + lx / 2
            y_mid = y - ly / 2
            self.line(x_mid, y_mid)
        elif func == self.rectangle_tilt:
            y_mid += lx / 2 * m.tan(arg[2])
            self.line(x_mid, y_mid)
        elif func == self.circle_at:
            x_mid = x + lx / 2
            y_mid = y - ly / 2
            self.line(x_mid, y_mid)
        #
        self.go_z_safe()
        if self.add_round and func == self.round_end_rectangle:
            file_bu = self.gcode_file_abs_name
            self.gcode_file_abs_name = self.output_round_file
            self.go_to(x, y)
            self.finish_round(self.a_round, self.r_round, x0, y0, *arg)
            self.gcode_file_abs_name = file_bu

    def change_rectangle_param(self, x0, y0, lx, ly):
        if self.do_by_in_out == 'inside':
            y0 -= self.tool_diameter / 2
            lx -= self.tool_diameter
            ly -= self.tool_diameter
            x0 += self.tool_diameter / 2
        elif self.do_by_in_out == 'outside':
            y0 += self.tool_diameter / 2
            lx += self.tool_diameter
            ly += self.tool_diameter
            x0 -= self.tool_diameter / 2
        return x0, y0, lx, ly

    def add_round_approach(self, p_radius, x0, y0, lx, ly):
        """
        Must ADD length to the original hole.
        """
        bu_do_by_in_out = self.do_by_in_out
        self.do_by_in_out = 'on_line'
        x_cur = x0
        y_cur = y0 + p_radius
        z_cur = 0
        lx_cur = lx + 2 * p_radius
        ly_cur = ly + 2 * p_radius
        self.go_to(x_cur, y_cur)
        while z_cur >= -p_radius:
            self.line(x_cur, y_cur)
            self.go_to_z(z_cur)
            self.round_end_rectangle(x_cur, y_cur, lx_cur, ly_cur)
            z_cur -= self.z_pass
            alpha = m.asin((p_radius + z_cur) / p_radius)
            diff = p_radius - m.cos(alpha) * p_radius
            y_cur = y0 + diff
            lx_cur = lx + 2 * diff
            ly_cur = ly + 2 * diff
        self.do_by_in_out = bu_do_by_in_out
    
    def make_sphere(self, x0, y0, p_radius):
        """
        Here x0 and y0 corresponds to the center coordinates.
        p_radius is equal to the radius of the sphere AND thus, the depth.
        """
        # Goto the center of the sphere, depth 0
        self.go_to(x0, y0)
        self.go_to_z(0)
        l_current_radius = 0
        while self.current_z + p_radius >= 0:
            # Compute new radius
            l_current_radius = m.sqrt(((p_radius) ** 2 - (p_radius + self.current_z) ** 2)) + self.tool_diameter / 2
            # Go to correct x, y coordinates
            self.line(x0 - (l_current_radius), y0)
            # Go down one step
            self.go_to_z(self.current_z - self.z_pass)
            self.print_g_file(
                'G2', 'IF', [l_current_radius , self.speed_mill])
            # Finalize the circle at depth for further millings
            while l_current_radius < p_radius:
                l_current_radius = l_current_radius + self.tool_diameter
                self.line(x0 - (l_current_radius), y0)
                self.print_g_file(
                    'G2', 'IF', [l_current_radius, self.speed_mill])
            self.line(x0 - (p_radius + self.tool_diameter / 2), y0)
            self.print_g_file(
                'G2', 'IF', [p_radius + self.tool_diameter / 2, self.speed_mill])

    def do_bezier(self, bezier_points):
        for point in bezier_points:
            self.line(point[0], point[1])

    def go_z_safe(self):
        self.print_g_file('G1', 'ZF', [self.safe_z, self.speed_z])
        self.current_z = self.safe_z

    def go_to(self, x, y):
        self.print_g_file('G1', 'ZF', [self.safe_z, self.speed_z])
        self.print_g_file('G1', 'XYF', [x, y, self.speed_mill])

    def go_to_slow(self, x, y):
        self.print_g_file('G1', 'XYF', [x, y, self.speed_slow])

    def go_to_z(self, z):
        self.print_g_file('G1', 'ZF', [z, self.speed_z])
        self.current_z = z

    def print_g_file(self, command, axes, args):
        if not (type(args) is list):
            args = [args]
        if len(axes) != len(args):
            g_logger.error('Args length do not match axes length.')
            return
        with open(self.gcode_file_abs_name, 'a+') as g_file:
            line = 'N' + str(self.current_command) + ' ' + command + ' '
            for axe, arg in zip(axes, args):
                line += axe + ' ' + str(arg) + ' '
            self.current_command += 1
            g_file.write(line)
            g_file.write('\n')

    def print_g_file_comment(self, text):
        with open(self.gcode_file_abs_name, 'a+') as g_file:
            g_file.write('(')
            g_file.write(text)
            g_file.write(')')
            g_file.write('\n')
    
    def convert_line_based(self, line_data):
        for point in line_data:
            if point[0] != 'z':
                self.line(point[0], point[1])
            else:
                if point[1] == 'z_pass':
                    self.go_to_z(self.current_z - self.z_pass)
                elif point[1] == 'z_safe':
                    self.go_z_safe()
                elif point[1] == 'z_go':
                    self.go_to_z(-point[2])


if __name__ == "__main__":
    gco = G_Objects(do_by_in_out='inside')
    hole_1 = glb.Hole(0, 20, 100, 35, m.pi / 18)
    hole_2 = glb.Hole(0, 120, 100, 25, m.pi / 9)
    hole_3 = glb.Hole(0, 220, 100, 20, 0)
    hole_4 = glb.Hole(0, 320, 100, 25, m.pi / 9)
    hole_5 = glb.Hole(0, 420, 100, 35, m.pi / 18)
    line_bb1 = glb.Line(50 , 20, 37, 500, [hole_1, hole_2, hole_3, hole_4, hole_5], 1, 19, 1)
    line_bb2 = glb.Line(100 , 20, 37, 500, [hole_1, hole_2, hole_3, hole_4, hole_5], 1, 19, 1)
    line_bb1.compute_points()
    line_bb2.compute_points()
    gco.convert_line_based(line_bb1.position_list)
    gco.convert_line_based(line_bb2.position_list)
    
