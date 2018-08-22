'''
Created on Feb 5, 2018

@author: profitrolle
'''

example_json = {
    "width": 600,
    "height": 200,
    "depth": 50,
    "hole_height": 20,
    "holes": [
        {"hole_type": "x_hole", "x_position": 20, "y_position": 32, "depth": 20, "length" : 80,"height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 110, "y_position": 32, "depth": 20, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 144, "y_position": 32, "depth": 20, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 202, "y_position": 32, "depth": 20, "length" : 140, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 351, "y_position": 32, "depth": 20, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 411, "y_position": 32, "depth": 20, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 445, "y_position": 32, "depth": 20, "length" : 80, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 20, "y_position": 64, "depth": 30, "length" : 80, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 110, "y_position": 64, "depth": 30, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 144, "y_position": 64, "depth": 30, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 202, "y_position": 64, "depth": 30, "length" : 140, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 351, "y_position": 64, "depth": 30, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 411, "y_position": 64, "depth": 30, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 445, "y_position": 64, "depth": 30, "length" : 80, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 20, "y_position": 96, "depth": 40, "length" : 80, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 110, "y_position": 96, "depth": 40, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 144, "y_position": 96, "depth": 40, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 202, "y_position": 96, "depth": 40, "length" : 140, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 351, "y_position": 96, "depth": 40, "length" : 50, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 411, "y_position": 96, "depth": 40, "length" : 24, "height":20, "angle" : 0, "hole_list" : []},
        {"hole_type": "x_hole", "x_position": 445, "y_position": 96, "depth": 40, "length" : 80, "height":20, "angle" : 0, "hole_list" : []},  
    ]
}

class Hole():

    def __init__(self, hole_type='None', x_position=0, y_position=0, depth=0, length=0, height=0, angle=0, hole_list=[]):
        self.hole_type = hole_type
        self.x_position = x_position
        self.y_position = y_position
        self.depth = depth
        self.length = length
        self.height = height
        self.angle = angle
        self.hole_list = hole_list
    
    def printify(self):
        print("type : ", self.hole_type)
        print("X : ", self.x_position)
        print("Y : ", self.y_position)
        print("Depth : ", self.depth)
        print("Length : ", self.length)
        print("Heigh : ", self.height)
        print("Angle : ", self.angle)
        print("Hole list : ")        
        for hole in self.hole_list:
            print("X : ", hole.x_position)
            print("Y : ", hole.y_position)
            print("Heigh : ", self.height)
            print("Depth : ", hole.depth)
            print("Length : ", hole.length)


if __name__ == "__main__":
    holes = example_json["holes"]
    i = 0
    for hole in holes:
        print("Hole ", i)
        i+=1
        new_hole = Hole(**hole)
        new_hole.printify()
        