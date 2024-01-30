from functions import calculate_angle, angle_of_singleline, distance


def camside(markers) :
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

    # If bool True -> no problem can check the problem with a lower priority
    if no_pb : 

        # Feet on the floor
        # Watch if heel and toe on the same horizontal line
        error_toe_heel = 0.03 # Error when we assume not a good position
        diff_toe_heel = heel_left[1]-toe_left[1] # Using specific markers to measure the position of heels and toes
        
        if abs(diff_toe_heel) > error_toe_heel :
            # Found a problem so bool -> False
            no_pb = False 
            # If - : heels ont he floor
            if diff_toe_heel < 0 : 
                # Number of priority
                pb_int = 1
            # If + : toes on the floor
            else :
                pb_int = 2

        else :
            # No prblem -> bool True : continue to check problems
            no_pb = True
    
    # Next problem
    if no_pb : 
        
        # Angle of the head 
        diff_regard = ear_left[1] - eye_left[1]
        error_tete = 0.01

        if abs(diff_regard) > error_tete :
            no_pb = False 
            # If - : Head up
            if diff_regard < 0 : 
                pb_int = 5
            # If + : Head down
            else :
                pb_int = 6
        else :
            no_pb = True
                                    
    # if no_pb : 
        
    #     # Head too much forward -> " do double chin"

    #     error_tete_avant = 170 # degrees
    #     ang_tete_av = calculate_angle(ear_left,shoulder_left, hip_left)
    
    #     # If ang inf head too much forward
    #     if ang_tete_av < error_tete_avant :
    #         no_pb = False 
    #         pb_int = 9
    #     else :
    #         no_pb = True
    
                 
        
    if no_pb : 
            # Alignment shoulders
            error_sho_dist = 0.04
            diff_sho = distance(shoulder_right[0], shoulder_right[1], shoulder_left[0], shoulder_left[1])
            signe_diff_sho = shoulder_right[0] - shoulder_left[0]
            
            if abs(diff_sho) > error_sho_dist :
                no_pb = False 
                # If - : right shoulder in front
                if signe_diff_sho < 0 :
                    pb_int = 13
                # If + : left shoulder in front 
                else : 
                    pb_int = 12
            else :
                no_pb = True  
    
    
    if no_pb : 
    # Alignment hips
        error_hip_dist = 0.05
        diff_hip = distance(hip_right[0], hip_right[1], hip_left[0], hip_left[1])
        signe_diff_hip = hip_right[0] - hip_left[0]
        
        if abs(diff_hip) > error_hip_dist :
            no_pb = False 
            # If - : right hip in front
            if signe_diff_hip < 0 :
                pb_int = 17
            # If + : left hip in front
            else : 
                pb_int = 16
        else :
            no_pb = True



    if no_pb :
    # Alignment knees
        error_knees_dist = 0.05
        diff_knees = distance(knee_right[0], knee_right[1], knee_left[0], knee_left[1])
        signe_diff_knee = knee_right[0] - knee_left[0]
        
        if abs(diff_knees) > error_knees_dist :
            no_pb = False 
            # If - : right knee in front
            if signe_diff_knee < 0 :
                pb_int = 20
            # If + : left knee in front
            else : 
                pb_int = 21
        else :
            no_pb = True

    if no_pb : 
        # Distance toe and knee 
        error_dist_toe_knee = - 0.01
        diff_toe_knee = knee_left[0]- toe_left[0]
        
        # If inferior to threshold : knee go back
        if diff_toe_knee < error_dist_toe_knee :
            no_pb = False 
            pb_int = 24
        else :
            no_pb = True

    if no_pb : 
        # Difference angle truck line and tibia line
        error_tronc_tibia = 20 #degrees
        angle_back_knee_left = calculate_angle(hip_left, knee_left, ankle_left)
        angle_front_hip_left = calculate_angle(shoulder_left, hip_left, knee_left)
        diff_angle_tronc_tib = angle_back_knee_left - angle_front_hip_left
        
        # If too big diff between angles : problem
        if abs(diff_angle_tronc_tib) > error_tronc_tibia :
            no_pb = False 
            # If + : straighten
            if diff_angle_tronc_tib > 0 : 
                pb_int = 25
            # If - : tilt
            else : 
                pb_int = 26

        else :
            no_pb = True

    return pb_int