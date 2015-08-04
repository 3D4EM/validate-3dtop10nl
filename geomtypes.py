import math

TOLERANCE = 1e-8

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


def cmp_doubles(a, b):
    if abs(a-b) <= TOLERANCE:
        return 0
    else:
        if a - b > 0:
            return 1
        else:
            return -1
