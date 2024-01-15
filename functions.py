import math
import numpy as np

## on définit les fonctions de calcul d'angle entre 2 points, avec l'horizontale et de distance : 

#entre 3 points
def calculate_angle(a,b,c):
    a = np.array(a) # Point proximal
    b = np.array(b) # intersection
    c = np.array(c) # Point distal
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle >180.0:
        angle -= 360
    elif angle < -180.0 : 
        angle += 360
        
    return angle

#entre 2 points et l'horizontale 
def angle_of_singleline(point1, point2):
    x_diff = point2[0] - point1[0]
    y_diff = point2[1] - point1[1]
    return math.degrees(math.atan2(y_diff, x_diff))

# entre 2 points et la ligne des pieds
def angle_from_footline(point1,point2, ligne_feet_init) : 
    angle = angle_of_singleline(point1, point2) - ligne_feet_init 
    if angle >180.0:
        angle -= 360
    elif angle < -180.0 : 
        angle += 360
    return angle


#distance entre 2 points 
def distance(point1, point2, normal_dist):
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist/normal_dist