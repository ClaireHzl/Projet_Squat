import cv2
from cv2 import destroyAllWindows
from functions import calculate_angle, distance, angle_from_footline, angle_of_singleline
import mediapipe as mp
import math
import numpy as np
import time
from collections import Counter
from playsound import playsound
import pyaudio
import os, sys


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


## Partie audio 
path = "./Audios"
audio_files = os.listdir(path) # 27 audios
audio_files.sort()
tab_pb_int=[]


# on utilise une capture d'image par webcam 
#on utilise le nombre qui correspond à l'ordre où on a branché les cams
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)

# Curl counter variables
text_pb= None
squat = False
squat_ok = None

#on inverse la largeur et la hauteur car on va faire une rotation de l'image
height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)

size = (width, height)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('your_video.mp4', fourcc, 10.0, size, True)
playsound(f"{path}/calibration.mp3")

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    eye_right, eye_left, ear_right, ear_left, nose_init, shoulder_right, shoulder_left, hip_left, hip_right, knee_right, knee_left, ankle_right, ankle_left, heel_right, heel_left, foot_right, foot_left  = ([] for i in range(17))

    start = time.time()

    #initialisation avec calibration
    while (time.time()-start)< 5  : 
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
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

    eye_init = [np.median(eye_right, axis = 0).tolist(), np.median(eye_left, axis = 0).tolist()]
    ear_init = [np.median(ear_right, axis = 0).tolist(), np.median(ear_left, axis = 0).tolist()]
    nose_init = np.median(nose_init, axis = 0).tolist()
    shoulder_init = [np.median(shoulder_right, axis = 0).tolist(), np.median(shoulder_left, axis = 0).tolist()]
    hip_init = [np.median(hip_right, axis = 0).tolist(), np.median(hip_left, axis = 0).tolist()]
    knee_init = [np.median(knee_right, axis = 0).tolist(), np.median(knee_left, axis = 0).tolist()]
    ankle_init = [np.median(ankle_right, axis = 0).tolist(), np.median(ankle_left, axis = 0).tolist()]
    heel_init = [np.median(heel_right, axis = 0).tolist(), np.median(heel_left, axis = 0).tolist()]
    foot_init = [np.median(foot_right, axis = 0).tolist(), np.median(foot_left, axis = 0).tolist()]
    
    normal_dist = math.sqrt((shoulder_init[ind_cote][0] - heel_init[ind_cote][0]) ** 2 + (shoulder_init[ind_cote][1] - heel_init[ind_cote][1]) ** 2)

    #Lignes 
    ligne_feet_init = angle_of_singleline(foot_init[0], foot_init[1])
    ligne_gaze_init = [angle_from_footline(nose_init, ear_init[0], ligne_feet_init), angle_from_footline(nose_init, ear_init[1], ligne_feet_init)]
    ligne_ear_init = angle_from_footline(ear_init[0],ear_init[1], ligne_feet_init)
    ligne_shoulders_init = angle_from_footline(shoulder_init[0],shoulder_init[1], ligne_feet_init)
    ligne_hips_init= angle_from_footline(hip_init[0],hip_init[1], ligne_feet_init)
    ligne_knees_init = angle_from_footline(knee_init[0], knee_init[1], ligne_feet_init)

    angle_head_init = [calculate_angle(nose_init, ear_init[0],shoulder_init[0]), calculate_angle(nose_init,ear_init[1], shoulder_init[1])]

    #distances 
    dist_ear_should_x_init = [abs(ear_init[0][0] - shoulder_init[0][0])/normal_dist, abs(ear_init[1][0]- shoulder_init[1][0])/normal_dist]
    dist_shoulder_init = distance(shoulder_init[0], shoulder_init[1], normal_dist)
    dist_hip_init = distance(hip_init[0], hip_init[1], normal_dist)
    dist_knee_init = distance(knee_init[0], knee_init[1], normal_dist)
    dist_feet_init=distance(foot_init[0], foot_init[1], normal_dist)

    playsound(f"{path}/start.mp3")

    
    while cap.isOpened():
        ret, frame = cap.read()        
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
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

            #membre sup
            shoulder = [[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]]
        
            # membre inf
            hip = [[landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]]
            knee = [[landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]]
            
            #pieds
            ankle = [[landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]]
            heel = [[landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]]
            foot = [[landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y], [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]]

            #Lignes du regard, épaules, hanches et genoux : doivent être à 0°
            ligne_gaze = [angle_from_footline(nose, ear[0], ligne_feet_init), angle_from_footline(nose, ear[1], ligne_feet_init)]
            ligne_shoulders = angle_from_footline(shoulder[0],shoulder[1], ligne_feet_init)
            ligne_hips= angle_from_footline(hip[0],hip[1], ligne_feet_init)
            ligne_knees = angle_from_footline(knee[0], knee[1], ligne_feet_init)
            ligne_feet = angle_from_footline(foot[0], foot[1], ligne_feet_init)
            ligne_ear = angle_from_footline(ear[0],ear[1], ligne_feet_init)

            #Angles des segments
            angle_knee = [calculate_angle(hip[0],knee[0], ankle[0]), calculate_angle(hip[1],knee[1], ankle[1])]
            angle_hip = [calculate_angle(shoulder[0],hip[0],knee[0]), calculate_angle(shoulder[1],hip[1],knee[1])]
            angle_head = [calculate_angle(nose,ear[0],shoulder[0]), calculate_angle(nose, ear[1], shoulder[1])]
            
            #distances 
            dist_ear_should_x = [abs(ear[0][0] - shoulder[0][0])/normal_dist, abs(ear[1][0]- shoulder[1][0])/normal_dist]
            dist_shoulder = distance(shoulder[0], shoulder[1], normal_dist)
            dist_hip = distance(hip[0], hip[1], normal_dist)
            dist_knee = distance(knee[0], knee[1], normal_dist)
            dist_heel = distance(heel[0], heel[1], normal_dist)
            dist_feet=distance(foot[0], foot[1], normal_dist)


            # Visualize angle 
            #angle du regard 
            cv2.putText(image, str(round(dist_knee/dist_knee_init,4)), 
                           tuple(np.multiply(ear[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 0, 66), 2, cv2.LINE_AA
                                )
            
            #angle de hanche 
            cv2.putText(image, str(dist_hip / dist_hip_init), 
                           tuple(np.multiply(shoulder[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
            #angle du regard 
            cv2.putText(image, str(round(abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]),4) ), 
                           tuple(np.multiply(hip[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 121, 66), 2, cv2.LINE_AA
                                )
            
            #angle de hanche 
            cv2.putText(image, str(dist_knee/dist_knee_init), 
                           tuple(np.multiply(knee[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 2, cv2.LINE_AA
                                )
            

            ### Les différents problèmes

            text_pb = f"good {foot[0]}"
            print(foot)

            if any(abs(i)<160 for i in angle_knee) : 
                squat = True

                ## pieds
                if dist_feet < dist_heel :
                    text_pb = f"NOT GOOD, pied rentres {dist_feet - dist_heel}"
                    tab_pb_int.append(1)

                elif any(heel_init[i][1] - heel[i][1] > 0.01 for i in range(2)):
                        text_pb = f"NOT GOOD talons, {heel_init[ind_cote][1] - heel[ind_cote][1]}"
                        tab_pb_int.append(2)

                # tête 
                elif abs(ligne_ear - ligne_ear_init) > 7 and any(dist_ear_should_x_init[i]- dist_ear_should_x[i] > 0.04 for i in range (2)): 
                    if dist_ear_should_x_init[ind_cote]- dist_ear_should_x[ind_cote] > 0.04 : 
                        text_pb = f"NOT GOOD, tete inclinee {cote} : {round(ligne_ear - ligne_ear_init,3),round(dist_ear_should_x_init[ind_cote]- dist_ear_should_x[ind_cote],4)}"
                        tab_pb_int.append(4)
                    elif dist_ear_should_x_init[ind_autre_cote]- dist_ear_should_x[ind_autre_cote] > 0.04 : 
                        text_pb = f"NOT GOOD, tete inclinee {autre_cote}: {round(ligne_ear - ligne_ear_init,3),round(dist_ear_should_x_init[ind_autre_cote]- dist_ear_should_x[ind_autre_cote],3)}"
                        tab_pb_int.append(5)
                    else : text_pb = "NOT GOOD, tete inclinee"
                    #vibration haut du dos / intensité légère

                #elif abs(ligne_ear - ligne_ear_init) <= 7 or any(dist_ear_should_x_init[i]- dist_ear_should_x[i] < 0.04 for i in range (2)) :
                elif (angle_head_init[ind_cote]-angle_head[ind_cote] < -6 )  and (nose_init[0]  - shoulder_init[ind_autre_cote][0]- (nose[0] - shoulder[ind_autre_cote][0] )>0.03) : #or angle_head_init[ind_cote]-angle_head[ind_cote]> 250 # < -4,5
                        text_pb = f"NOT GOOD, tete trop avancée : {round(angle_head_init[ind_cote]-angle_head[ind_cote], 4), round(nose_init[0]  - shoulder_init[ind_autre_cote][0]- (nose[0] - shoulder[ind_autre_cote][0] ),4)}"
                        #vibration haut du dos / intensité légère
                        tab_pb_int.append(6)
                
                elif abs(ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]) > 7 : #8
                        if ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote] < 0 : 
                            text_pb = f"NOT GOOD, tete  vers le haut : {ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]}"
                            tab_pb_int.append(7)
                        else : 
                            text_pb = f"NOT GOOD, tete  vers le bas : {ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]}"
                            tab_pb_int.append(8)
                        #vibration haut du dos / intensité légère
                                           
                ##épaules      
                elif abs(abs(ligne_shoulders) - abs(ligne_shoulders_init)) > 6.5 and  0.9 < dist_shoulder / dist_shoulder_init < 1.05 : #-0.005 < dist_shoulder_init - dist_shoulder < 0.05 : 
                #elif ligne_shoulders > -12 or ligne_shoulders < -27 : #(ligne_shoulders+ligne_feet_init > 3 or  ligne_shoulders+ligne_feet_init < -15) :
                    if ligne_shoulders - ligne_shoulders_init > 0 : 
                        text_pb = f"NOT GOOD epaule {autre_cote} trop haute, {ligne_shoulders}"
                        #vibration haut du dos / intensité moyenne
                        tab_pb_int.append(9)
                    else : 
                        text_pb = f"NOT GOOD epaule {cote} trop haute, {ligne_shoulders}"
                        #vibration haut du dos / intensité moyenne
                        tab_pb_int.append(10)
                        
                elif dist_shoulder / dist_shoulder_init > 1.05 : #dist_shoulder_init - dist_shoulder < -0.005 #dist_shoulder/dist_shoulder_init > 1.08 :  #(0.92+0.012*ligne_feet_init)*dist_shoulder_init : #1.09*dist_shoulder_init (pour 14): 
                    text_pb = f"NOT GOOD epaule {autre_cote} en avant, {dist_shoulder / dist_shoulder_init}"
                    #vibration haut du dos / intensité moyenne
                    tab_pb_int.append(11)
                elif dist_shoulder / dist_shoulder_init  < 0.9 : #dist_shoulder_init - dist_shoulder > 0.07 : #dist_shoulder/dist_shoulder_init <0.7 : #(0.94-0.003*ligne_feet_init) * dist_shoulder_init : #< 0.89 avec 18 #0.99 avec 14 d'angle 0.87 avec 25
                    text_pb = f"NOT GOOD epaule {cote} en avant, {dist_shoulder / dist_shoulder_init}"
                    #vibration haut du dos / intensité moyenne
                    tab_pb_int.append(12)

                                ## hanches
                elif dist_hip/dist_hip_init > 1.02 : #dist_hip_init- dist_hip < - 0.002 : #and dist_hip/dist_hip_init >  1.15 : #(1.01+ligne_feet_init*0.005)*dist_hip_init : #1.08 pour 14 et 1.13 pour 25
                    text_pb = f"NOT GOOD hanche {autre_cote} en avant, {dist_hip_init- dist_hip}"
                    #vibration bas du dos / intensité moyenne   
                    tab_pb_int.append(13)     
                elif dist_hip/dist_hip_init < 0.9 : #dist_hip_init- dist_hip > 0.02 : #dist_hip/dist_hip_init < 0.88 : #(1.06 - ligne_feet_init*0.01)*dist_hip_init : #0.88 à 16 et 0.92 avec 14 d'angle
                    text_pb = f"NOT GOOD hanche {cote} en avant, {dist_hip_init- dist_hip}"
                    #vibration bas du dos / intensité moyenne
                    tab_pb_int.append(14)
                
                elif ligne_hips_init - ligne_hips < -2.5 :#abs(abs(ligne_hips) - abs(ligne_hips_init)) > 8.5:
                    text_pb = f"NOT GOOD hanche {cote} trop basse, {round(ligne_hips_init - ligne_hips, 4)}"
                    #vibration bas du dos / intensité moyenne
                    tab_pb_int.append(15)

                elif ligne_hips_init - ligne_hips > 3  : 
                    text_pb = f"NOT GOOD hanche {autre_cote} trop basse, {round(ligne_hips_init - ligne_hips, 4)}"
                    #vibration bas du dos / intensité moyenne
                    tab_pb_int.append(16)

                

                 ##tronc
                elif abs(angle_knee[ind_autre_cote])<160 and (abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) < 5 or  abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) > 30): 
                    if abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) > 30: 
                        text_pb=f"NOT GOOD, trop penche {angle_knee[ind_autre_cote] - angle_hip[ind_autre_cote]}"
                        tab_pb_int.append(17)
                    else:               
                        text_pb=f"NOT GOOD, buste trop droit {angle_knee[ind_autre_cote] - angle_hip[ind_autre_cote]}"
                        tab_pb_int.append(18)
                    #vibration bas du dos / intensité moyenne
                        
                else : 
                    tab_pb_int.append(0)
                
                ## genoux
                    

                 #si l'écart des genoux est trop grand 
                if dist_knee/dist_knee_init >= 1.6 : 
                    if knee[ind_cote][0] > ankle[ind_cote][0] :
                        text_pb=f"NOT GOOD, genou {cote} vers l'exterieur {round(ligne_knees,2)}"
                        tab_pb_int.append(22)
                        #vibration genou {cote} 

                    else : 
                        text_pb=f"NOT GOOD, genou {autre_cote} vers l'exterieur {round(ligne_knees,2)}"
                        #vibration genou {autre_cote} 
                        tab_pb_int.append(23)

                #si le genou controlatéral dépasse la pointe de pied  
                elif knee[ind_autre_cote][0] < foot[ind_autre_cote][0] :
                    text_pb=f"NOT GOOD, genou en avant {round(knee[ind_autre_cote][0] - foot[ind_autre_cote][0],2)}"
                    #vibration bas du dos / intensité moyenne
                    tab_pb_int.append(19)

                #si le genou est en flexion et que l'écart des genoux diminue ou que le genou controlatéral est plus bas 
                elif dist_knee/dist_knee_init < 1.1 or (any(abs(i)<150 for i in angle_knee) and (dist_knee/dist_knee_init < 1.3  or  knee[ind_autre_cote][1]>knee[ind_cote][1])):
                    #en fonction de l'angle de la ligne des genoux : 
                    if ligne_knees < - 5 or knee[ind_autre_cote][1]>knee[ind_cote][1] : #-12
                        text_pb=f"NOT GOOD, genou {autre_cote} vers l'interieur {round(ligne_knees_init - ligne_knees,2)}"
                        #vibration genou {autre_cote} 
                        tab_pb_int.append(20)
                    elif ligne_knees > -3 : 
                        text_pb=f"NOT GOOD, genou {cote} vers l'interieur {round(ligne_knees,2)}"
                        #vibration genou {cote} 
                        tab_pb_int.append(21)
                    else : text_pb=f"NOT GOOD, genou vers l'intérieur {round(ligne_knees,2)}"
                


            else : 
                if squat == True : 
                    print('tab', tab_pb_int)
                    counter_pb = Counter(tab_pb_int)
                    tab_pb_int=[]
                    if counter_pb.most_common(1)[0][1] > 5 :
                        most_pb = counter_pb.most_common(1)[0][0]
                        squat_ok = False
                    else : most_pb = 0
                    print('major pb : ', most_pb)
                    
                    # Audio du problème prioritaire
                    if squat_ok == False or squat_ok == None: 
                        playsound(f"{path}/{audio_files[most_pb]}")
                    
                    if most_pb == 0 : squat_ok = True

                squat = False     
                text_pb=f"{most_pb}"   


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
        #image = cv2.resize(image, (width//3, height//3)) 

        cv2.imshow('Squat Correction',image)

        

        if cv2.waitKey(10) & 0xFF == ord('q') or foot[0][1] > 1 or foot[1][1] > 1:
            break

    cap.release()
    #out.release()
    cv2.destroyAllWindows()
    
#destroyAllWindows()
