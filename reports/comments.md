
# Some comments about the validation of the 3DTOP10NL


## ALL triangles are duplicated

In the 4 tiles I've checked (`25ez1`, `37en1`, `37en21`, `37ez1`) the triangles for the class `terreinVlak_3D_LOD0` are duplicated.
Notice that I don't have ArcGIS and I am using the [OpenFileGDB](http://www.gdal.org/drv_openfilegdb.html) to read the goemetries.
But I have converted one tile to a SHP and I too get twice each triangle.

![](2015-08-03 at 08.35 2x.png)

At first I thought that you had stored each triangle twice (one in each direction) for visualisation purposes, but no each triangle is there twice in the same order.
Luckily it's always one after the other, so automatic cleaning is easy. 
All my results below implies that I first jettison the duplicates.


## often big parts are missing 

eg the rectangular areas in tile `37ez1`. Why is that? Is it "normal"?

![](2015-07-24 at 09.56.png)


## some classes don't have polygons and/or triangles

In tile `25ez1`, no triangles/polygons fill the bridges (no features in `brugWeg` and
`brugWater`).

In tile `37en1`/`37ez1`, unlike `25ez1` have features in `brugWeg`/`terreinOnder`/`brugWater`, but
these are *not* triangulated.
Where are the triangles?

![](2015-07-24 at 09.57.png)


## triangulation has several long and skinny triangles

Especially in water area, there are sometimes regular patterns where (unnecessary) points in the middle of the water exist.
Also, are these Steiner points or they are left from the simplification of the AHN2 points?
I think we should aim at avoid long and skinny triangles, especially if we want to distribute in GML (or another TXT format), then the precision could become an issue for users.

![](2015-08-03 at 08.19.png)


## features have ITC attributes

![](2015-08-03 at 08.27 2x.png)


## Vertical triangles

I count 380 of them in the tile `25ez1` for the class `terreinVlak_3D_LOD0` (out of 1,173,848). 
Will these only happen at the borders (where 2 different classes are adjacent) of polygons of top10nl?
Or can they also be in the middle of a polygon? 
I assume only for 2 different classes, and if it is so, what is the rule, to which class is the vertical triangle assigned?


## TOP10NL polygons are arbitrarily split into several features while triangulating

I can't figure out the rules, but the splitting creates unconnected parts (which we do not want I assume).
See for example these:

![](2015-08-03 at 08.33 2x.png)

![](2015-08-03 at 14.21.png)

These could be easily fixed because the `TOP10_ID` for each feature is kept, and we could merge these.
See that the unconnected parts are actually coming from a (connected) polygon in the original TOP10NL:

![](2015-08-03 at 14.22.png)

![](2015-08-03 at 14.24.png)


## how are polygons are the border handled?

In tile `25ez1` there are these cases:

![](2015-08-03 at 14.26.png)

![](2015-08-03 at 14.27.png)

And at the border of 2 other tiles:

![](2015-08-03 at 14.36.png)
![](2015-08-03 at 14.38.png)
![](2015-08-03 at 14.382.png)

What is the rule to decide where to split input polygons?


## Some results

For the tile `37ez1.gdb`:

```
Input file /Users/hugo/data/3dtop10nl/37ez1.gdb
Processing layer 'terreinVlak_3D_LOD0'
# Regions: 3,540
# triangles: 1,346,806
# invalid triangle(s): 0
# vertical triangle(s): 284
# invalid regions: 301
```

Single triangle validation means that I verify that there is indeed a triangle with 3 vertices; all valid.

8.5% of the regions are invalid, that is they are disconnected (surely because of the splitting of the TOP10NL input polygons).

<!-- [35, 50, 54, 55, 62, 76, 82, 83, 99, 105, 139, 209, 249, 259, 265, 269, 276, 287, 307, 310, 315, 329, 330, 335, 338, 349, 352, 355, 361, 362, 369, 379, 397, 402, 410, 425, 452, 470, 501, 504, 512, 515, 526, 530, 548, 565, 581, 588, 667, 674, 687, 691, 694, 711, 720, 774, 806, 813, 840, 841, 853, 882, 888, 911, 915, 916, 934, 942, 961, 964, 965, 1006, 1022, 1027, 1045, 1055, 1057, 1060, 1080, 1081, 1082, 1089, 1092, 1100, 1104, 1116, 1122, 1127, 1144, 1155, 1156, 1160, 1165, 1180, 1189, 1201, 1213, 1228, 1239, 1240, 1241, 1245, 1250, 1263, 1268, 1273, 1297, 1304, 1317, 1322, 1338, 1341, 1365, 1373, 1382, 1397, 1433, 1441, 1449, 1450, 1456, 1462, 1470, 1482, 1483, 1495, 1500, 1504, 1506, 1507, 1520, 1525, 1539, 1565, 1568, 1569, 1577, 1579, 1582, 1586, 1599, 1608, 1615, 1637, 1641, 1642, 1645, 1659, 1673, 1681, 1685, 1701, 1716, 1717, 1719, 1731, 1733, 1751, 1752, 1756, 1760, 1766, 1772, 1775, 1807, 1851, 1873, 1893, 1906, 1912, 1916, 1917, 1920, 1923, 1950, 1952, 1961, 1967, 1969, 1972, 1996, 1997, 2003, 2011, 2022, 2042, 2059, 2063, 2080, 2100, 2105, 2110, 2141, 2144, 2148, 2246, 2287, 2296, 2309, 2315, 2321, 2360, 2365, 2374, 2406, 2410, 2412, 2420, 2425, 2439, 2447, 2456, 2465, 2470, 2478, 2483, 2503, 2519, 2521, 2587, 2599, 2622, 2659, 2662, 2675, 2677, 2678, 2681, 2683, 2734, 2753, 2771, 2773, 2784, 2791, 2805, 2809, 2837, 2843, 2844, 2847, 2850, 2851, 2855, 2859, 2901, 2909, 2915, 2919, 2946, 2954, 2963, 2970, 2982, 2990, 2993, 2995, 3000, 3004, 3023, 3044, 3051, 3055, 3058, 3081, 3089, 3103, 3117, 3120, 3121, 3128, 3132, 3170, 3214, 3216, 3226, 3235, 3246, 3277, 3281, 3286, 3297, 3313, 3317, 3329, 3343, 3361, 3363, 3364, 3372, 3380, 3388, 3398, 3407, 3421, 3425, 3442, 3463, 3484, 3489, 3492] -->






