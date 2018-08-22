'''
Created on Apr 26, 2017

@author: profitrolle
'''

import g_objects

class Sphere_maker():

    def __init__(self):
        # object creator
        self.object_creator = g_objects.G_Objects(
            speed_fast=1000,
            speed_mill=500,
            safe_z=2,
            z_pass=1,
            tool_diameter=16,
            do_by_in_out='on_line',
            output_file='rondoudou.gco')
        self.object_creator.make_sphere(0, 0, 61)

if __name__ == '__main__':
    bo = Sphere_maker()