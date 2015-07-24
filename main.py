import sys
import os
import fiona
import math
from shapely.geometry import Polygon
from shapely.geometry import asShape
from shapely.geometry import mapping


INFILE = '/Users/hugo/data/3dtop10nl/25ez1.gdb'
LAYERS = ['terreinVlak_3D_LOD0', 'wegdeelVlak_3D_LOD0', 'waterdeelVlak_3D_LOD0']
# print fiona.listlayers(INFILE)


TOLERANCE = 1e-8

def cmp_doubles(a, b):
    if abs(a-b) <= TOLERANCE:
        return 0
    else:
        if a - b > 0:
            return 1
        else:
            return -1

class Point3d:
    def __init__(self, cx=0.0, cy=0, cz=0, cid=0):
        self.x = float(cx)
        self.y = float(cy)
        self.z = float(cz)
        self.id = int(cid)
    def __repr__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)
    def __str__(self):
        return "{:f}".format(self.x) + "," + "{:f}".format(self.y) + "," + "{:f}".format(self.z)
    def __getitem__(self, index):
        if index < 0 or index > 2:
            raise Exception("out of bound for Point access.")
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        if index == 2:
            return self.z
    def __eq__(self, other):
        if (cmp_doubles(self.x, other.x) == 0 and 
            cmp_doubles(self.y, other.y) == 0 and
            cmp_doubles(self.z, other.z) == 0 ):
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __neg__(self):
        self.x = -(self.x)
        self.y = -(self.y)
        self.z = -(self.z)
        return self
    def copy(self):
        return Point(self.x, self.y, self.z)

def main():
    for l in LAYERS:
        print "Processing", l
        c = fiona.open(INFILE, 'r', driver='OpenFileGDB', layer=l)

        #-- store the geometries in a list (shapely objects)
        lsPolys = []
        for each in c:
            lsPolys.append(asShape(each['geometry']))

        # #-- Find and print the number of geometries
        # print "# MultiPolygons:", len(c)
        # totaltr = 0
        # for mp in lsPolys:
        #     totaltr += len(mp)
        # print "# triangles:", totaltr
        
        # validate_individual_triangles(lsPolys)
        # vertical_triangles(lsPolys)
        validate_individual_regions(lsPolys)


def vertical_triangles(lsPolys):
    verticaltr = 0
    for mp in lsPolys:
        for p in mp:
            if (p.area == 0.0): #-- since shapely's area() ignores Z values
                verticaltr += 1
    print "# vertical triangle(s):", verticaltr

    
def validate_individual_triangles(lsPolys):
    #-- validate individually each triangle
    invalidtr = 0
    for mp in lsPolys:
        for p in mp:
            if (validate_one_triangle(p) == False):
                invalidtr += 1
    print "# invalid triangle(s):", invalidtr


def validate_individual_regions(lsPolys):
    #-- validate individually each top10 polygon
    invalidmp = 0
    for mp in lsPolys:
        if (validate_one_region(mp) == False):
            invalidmp += 1
        sys.exit()
    print "# invalid area(s):", invalidtr


def validate_one_triangle(tr):
    if len(list(tr.exterior.coords)) != 4:
        return False
    if len(tr.interiors) != 0:
        return False
    return True

def validate_one_region(mp):
    lsNodes = []
    lsTr = []
    for p in mp:
        tr = []
        for i in range(3):
            temp = Point3d(p.exterior.coords[i][0], p.exterior.coords[i][1], p.exterior.coords[i][2])
            if lsNodes.count(temp) == 0:
                lsNodes.append(temp)
                temp.id = len(lsNodes) - 1
                tr.append(temp.id)
            else:
                tr.append(lsNodes.index(temp))
        lsTr.append(tr)
    print "nodes:", len(lsNodes)
    print "tr:", len(lsTr)

    
    return True

if __name__ == '__main__':
    main()



