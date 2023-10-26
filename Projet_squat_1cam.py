import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
import math
import numpy as np
import sys
import time



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


## on définit les fonctions de calcul d'angle entre 2 points, avec l'horizontale et de distance : 

#entre 3 points
def calculate_angle(a,b,c):
    a = np.array(a) # Point proximal
    b = np.array(b) # intersection
    c = np.array(c) # Point distal
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

#entre 2 points et l'horizontale 
def angle_of_singleline(point1, point2):
    x_diff = point2[0] - point1[0]
    y_diff = point2[1] - point1[1]
    return math.degrees(math.atan2(y_diff, x_diff))

#distance entre 2 points 
def distance(point1, point2):
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist



# on utilise une capture d'image par webcam 
#on utilise le nombre qui correspond à l'ordre où on a branché les cams
cap = cv2.VideoCapture(0)


# Curl counter variables
counter = 0 
text_pb= None

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
size = (width, height)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('your_video.mp4', fourcc, 10.0, size, True)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    tabsol = []
    start = time.time()

#     #initialisation
#     while (time.time()-start)< 10  : 
#         ret, frame = cap.read()
#         # Recolor image to RGB
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         # Make detection
#         results = pose.process(image)
#         # Recolor back to BGR
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
#         # Extract landmarks
#         try:
#             landmarks = results.pose_landmarks.landmark
#             rightfoot = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]
#             leftfoot = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
#             tabsol.append(angle_of_singleline(rightfoot, leftfoot))
#         except:
#             pass
#     anglesol = np.mean(tabsol)


    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
    
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            #visage 
            righteye = [landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].y]
            lefteye = [landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].y]
            rightear = [landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y]
            leftear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            righteyenose = [(righteye[0]+nose[0])/2, (righteye[1]+nose[1])/2]
            lefteyenose = [(lefteye[0]+nose[0])/2, (lefteye[1]+nose[1])/2]

            #membre sup
            rightshoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            leftshoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        
            # membre inf
            righthip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            lefthip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            rightknee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            leftknee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            
            #pieds
            rightankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            leftankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            rightheel = [landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y]
            leftheel = [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]
            rightfoot = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]
            leftfoot = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
           
            
            ## Calculate angle

            #Lignes du regard, épaules, hanches et genoux : doivent être à 0°
            ligne_gaze=angle_of_singleline(lefteyenose,leftear)
            #ligne_gaze = angle_of_singleline(righteye, lefteye) plutôt pour cam de face
            ligne_shoulders = angle_of_singleline(rightshoulder,leftshoulder)
            ligne_hips= angle_of_singleline(righthip,lefthip)
            ligne_knees = angle_of_singleline(rightknee, leftknee)

            #Angles des segments
            angle_knee = [calculate_angle(righthip,rightknee, rightankle), calculate_angle(lefthip,leftknee, leftankle)]
            angle_head = [calculate_angle(rightear,rightshoulder, righthip), calculate_angle(leftear, leftshoulder, lefthip)]
            angle_feet = [calculate_angle(righthip,rightheel, rightfoot), calculate_angle(lefthip, leftheel, leftfoot)]
            
            #distances 
            dist_shoulder = distance(rightshoulder, leftshoulder)
            dist_hip = distance(righthip, lefthip)
            dist_knee = distance(rightknee, leftknee)
            dist_feet=distance(rightfoot, leftfoot)
            long_feet= [distance(rightheel, rightfoot), distance(leftheel,leftfoot)]


            # Visualize angle 
            #angle du genou 
            cv2.putText(image, str(ligne_gaze), 
                           tuple(np.multiply(lefteye, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (79, 121, 66), 2, cv2.LINE_AA
                                )
            
            #angle de hanche 
            cv2.putText(image, str(ligne_shoulders), 
                           tuple(np.multiply(leftshoulder, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            

            ### Les différents problèmes

            text_pb = "good"
            
            ##tête 
            if ligne_gaze > 10 : 
                text_pb = f"NOT GOOD, tête inclinée : {ligne_gaze}"
                #ajouter voix "relève la tête"

            #déterminer le threshold
            threshold = 150
            if angle_head[1] < threshold : 
                text_pb = f"NOT GOOD, tête trop avancée : {angle_head[1]}"
                #ajouter voix "rentre le menton"
            
            ##épaules
            if abs(ligne_shoulders) > 10 : 
                text_pb = f"NOT GOOD épaules, {ligne_shoulders}"
                # ajouter voix "épaules droites" + vibration haut du dos
            
            if dist_shoulder > threshold : 
                text_pb = f"NOT GOOD épaules, {dist_shoulder}"
                # ajouter voix "tiens toi droit" + vibration haut du dos

            ## hanches
            if abs(ligne_hips) > 10 : 
                text_pb = f"NOT GOOD hanches, {ligne_hips}"
                # ajouter voix "hanches parallèles au sol " + vibration bas du dos
            
            if dist_hip > threshold : 
                text_pb = f"NOT GOOD hanches, {dist_hip}"
                # ajouter voix "hanche face aux épaules" + vibration bas du dos
        
            ## genoux
            if abs(ligne_knees) > 10 : 
                text_pb = f"NOT GOOD genoux, {ligne_knees}"
                # ajouter voix "genoux parallèles au sol " + vibration genoux 
            
            if dist_knee > threshold : 
                text_pb = f"NOT GOOD genoux, {dist_knee}"
                # ajouter voix "genou face aux hanches" + vibration genoux
            
            ## pieds
            if angle_feet[1]> threshold : 
                text_pb = f"NOT GOOD talons, {angle_feet[1]}"
                # ajouter voix "gardez les talons au sol"
            
            if abs(long_feet[0] - long_feet[1]) >threshold : 
                text_pb = f"NOT GOOD pieds non alignés"
                # ajouter voix "gardez les pieds droits"

            
            # #genoux à l'extérieur des chevilles (plutôt pour une cam)
            # if abs(angle_knee[0]- angle_knee[1]) > 10 : 
            #     diffknee = angle_knee[0] - angle_knee[1]
            #     if diffknee > 0 : 
            #         text_pb = "genou droit à l'intérieur"
            #         #ajouter vibration au genou droit selon la valeur de diffknee
            #     else : 
            #         text_pb = "genou gauche à l'intérieur"
            #         #ajouter vibration au genou gauche selon la valeur de diffknee
            



            # else : text_pb = f"GOOD, {anglesol}"


        except:
            pass
        

        # Render squat counter
        # Setup status box
        cv2.rectangle(image, (0,0), (500,20), (255,255,255), -1) # couleur blanche
        
        # Dire le problème 
        cv2.putText(image, f'{text_pb}', (15,10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

        
        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 )               
        
        out.write(image)
        cv2.imshow('Squat Correction',image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    #out.release()
    cv2.destroyAllWindows()
    
#destroyAllWindows()