import math
import numpy

while(True):
    ang = int( input("ENTER ANG: ") )
    s = -1*numpy.sign(ang)

    if(abs(ang) > 180 and abs(ang) < 360):
        ang += 360*s
    if(abs(ang) >= 360):
        ang -= 360*numpy.sign(ang)

    print(ang)