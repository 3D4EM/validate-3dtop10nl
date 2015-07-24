import sys
import os
import fiona
from shapely.geometry import Polygon
from shapely.geometry import asShape
from shapely.geometry import mapping


INFILE = '/Users/hugo/data/3dtop10nl/25ez1.gdb'
LAYERS = ['terreinVlak_3D_LOD0', 'wegdeelVlak_3D_LOD0', 'waterdeelVlak_3D_LOD0']
# print fiona.listlayers(INFILE)

def main():
    for l in LAYERS:
        print "Processing", l
        c = fiona.open(INFILE, 'r', driver='OpenFileGDB', layer=l)

        #-- store the geometries in a list (shapely objects)
        lsPolys = []
        for each in c:
            lsPolys.append(asShape(each['geometry']))

        #-- Find and print the number of geometries
        print "# MultiPolygons:", len(c)
        totaltr = 0
        for mp in lsPolys:
            totaltr += len(mp)
        print "# triangles:", totaltr
        

        #-- validate individually each triangle
        invalidtr = 0
        verticaltr = 0
        for mp in lsPolys:
            # print mp.geom_type, len(mp)
            for p in mp:
                if (validate_one_triangle(p) == False):
                    invalidtr += 1
                if (p.area == 0.0): #-- since shapely's area() ignores Z values
                    verticaltr += 1
        print "# invalid triangle(s):", invalidtr
        print "# vertical triangle(s):", verticaltr
        sys.exit()

        #-- validate individually each top10 polygon
        invalidmp = 0
        for mp in lsPolys:
            if (validate_one_top10polygon(mp) == False):
                invalidmp += 1
        print "# invalid area(s):", invalidtr
        


def validate_one_triangle(tr):
    if len(list(tr.exterior.coords)) != 4:
        return False
    if len(tr.interiors) != 0:
        return False
    return True

def validate_one_top10polygon(mp):
    return True

if __name__ == '__main__':
    main()



