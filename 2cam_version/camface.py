'''
Get most important problem of the face camera
(First problem of camside more detailled)
'''

from functions import calculate_angle, angle_of_singleline, distance

def camface(markers):
    # Get coordonates of the Mediapipe markers for each part of the body wanted
    nose = markers[0]

    # Get coordinates left 
    shoulder_left = markers[1]
    hip_left = markers[2]
    knee_left = markers[3]
    ankle_left = markers[4]
    heel_left = markers[5]
    toe_left = markers[6]
    ear_left = markers[7]
    eye_left =  markers[8]

    # Get coordinates right
    shoulder_right = markers[9]
    hip_right = markers[10]
    knee_right = markers[11]
    ankle_right = markers[12]
    heel_right = markers[13]
    toe_right = markers[14]
    ear_right =  markers[15]
    eye_right = markers[16]

    # Init no problem
    no_pb = True
    pb_int = 0

    if no_pb : 
        # Feet spreading
        diff_toe_heel_r = toe_right[0] - heel_right[0]
        diff_toe_heel_l = toe_left[0] - heel_left[0]
        error_toe_heel = 0.02

        if diff_toe_heel_r >  - error_toe_heel or diff_toe_heel_l <  error_toe_heel :
            no_pb = False 
            # If sup error : open right foot
            if diff_toe_heel_r >  - error_toe_heel : 
                pb_int = 3
            # If inf error : open left foot
            if diff_toe_heel_l <  error_toe_heel :
                pb_int = 4

        else :
            no_pb = True   
        
        

    if no_pb : 
        # Difference head angle 
        diff_ang_tete = ear_left[1] - ear_right[1]
        error_ang_tete = 0.025

        if abs(diff_ang_tete) > error_ang_tete :
            no_pb = False 
            # If - : straighten head left
            if diff_ang_tete < 0 : 
                pb_int = 7
            # If + : straighten head right
            else :
                pb_int = 8
        else :
            no_pb = True        
        
    
                        
    if no_pb : 
        # Difference shoulder too high
        diff_shoulder_f = shoulder_left[1] - shoulder_right[1]
        error_shoulder_f = 0.03

        if abs(diff_shoulder_f) > error_shoulder_f :
            no_pb = False 
            # If - : lower left shoulder
            if diff_shoulder_f< 0 : 
                pb_int = 10
            # If + : lower rigth shoulder
            else :
                pb_int = 11
        else :
            no_pb = True 
        
        

    if no_pb : 
        # Difference hip too high
        diff_hip_f = hip_left[1] - hip_right[1]
        error_hip_f = 0.01

        if abs(diff_hip_f) > error_hip_f :
            no_pb = False 
            # If - : lower left hip
            if diff_hip_f < 0 : 
                pb_int = 14
            # If + : lower right hip
            else :
                pb_int = 15
        else :
            no_pb = True 
        
                
        
    if no_pb : 
        # Difference knee too high 
        diff_knee_f = knee_left[1] - knee_right[1]
        error_knee_f = 0.01

        if abs(diff_knee_f) > error_knee_f :
            no_pb = False 
            # If - : lower left knee
            if diff_knee_f< 0 : 
                pb_int = 18
            # If + : lower right knee
            else :
                pb_int = 19
        else :
            no_pb = True 
        
                        
            
    if no_pb :
    # If too big difference between knee angles -> spread the one with the biggest angle
        ang_knee_r = calculate_angle(hip_right,knee_right,heel_right)
        ang_knee_l = calculate_angle(hip_left,knee_left,heel_left)
        diff_ang_knee = abs(ang_knee_l-ang_knee_r)
        error_ang_knee = 12

        if diff_ang_knee > error_ang_knee : 
            no_pb = False 
            # If ang_left > ang_right : spread knee left
            if ang_knee_l > ang_knee_r :
                pb_int = 22
            # If ang_left < ang_right : spread knee right
            else :
                pb_int = 23

        else : 
            no_pb = True

    return pb_int


