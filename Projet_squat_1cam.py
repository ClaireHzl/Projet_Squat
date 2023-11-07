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
def angle_from_footline(point1,point2) : 
    angle = angle_of_singleline(point1, point2) - ligne_feet_init 
    if angle >180.0:
        angle -= 360
    elif angle < -180.0 : 
        angle += 360
    return angle


#distance entre 2 points 
def distance(point1, point2):
    dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist/normal_dist


# on utilise une capture d'image par webcam 
#on utilise le nombre qui correspond à l'ordre où on a branché les cams
cap = cv2.VideoCapture(1)


# Curl counter variables
counter = 0 
text_pb= None

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
size = (width, height)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('your_video.mp4', fourcc, 10.0, size, True)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    eye_right, eye_left, ear_right, ear_left, nose_init, shoulder_right, shoulder_left, hip_left, hip_right, knee_right, knee_left, ankle_right, ankle_left, heel_right, heel_left, foot_right, foot_left  = ([] for i in range(17))

    start = time.time()

    #initialisation avec calibration
    while (time.time()-start)< 5  : 
        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # on définit de quel côté on est placé : 
            if landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y < landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y  : 
                ind_cote = 1
                ind_autre_cote = 0
                cote = 'cote gauche'
                autre_cote = 'cote droit'

            
            else : 
                ind_cote=0
                ind_autre_cote = 1
                cote = 'cote droit'
                autre_cote = 'cote gauche'

            nose_init.append([landmarks[mp_pose.PoseLandmark.NOSE.value].x,landmarks[mp_pose.PoseLandmark.NOSE.value].y])
            
            # Get coordinates left
            shoulder_left.append([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
            hip_left.append([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y])
            knee_left.append([landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y])
            ankle_left.append([landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y])
            heel_left.append([landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y])
            foot_left.append([landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y])
            ear_left.append([landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y])
            eye_left.append([landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].y])
            
            # Get coordinates right
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

    eye_init = [np.mean(eye_right, axis = 0).tolist(), np.mean(eye_left, axis = 0).tolist()]
    ear_init = [np.mean(ear_right, axis = 0).tolist(), np.mean(ear_left, axis = 0).tolist()]
    nose_init = np.mean(nose_init, axis = 0).tolist()
    shoulder_init = [np.mean(shoulder_right, axis = 0).tolist(), np.mean(shoulder_left, axis = 0).tolist()]
    hip_init = [np.mean(hip_right, axis = 0).tolist(), np.mean(hip_left, axis = 0).tolist()]
    knee_init = [np.mean(knee_right, axis = 0).tolist(), np.mean(knee_left, axis = 0).tolist()]
    ankle_init = [np.mean(ankle_right, axis = 0).tolist(), np.mean(ankle_left, axis = 0).tolist()]
    heel_init = [np.mean(heel_right, axis = 0).tolist(), np.mean(heel_left, axis = 0).tolist()]
    foot_init = [np.mean(foot_right, axis = 0).tolist(), np.mean(foot_left, axis = 0).tolist()]
    
    mideyenose_init= ([[(eye_init[0][0]+nose_init[0])/2, (eye_init[0][1]+nose_init[1])/2], [(eye_init[1][0]+nose_init[0])/2, (eye_init[1][1]+nose_init[1])/2]])
    normal_dist = math.sqrt((shoulder_init[ind_cote][0] - ear_init[ind_cote][0]) ** 2 + (shoulder_init[ind_cote][1] - ear_init[ind_cote][1]) ** 2)

    #Lignes du regard, épaules, hanches et genoux : doivent être à 0°
    ligne_feet_init = angle_of_singleline(foot_init[0], foot_init[1])
    ligne_gaze_init=[angle_from_footline(mideyenose_init[0],ear_init[0]), angle_from_footline(mideyenose_init[1],ear_init[1])]
    ligne_shoulders_init = angle_from_footline(shoulder_init[0],shoulder_init[1])
    ligne_hips_init= angle_from_footline(hip_init[0],hip_init[1])
    ligne_knees_init = angle_from_footline(knee_init[0], knee_init[1])

    #Angles des segments
    angle_knee_init = [calculate_angle(hip_init[0],knee_init[0], ankle_init[0]), calculate_angle(hip_init[1],knee_init[1], ankle_init[1])]
    angle_hip_init = [calculate_angle(shoulder_init[0],hip_init[0],knee_init[0]), calculate_angle(shoulder_init[1],hip_init[1],knee_init[1])]
    angle_head_init = [calculate_angle(ear_init[0],shoulder_init[0], hip_init[0]), calculate_angle(ear_init[1], shoulder_init[1], hip_init[1])]
    angle_feet_init = [calculate_angle(hip_init[0],heel_init[0], foot_init[0]), calculate_angle(hip_init[1], heel_init[1], foot_init[1])]
    
    #distances 
    dist_nose_should_init = [distance(nose_init, shoulder_init[0]), distance(nose_init, shoulder_init[1])]
    dist_shoulder_init = distance(shoulder_init[0], shoulder_init[1])
    dist_hip_init = distance(hip_init[0], hip_init[1])
    dist_knee_init = distance(knee_init[0], knee_init[1])
    dist_feet_init=distance(foot_init[0], foot_init[1])
    long_foot_init= [distance(heel_init[0], foot_init[0]), distance(heel_init[1],foot_init[1])]


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
        
        # Extract landmarks [droite, gauche]
        try:
            landmarks = results.pose_landmarks.landmark

            #visage 
            eye = [[landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EYE_INNER.value].y],[landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EYE_INNER.value].y]]
            ear = [[landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y],[landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]]
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            mideyenose = [[(eye[0][0]+nose[0])/2, (eye[0][1]+nose[1])/2], [(eye[1][0]+nose[0])/2, (eye[1][1]+nose[1])/2]]

            #membre sup
            shoulder = [[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]]
        
            # membre inf
            hip = [[landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]]
            knee = [[landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]]
            
            #pieds
            ankle = [[landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]]
            heel = [[landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]]
            foot = [[landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]]
           

            ## Calculate angle

            #Lignes du regard, épaules, hanches et genoux : doivent être à 0°
            ligne_gaze=[angle_from_footline(mideyenose[0],ear[0]), angle_from_footline(mideyenose[1],ear[1])]
            #ligne_gaze = angle_from_footline(righteye, eye[1]) plutôt pour cam de face
            ligne_shoulders = angle_from_footline(shoulder[0],shoulder[1])
            ligne_hips= angle_from_footline(hip[0],hip[1])
            ligne_knees = angle_from_footline(knee[0], knee[1])
            ligne_feet = angle_from_footline(foot[0], foot[1])

            #Angles des segments
            angle_knee = [calculate_angle(hip[0],knee[0], ankle[0]), calculate_angle(hip[1],knee[1], ankle[1])]
            angle_hip = [calculate_angle(shoulder[0],hip[0],knee[0]), calculate_angle(shoulder[1],hip[1],knee[1])]
            angle_head = [calculate_angle(ear[0],shoulder[0], hip[0]), calculate_angle(ear[1], shoulder[1], hip[1])]
            angle_feet = [calculate_angle(hip[0],heel[0], foot[0]), calculate_angle(hip[1], heel[1], foot[1])]
            
            #distances 
            dist_nose_should = [distance(nose, shoulder[0]), distance(nose, shoulder[1])]
            dist_shoulder = distance(shoulder[0], shoulder[1])
            dist_hip = distance(hip[0], hip[1])
            dist_knee = distance(knee[0], knee[1])
            dist_feet=distance(foot[0], foot[1])
            dist_knee_heel= distance(knee[ind_cote], heel[ind_autre_cote])
            long_foot= [distance(heel[0], foot[0]), distance(heel[1],foot[1])]


            # Visualize angle 
            #angle du regard 
            cv2.putText(image, str(ligne_feet), 
                           tuple(np.multiply(ear[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 0, 66), 2, cv2.LINE_AA
                                )
            
            #angle de hanche 
            cv2.putText(image, str(dist_knee_heel), 
                           tuple(np.multiply(foot[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
                        #angle du regard 
            cv2.putText(image, str(angle_hip[1]), 
                           tuple(np.multiply(hip[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 121, 66), 2, cv2.LINE_AA
                                )
            
            #angle de hanche 
            cv2.putText(image, str(ligne_knees), 
                           tuple(np.multiply(knee[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 2, cv2.LINE_AA
                                )
            

            ### Les différents problèmes

            text_pb = f"good {ligne_feet_init}"
            thresh_head = 145
            
            ##tête 

            # if angle_head[ind_cote] < thresh_head and dist_nose_should[ind_autre_cote] > 0.7 : 
            #     text_pb = f"NOT GOOD, tête trop avancée : {angle_head[ind_cote]}"
            #     #ajouter voix "rentre le menton"

            # # la ligne est entre l'oreille et le centre du segment nez-intérieur de l'oeil
            # elif abs(ligne_gaze[ind_cote]) > 10 : 
            #     if dist_nose_should[ind_autre_cote] < 0.7 : 
            #         text_pb = f"NOT GOOD, tête vers le bas : {dist_nose_should[ind_autre_cote]}"
            #     elif dist_nose_should[ind_autre_cote] > 0.95 : 
            #         text_pb = f"NOT GOOD, tête  vers le haut : {dist_nose_should[ind_autre_cote]}"
            #     elif ligne_gaze[ind_cote] > 0 : 
            #         text_pb = f"NOT GOOD, tête inclinée vers le {cote} : {ligne_gaze}"
            #     elif ligne_gaze[ind_cote] < 0 : text_pb = f"NOT GOOD, tête inclinée vers le {autre_cote} : {ligne_gaze}"
            #     #ajouter voix "ta tête est inclinée"
            
            
            # ##épaules
            # if abs(ligne_shoulders) > 10 : 
            #     text_pb = f"NOT GOOD épaules, {ligne_shoulders}"
            #     # ajouter voix "épaules droites" + vibration haut du dos
            
            # if dist_shoulder > threshold : 
            #     text_pb = f"NOT GOOD épaules, {dist_shoulder}"
            #     # ajouter voix "tiens toi droit" + vibration haut du dos

            # ## hanches
            # if abs(ligne_hips) > 10 : 
            #     text_pb = f"NOT GOOD hanches, {ligne_hips}"
            #     # ajouter voix "hanches parallèles au sol " + vibration bas du dos
            
            # if dist_hip > threshold : 
            #     text_pb = f"NOT GOOD hanches, {dist_hip}"
            #     # ajouter voix "hanche face aux épaules" + vibration bas du dos

             ##tronc
            if abs(angle_knee[ind_cote])<165 and abs(abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote])) > 0.9*ligne_feet_init: 
                if abs(angle_knee[ind_autre_cote]) > abs(angle_hip[ind_autre_cote]) : 
                    text_pb=f"NOT GOOD, trop penche"
                else:               
                    text_pb=f"NOT GOOD, buste trop droit"
        
            ## genoux
            #si le genou est en flexion et que l'écart des genoux est supérieur à la moyenne de l'écart des hanches et des pieds
            elif (abs(angle_knee[ind_cote])<160 or abs(angle_knee[ind_autre_cote])<160) and (dist_knee < 1.1 * dist_knee_init or knee[ind_autre_cote][1]>knee[ind_cote][1]):
             #elif (abs(angle_knee[ind_cote])<160 or abs(angle_knee[ind_autre_cote])<160) and dist_knee < 1.1*dist_knee_init : #dist_knee <= (dist_hip+dist_feet)/2 :
                #en fonction de l'angle de la ligne des genoux : 
                if ligne_knees < -(ligne_feet_init)/1.75 : 
                    text_pb=f"NOT GOOD, genou {autre_cote} vers l'interieur"
                elif ligne_knees > -(ligne_feet_init)/3: 
                    text_pb=f"NOT GOOD, genou {cote} vers l'interieur"
                # #si le genou gauche est plus bas que l'autre 
                # if knee[ind_cote][1] > knee[ind_autre_cote][1] : 
                #     text_pb=f"NOT GOOD, genou {cote} vers l'interieur"
                # else : text_pb=f"NOT GOOD, genou {autre_cote} vers l'interieur"
            
            #si l'écart des genoux est trop grand 
            elif (abs(angle_knee[ind_cote])<160 or abs(angle_knee[ind_autre_cote])<160) and dist_knee > 1.5*dist_knee_init :
                if ligne_knees < -(ligne_feet_init)/2 : 
                    text_pb=f"NOT GOOD, genou {cote} vers l'exterieur"
                elif ligne_knees > -(ligne_feet_init)/3:
                    text_pb=f"NOT GOOD, genou {autre_cote} vers l'exterieur"
                #si le genou est externe au 1/3 distal du pied
                # if knee[ind_cote][0] > (2*foot_init[ind_cote][0] + heel_init[ind_cote][0])/3 : 
                #     text_pb=f"NOT GOOD, genou {cote} vers l'exterieur"
                # else : text_pb=f"NOT GOOD, genou {autre_cote} vers l'exterieur"


            # if abs(ligne_knees) > 10 : 
            #     text_pb = f"NOT GOOD genoux, {ligne_knees}"
            #     # ajouter voix "genoux parallèles au sol " + vibration genoux 
            
            # if dist_knee > 13 : 
            #     text_pb = f"NOT GOOD genoux, {dist_knee}"
            #     # ajouter voix "genou face aux hanches" + vibration genoux
            
            # ## pieds
            # if angle_feet[1]> threshold : 
            #     text_pb = f"NOT GOOD talons, {angle_feet[1]}"
            #     # ajouter voix "gardez les talons au sol"
            
            # if abs(long_foot[0] - long_foot[1]) >threshold : 
            #     text_pb = f"NOT GOOD pieds non alignés"
            #     # ajouter voix "gardez les pieds droits"

            
            # # #genoux à l'extérieur des chevilles (plutôt pour une cam)
            # # if abs(angle_knee[0]- angle_knee[1]) > 10 : 
            # #     diffknee = angle_knee[0] - angle_knee[1]
            # #     if diffknee > 0 : 
            # #         text_pb = "genou droit à l'intérieur"
            # #         #ajouter vibration au genou droit selon la valeur de diffknee
            # #     else : 
            # #         text_pb = "genou gauche à l'intérieur"
            # #         #ajouter vibration au genou gauche selon la valeur de diffknee
            



            # # else : text_pb = f"GOOD, {anglesol}"


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
