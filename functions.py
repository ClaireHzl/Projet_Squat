import math
import numpy as np
from datetime import datetime
import cv2
import mediapipe as mp
import time

#function to write the video with landmarks in the current directory
def video_init(cap) : 
    #inverted width and height because of rotated image
    height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    #the name of the video will be set with the date and time
    out = cv2.VideoWriter(f'squat_{datetime.now().strftime("%d%m%y_%H%M")}.mp4', fourcc, 10.0, size, True)
    return out

#function to initialize the image processing before getting the landmarks
def landmarks_init (cap, pose):
    ret, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


## Function to determine which side is closer to the camera 
def get_side(landmarks, mp_pose) :
    if landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y < landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y  : 
        ind_side = 1
        ind_other_side = 0
        side = 'left side'
        other_side = 'right side'
    else : 
        ind_side= 0
        ind_other_side = 1
        side = 'right side'
        other_side = 'left side'
    return ind_side, ind_other_side, side, other_side



def calibration (mp_pose, pose, cap, start) : 
    #initialization of empty tabs
    eye_right, eye_left, ear_right, ear_left, nose_init, shoulder_right, shoulder_left, hip_left, hip_right, knee_right, knee_left, ankle_right, ankle_left, heel_right, heel_left, foot_right, foot_left  = ([] for i in range(17))

    #measures of landmarks for 5 seconds 
    while (time.time()-start)< 5  : 
        image, results = landmarks_init (cap, pose)
        
        # Extract landmarks on each frame 
        try:
            landmarks = results.pose_landmarks.landmark
            
            nose_init.append([landmarks[mp_pose.PoseLandmark.NOSE.value].x,landmarks[mp_pose.PoseLandmark.NOSE.value].y])
            # Get left coordinates 
            shoulder_left.append([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
            hip_left.append([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y])
            knee_left.append([landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y])
            ankle_left.append([landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y])
            heel_left.append([landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y])
            foot_left.append([landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y])
            ear_left.append([landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y])
            eye_left.append([landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].y])
            
            # Get right coordinates
            shoulder_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])
            hip_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y])
            knee_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y])
            ankle_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y])
            heel_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y])
            foot_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y])
            ear_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y])
            eye_right.append([landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].y])
        
        except:
            pass

    #record the median of each coordinates           
    eye_init = [np.median(eye_right, axis = 0).tolist(), np.median(eye_left, axis = 0).tolist()]
    ear_init = [np.median(ear_right, axis = 0).tolist(), np.median(ear_left, axis = 0).tolist()]
    nose_init = np.median(nose_init, axis = 0).tolist()
    shoulder_init = [np.median(shoulder_right, axis = 0).tolist(), np.median(shoulder_left, axis = 0).tolist()]
    hip_init = [np.median(hip_right, axis = 0).tolist(), np.median(hip_left, axis = 0).tolist()]
    knee_init = [np.median(knee_right, axis = 0).tolist(), np.median(knee_left, axis = 0).tolist()]
    ankle_init = [np.median(ankle_right, axis = 0).tolist(), np.median(ankle_left, axis = 0).tolist()]
    heel_init = [np.median(heel_right, axis = 0).tolist(), np.median(heel_left, axis = 0).tolist()]
    foot_init = [np.median(foot_right, axis = 0).tolist(), np.median(foot_left, axis = 0).tolist()]
    
    #definition of the closer side and the distance used to normalize every other distances 
    ind_side, ind_other_side, side, other_side = get_side(landmarks, mp_pose)
    normal_dist = math.sqrt((shoulder_init[ind_side][0] - heel_init[ind_side][0]) ** 2 + (shoulder_init[ind_side][1] - heel_init[ind_side][1]) ** 2)

    #Measures of initial line orientations
    ligne_feet_init = angle_of_singleline(foot_init[0], foot_init[1])
    ligne_gaze_init = [angle_from_footline(nose_init, ear_init[0], ligne_feet_init), angle_from_footline(nose_init, ear_init[1], ligne_feet_init)]
    ligne_ear_init = angle_from_footline(ear_init[0],ear_init[1], ligne_feet_init)
    ligne_shoulders_init = angle_from_footline(shoulder_init[0],shoulder_init[1], ligne_feet_init)
    ligne_hips_init= angle_from_footline(hip_init[0],hip_init[1], ligne_feet_init)
    ligne_knees_init = angle_from_footline(knee_init[0], knee_init[1], ligne_feet_init)

    #Measure of initial angle
    angle_head_init = [calculate_angle(nose_init, ear_init[0],shoulder_init[0]), calculate_angle(nose_init,ear_init[1], shoulder_init[1])]

    #Measure of initial distances 
    dist_ear_should_x_init = [abs(ear_init[0][0] - shoulder_init[0][0])/normal_dist, abs(ear_init[1][0]- shoulder_init[1][0])/normal_dist]
    dist_shoulder_init = distance(shoulder_init[0], shoulder_init[1], normal_dist)
    dist_hip_init = distance(hip_init[0], hip_init[1], normal_dist)
    dist_knee_init = distance(knee_init[0], knee_init[1], normal_dist)
    dist_feet_init=distance(foot_init[0], foot_init[1], normal_dist)

    return ind_side, ind_other_side, side, other_side, normal_dist, nose_init, shoulder_init, heel_init, ligne_ear_init, dist_ear_should_x_init, dist_shoulder_init, dist_hip_init, dist_knee_init, ligne_gaze_init, ligne_shoulders_init, ligne_hips_init, ligne_knees_init, ligne_feet_init, angle_head_init



#real-time parameter calculation on each frame
def realtime_param (landmarks, mp_pose, normal_dist, ligne_feet_init) :
    #face 
    #eye = [[landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].y],[landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].y]]
    ear = [[landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y],[landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]]
    nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,landmarks[mp_pose.PoseLandmark.NOSE.value].y]

    #superior limb
    shoulder = [[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]]

    # inferior limb
    hip = [[landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]]
    knee = [[landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]]
    
    #feet
    ankle = [[landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]]
    heel = [[landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]]
    foot = [[landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]]

    #Measures of different line orientations, according to the initial orientation of the feet
    ligne_gaze = [angle_from_footline(nose, ear[0], ligne_feet_init), angle_from_footline(nose, ear[1], ligne_feet_init)]
    ligne_shoulders = angle_from_footline(shoulder[0],shoulder[1], ligne_feet_init)
    ligne_hips= angle_from_footline(hip[0],hip[1], ligne_feet_init)
    ligne_knees = angle_from_footline(knee[0], knee[1], ligne_feet_init)
    ligne_feet = angle_from_footline(foot[0], foot[1], ligne_feet_init)
    ligne_ear = angle_from_footline(ear[0],ear[1], ligne_feet_init)

    #Measure of segment angles
    angle_knee = [calculate_angle(hip[0],knee[0], ankle[0]), calculate_angle(hip[1],knee[1], ankle[1])]
    angle_hip = [calculate_angle(shoulder[0],hip[0],knee[0]), calculate_angle(shoulder[1],hip[1],knee[1])]
    angle_head = [calculate_angle(nose,ear[0],shoulder[0]), calculate_angle(nose, ear[1], shoulder[1])]
    
    #Measures of distances (normalized standardized according to heel-shoulder height)
    dist_ear_should_x = [abs(ear[0][0] - shoulder[0][0])/normal_dist, abs(ear[1][0]- shoulder[1][0])/normal_dist]
    dist_shoulder = distance(shoulder[0], shoulder[1], normal_dist)
    dist_hip = distance(hip[0], hip[1], normal_dist)
    dist_knee = distance(knee[0], knee[1], normal_dist)
    dist_heel = distance(heel[0], heel[1], normal_dist)
    dist_feet=distance(foot[0], foot[1], normal_dist)

    return ear, nose, shoulder, hip, knee, ankle, heel, foot, ligne_gaze, ligne_shoulders, ligne_hips, ligne_knees, ligne_feet, ligne_ear, angle_knee, angle_hip, angle_head, dist_ear_should_x, dist_shoulder, dist_hip, dist_knee, dist_heel, dist_feet


## Angle, distance and orientation calculation functions

#Angle in degrees between 3 points
def calculate_angle(a,b,c):
    a = np.array(a) # Proximal point
    b = np.array(b) # Intersection
    c = np.array(c) # Distal point
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle >180.0:
        angle -= 360
    elif angle < -180.0 : 
        angle += 360
        
    return angle

#between 2 points and the horizontal
def angle_of_singleline(point1, point2):
    x_diff = point2[0] - point1[0]
    y_diff = point2[1] - point1[1]
    return math.degrees(math.atan2(y_diff, x_diff))

#between 2 points and the initial feet line
def angle_from_footline(point1,point2, ligne_feet_init) : 
    angle = angle_of_singleline(point1, point2) - ligne_feet_init 
    if angle >180.0:
        angle -= 360
    elif angle < -180.0 : 
        angle += 360
    return angle


#normalized distance between 2 points 
def distance(point1, point2, normal_dist):
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist/normal_dist



def vib_live(pbint, ligne_shoulders, ligne_shoulders_init, dist_shoulder, dist_shoulder_init,  dist_hip, dist_hip_init, ligne_hips_init, ligne_hips, angle_knee, ind_other_side, angle_hip, dist_knee, dist_knee_init ) :
    max_norm = [255,400, 400] #maximal value of vibration for back, right_knee, left_knee
    min_norm= [150,100,100] #minimal value of vibration for back, right_knee, left_knee
    pb_novib = [1,2,3,4,5,6,7,8,19] #problems without vibration feedback
    pb_vib_inv = [12,14,15,18] #back problems with vibration feedback with a range in descending order

    #defining the id of the corresponding vibrator 
    if 21<=pbint<=22 : vib_id = 2 #left knee
    elif pbint == 23 or pbint ==20 : vib_id = 1 #right knee 
    else : vib_id = 0 #back
    
    ## Defining the value of the vibration
    if pbint in pb_novib : vib = 0
    
    #crit is the error criteria and inter is the range of errors [min,max]
    else : 
        if pbint== 9 or pbint == 10 : 
            crit = abs(abs(ligne_shoulders) - abs(ligne_shoulders_init))
            inter = [7, 10]

        elif pbint == 11 or pbint == 12 :
            crit = dist_shoulder / dist_shoulder_init
            if pbint == 11 : inter = [1.05, 1.1]
            else : inter = [0.6,0.9] 
            
        elif pbint == 13 or pbint == 14 :
            crit = dist_hip/dist_hip_init
            if pbint == 13 : inter = [1.07, 1.1]
            else : inter = [0.75, 0.85] 
        
        elif pbint == 15 or pbint == 16 :
            crit = ligne_hips_init - ligne_hips
            if pbint == 15 : inter = [-8, -2.5] 
            else :inter = [6, 10]

        elif pbint == 17 or pbint == 18 :
            crit = abs(angle_knee[ind_other_side]) - abs(angle_hip[ind_other_side])
            if pbint == 17 : inter = [30, 60]
            else : inter = [-40, 0]

        elif pbint == 20 or pbint == 21 or pbint == 22 or pbint == 23 :
            crit = dist_knee/dist_knee_init
            if pbint == 20 or pbint == 21 : inter = [1.3, 0.8] 
            else : inter =  [1.6, 2.1]

        #normalization of the error range between 100 and 255 for the back and 100 and 400 for the knees
        vib = min_norm[vib_id] + (crit -inter[0]) * (max_norm[vib_id]-min_norm[vib_id])/(inter[1]-inter[0])
        if pbint in pb_vib_inv : vib = max_norm[vib_id] - vib
        #normalization of the error range between 100 and 255 for the back and 100 and 400 for the knees
        # if pbint in pb_vib : vib = min_norm + (crit -inter[0]) * ((max_norm-min_norm)/(inter[1]-inter[0]))
        # elif pbint in pb_vib_inv : vib = max_norm - (min_norm +(crit -inter[1]) * ((max_norm-min_norm)/(inter[0]-inter[1])))
        # elif pbint in pb_knees : vib = (100+(inter[1]-crit)*300/(inter[1]- inter[0]))

        #make sure to have values between 0 and 255, and setting the vibration to zero if it's under the min
        vib = int(np.clip(vib, 0, max_norm[vib_id]))
        #if vib < min_norm : vib = 0

    return str(vib), vib_id #intensity of the vibrator and corresponding vibrator id 
