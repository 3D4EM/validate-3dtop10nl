import sys
import os
import fiona
import math
from shapely.geometry import Polygon
from shapely.geometry import asShape
from shapely.geometry import mapping
from shapely.ops import polygonize
from shapely.ops import cascaded_union


# INFILE = '/Users/hugo/data/3dtop10nl/25ez1.gdb'
INFILE = '/Users/hugo/data/3dtop10nl/37ez1.gdb'
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
    print "Input file", INFILE
    for l in LAYERS:
        print "Processing layer '%s'" % l
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
        
        # validate_triangles(lsPolys)
        # vertical_triangles(lsPolys)
        validate_regions(lsPolys)

        sys.exit()


def vertical_triangles(lsPolys):
    verticaltr = 0
    for mp in lsPolys:
        for p in mp:
            if (p.area == 0.0): #-- since shapely's area() ignores Z values
                verticaltr += 1
    print "# vertical triangle(s):", verticaltr

    
def validate_triangles(lsPolys):
    #-- validate individually each triangle
    invalidtr = 0
    for mp in lsPolys:
        for p in mp:
            if (validate_one_triangle(p) == False):
                invalidtr += 1
    print "# invalid triangle(s):", invalidtr


def validate_regions(lsPolys):
    #-- validate individually each top10 polygon
    invalidmp = 0
    toprocess = range(100)
    for i in toprocess:
    # for i in range(len(lsPolys)):
        print "----------- Validate MultiPolygon #%d ----------" % (i)
        if (validate_one_region(lsPolys[i]) == False):
            invalidmp += 1
    print "\n"
    print "=" * 40
    print "# invalid region(s):", invalidmp


def validate_one_triangle(tr):
    if len(list(tr.exterior.coords)) != 4:
        return False
    if len(tr.interiors) != 0:
        return False
    return True


def validate_one_region(mp):
    isValid = True
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
    
    lsTr = remove_duplicate_triangles(lsTr)

    # #-- fuck up the lsTr for testing purposes
    # b = [ lsTr[4][0], lsTr[4][2], lsTr[4][1] ]
    # lsTr.append(b)

    d = {}
    for tr in lsTr:
        pairs = ( (0, 1), (1, 2), (2, 0) )
        for each in pairs:
            a = tr[each[0]]
            b = tr[each[1]]
            if (a < b): #-- good order
                k = str(a) + "-" + str(b)
                if k in d: 
                    if d[k] == -1:
                        d[k] = 0
                    else:
                        print "ERROR: duplicate edge"
                        isValid = False
                        d[k] = 999
                else:
                    d[k] = 1
            else: #-- reverse order
                k = str(b) + "-" + str(a)
                if k in d: 
                    if d[k] == 1:
                        d[k] = 0
                    else:
                        print "ERROR: duplicate edge"
                        isValid = False
                        d[k] = 999
                else:
                    d[k] = -1

    tmp = []
    for k in d:
        if ( (d[k] == -1) or (d[k] == 1) ):
            tmp.append(k)
    boundaryedges = []
    for each in tmp:
        t = each.split('-')
        boundaryedges.append( [[lsNodes[int(t[0])][0], lsNodes[int(t[0])][1]], [lsNodes[int(t[1])][0], lsNodes[int(t[1])][1]]] )
    polygons = list(polygonize(boundaryedges))    
    if len(polygons) > 1:
        re = cascaded_union(polygons)  
        if re.geom_type != 'Polygon':
            print "ERROR: disconnected area"
            isValid = False

    return isValid


def remove_duplicate_triangles(lsTr):
    allduplicated = True
    for i in range(0, len(lsTr), 2):
        if lsTr[i] != lsTr[i + 1]:
            allduplicated = False
    if allduplicated == False:
        print "ERROR: triangles are NOT duplicated :/"
        return lsTr
    else:
        # print "ERROR: all triangles are duplicated. Will fix that automatically to continue..."
        return lsTr[0:len(lsTr):2]


if __name__ == '__main__':
    main()



