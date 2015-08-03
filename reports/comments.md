
# Some preliminary comments about the validation of the 3DTOP10NL


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

## Vertical triangles

Then the vertical triangles, I count 380 of them in the
25ez1—terreinVlak_3D_LOD0 (out of 1,173,848). Will these only happen
at the borders (where 2 different classes are adjacent) of polygons of
top10nl? Or can they also be in the middle of a polygon? I assume only
for 2 different classes, and if it is so, what is the rule, to which
class is the vertical triangle assigned?


- - - 




![](2015-08-03 at 14.38.png)

