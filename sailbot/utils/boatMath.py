"""
Math functions useful for sailbotting
"""
import math
# TODO: CONVERT
"""
math.radians() - convert degrees to radians
math.degrees() - convert radians to degrees
"""

def getCoordinateADistanceAlongAngle(distance, angle):
    print("write function")
    return "lat, long"

def distanceInMBetweenEarthCoordinates(lat1, lon1, lat2, lon2):
    earthRadiusKm = 6371

    dLat = math.radians(lat2-lat1)
    dLon = math.radians(lon2-lon1)

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return earthRadiusKm * c * 1000

def computeNewCoordinate(lat, lon, d_lat, d_lon):
    """
    finds the gps coordinate that is x meters from given coordinate
    """
    earthRadiusKm = 6371

    d_lat /= 1000
    d_lon /= 1000

    new_lat = lat + (d_lat / earthRadiusKm) * (180/math.pi)
    new_lon = lon + (d_lon / earthRadiusKm) * (180/math.pi) / math.cos(lat * math.pi/180)

    return (new_lat, new_lon)

def angleBetweenCoordinates(lat1, lon1, lat2, lon2):
    #angle (relative to north?) from lat/long1 to lat/long2
    theta1 = math.radians(lat1)
    theta2 = math.radians(lat2)
    delta2 = math.radians(lon2 - lon1)

    y = math.sin(delta2) * math.cos(theta2)
    x = math.cos(theta1) * math.sin(theta2) - math.sin(theta1)*math.cos(theta2)*math.cos(delta2)
    brng = math.atan(y/x)
    brng *= 180/math.pi

    brng = (brng + 360) % 360

    return brng

def angleToPoint(heading, lat1, long1, lat2, long2):
    phi = math.atan2(long1-long2, lat1-lat2)

    return (360 - (math.degrees(phi) + heading + 180)) % 360

def convertDegMinToDecDeg (degMin):
    min = 0.0
    decDeg = 0.0

    min = math.fmod(degMin, 100.0)

    degMin = int(degMin/100)
    decDeg = degMin + (min/60)

    return decDeg
