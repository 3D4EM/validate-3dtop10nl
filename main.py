
import sys
import os
import fiona
from geomtypes import Point3d
from shapely.geometry import Polygon
from shapely.geometry import asShape
from shapely.geometry import mapping
from shapely.ops import polygonize
from shapely.ops import cascaded_union
import subprocess

# INFILE = '/Users/hugo/data/3dtop10nl/25ez1.gdb'
INFILE = '/Users/hugo/data/3dtop10nl/37ez2.gdb'

BLAYERS = ['gebouw_3D_LOD1']
TRLAYERS = ['terreinVlak_3D_LOD0', 'wegdeelVlak_3D_LOD0', 'waterdeelVlak_3D_LOD0']

REPAIR = True        #-- automatic repair when possible
MERGEFEATURES = True #-- merging MultiPolygons based on 'TOP10_NL'

###############################################################################

def main():
    print "Input file", INFILE
    
    # validate_buildings()
    validate_triangulation()
            
    # # -- Find and print the number of geometries
    # print "# MultiPolygons:", len(dPolys)
    # totaltr = 0
    # for tid in dPolys:
    #     for each in dPolys[tid]:
    #         totaltr += len(each)
    # print "# triangles:", totaltr

    # validate_triangles(dPolys)
    # vertical_triangles(dPolys)
    # validate_regions(dPolys)


def read_input_layer(l):
    c = fiona.open(INFILE, 'r', driver='OpenFileGDB', layer=l)
    #-- store the geometries in a list (shapely objects)
    dPolys = {}
    for gid, each in enumerate(c):
        if MERGEFEATURES is True:
            k = each['properties']['TOP10_ID']
        else:
            k = gid
        if k not in dPolys:
            dPolys[k] = [asShape(each['geometry'])]
        else:
            dPolys[k].append(asShape(each['geometry']))
    return dPolys

def validate_triangulation():
    for each in TRLAYERS:
        print "Processing layer", each
        dPolys = read_input_layer(each)

        # -- Find and print the number of geometries
        print "# MultiPolygons:", len(dPolys)
        totaltr = 0
        for tid in dPolys:
            for each in dPolys[tid]:
                totaltr += len(each)
        print "# triangles:", totaltr

        validate_triangles(dPolys)
        vertical_triangles(dPolys)
        validate_regions(dPolys)


def validate_buildings():
    dPolys = read_input_layer(BLAYERS[0])
    invalidbuildings = 0
    invalidlist = []
    for tid in dPolys:
        print "----------- Validate #%s ----------" % (tid)
        if (validate_one_building(dPolys[tid]) == False):
            invalidbuildings += 1
            invalidlist.append(tid)
    print "\n"
    print "=" * 40
    print "# invalid building(s): %d/%d" % (invalidbuildings, len(dPolys))
    # print invalidlist


def validate_one_building(mp):
    isValid = True
    lsNodes = []
    lsFaces = []
    for each in mp:
        for p in each:
            idpoly = []
            for v in list(p.exterior.coords):
                temp = Point3d(v[0], v[1], v[2])
                if lsNodes.count(temp) == 0:
                    lsNodes.append(temp)
                    temp.id = len(lsNodes) - 1
                    idpoly.append(temp.id)
                else:
                    idpoly.append(lsNodes.index(temp))
            lsFaces.append(idpoly)
    #-- write POLY file
    tmp = []
    tmp.append("%d 3 0 0" % (len(lsNodes)))
    for i, n in enumerate(lsNodes):
        tmp.append("%d %f %f %f" % (i, n[0], n[1], n[2]))
    tmp.append("%d 0" % len(lsFaces))
    for i, f in enumerate(lsFaces):
        tmp.append("1 0")
        tmp.append("%d %s" % (len(f) -1, " ".join(map(str, f[:-1]))))
    tmp.append("0")
    tmp.append("0")
    polystr = "\n".join(tmp)
    fOut = open("/Users/hugo/temp/0.poly", 'w')
    fOut.write(polystr)
    fOut.close()
    #-- call val3dity binary
    exampleerrors = []
    str1 = "/Users/hugo/projects/val3dity/val3dity --xml -i /Users/hugo/temp/0.poly"
    op = subprocess.Popen(str1.split(' '),
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
    R = op.poll()
    if R:
       res = op.communicate()
       raise ValueError(res[1])
    o =  op.communicate()[0]
    if o.find('ERROR') != -1:
        i = o.find('<errorCode>')
        while (i != -1):
            if exampleerrors.count(o[i+11:i+14]) == 0:
                exampleerrors.append(o[i+11:i+14])
            tmp = o[i+1:].find('<errorCode>')
            if tmp == -1:
                i = -1
            else:
                i = tmp + i + 1
        print "ERROR: %s" % ("--".join(map(str, exampleerrors)))
        isValid = False
    return isValid


def vertical_triangles(dPolys):
    verticaltr = 0
    for tid in dPolys:
        for mp in dPolys[tid]:
            for p in mp:
                if (p.area == 0.0): #-- since shapely's area() ignores Z values
                    verticaltr += 1
    print "# vertical triangle(s):", verticaltr

    
def validate_triangles(dPolys):
    #-- validate individually each triangle
    invalidtr = 0
    for tid in dPolys:
        for mp in dPolys[tid]:
            for p in mp:
                if (validate_one_triangle(p) == False):
                    invalidtr += 1
    print "# invalid triangle(s):", invalidtr


def validate_regions(dPolys):
    #-- validate individually each top10 polygon
    invalidmp = 0
    invalidlist = []
    # toprocess = range(100)
    # toprocess = ['125232222', '125231986', '124798131']
    # toprocess = ['117116312', '125230993', '117198224']
    # for tid in toprocess:
    for tid in dPolys:
        print "----------- Validate #%s ----------" % (tid)
        if (validate_one_region(dPolys[tid]) == False):
            invalidmp += 1
            invalidlist.append(tid)
    print "\n"
    print "=" * 40
    print "# invalid region(s):", invalidmp
    print invalidlist


def validate_one_triangle(tr):
    if len(list(tr.exterior.coords)) != 4:
        return False
    if len(tr.interiors) != 0:
        return False
    return True


def validate_one_region(lsmp):
    isValid = True
    lsNodes = []
    lsTr = []
    vertical = False
    for mp in lsmp:
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
            if (p.area == 0.0):
                vertical = True
            # if REPAIR == True: #-- swap orientation of vertical triangles
            #     if (p.area == 0.0):
            #         tr[0],tr[1] = tr[1], tr[0]
            lsTr.append(tr)

    # if vertical == True:
        # print '*************'
    if REPAIR == True:
        lsTr = remove_duplicate_triangles(lsTr)

    # print lsNodes
    # print lsTr

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
                        print "ERROR: duplicate edge (%s)" % k
                        print lsNodes[a]
                        print lsNodes[b]
                        isValid = False
                        d[k] = 999
                else:
                    d[k] = 1
            else: #-- reverse order
                k = str(b) + "-" + str(a)
                # print k
                if k in d: 
                    # print d[k]
                    if d[k] == 1:
                        d[k] = 0
                    else:
                        print "ERROR: duplicate edge (%s)" % k
                        print lsNodes[b]
                        print lsNodes[a]
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



