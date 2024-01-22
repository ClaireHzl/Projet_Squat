#basic packages
import os, sys
import math
import numpy as np
import time
from collections import Counter
#created functions
from functions import * 
#image processing
import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
#audio and speech part
from playsound import playsound
import pyaudio
from speech_recognition import Recognizer, Microphone, AudioFile
#Arduino part
import socket


# setting our variables
tab_pb_int, list_pb=[], []
count, vib = 0, 0
audio_bool, squat, squat_ok, squat_pb1, vib_bool = False, False, False, False, False

##Electronics initialisation 
#IP adresses of the vibrators [back, right knee, left knee]
UDP_IP = ['192.168.112.7', '192.168.250.208', '192.168.250.208'] 
UDP_PORT = 8000
#setting the communication between the laptop and the vibrators
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


##Mediapipe initialisation
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

## Setting the audio part
path = "./Audios"
audio_files = os.listdir(path) 
audio_files.sort()

# ## Speech Recognition 
# # The program is waiting for the user to say "oui" after asking him "es-tu prêt ?"
# recognizer = Recognizer()
# with Microphone() as source:
#     playsound(f"{path}/ready.mp3",  block=False)

#     while not audio_bool : 
#         recorded_audio = recognizer.listen(source, phrase_time_limit = 5)

#         try:
#             print("Reconnaissance du texte...")
#             voice_command = recognizer.recognize_google(
#                         recorded_audio, 
#                         language="fr-FR"
#                     ).lower()
#             print("Vous avez dit : {}".format(voice_command))
#             if "oui" in voice_command : audio_bool = True

#         except Exception as ex:
#             print(ex)


#Recording by camera and showing on the laptop
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
out = video_init(cap)


#Using Mediapipe on the camera image
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    start = time.time()
    
    #calibration during 5 seconds
    playsound(f"{path}/calibration.mp3", block= False)
    ind_cote, ind_autre_cote, cote, autre_cote, normal_dist, nose_init, shoulder_init, heel_init, ligne_ear_init, dist_ear_should_x_init, dist_shoulder_init, dist_hip_init, dist_knee_init, ligne_gaze_init, ligne_shoulders_init, ligne_hips_init, ligne_knees_init, ligne_feet_init, angle_head_init = calibration (mp_pose, pose, cap, start)
    
    #SQUAT PROGRAM
    playsound(f"{path}/start.mp3", block=False)
    while cap.isOpened():
        image, results = landmarks_init (cap, pose)

        try:
            landmarks = results.pose_landmarks.landmark
            ear, nose, shoulder, hip, knee, ankle, heel, foot, ligne_gaze, ligne_shoulders, ligne_hips, ligne_knees, ligne_feet, ligne_ear, angle_knee, angle_hip, angle_head, dist_ear_should_x, dist_shoulder, dist_hip, dist_knee, dist_heel, dist_feet = realtime_param(landmarks, mp_pose, normal_dist, ligne_feet_init)

            #### PARTIE A ENLEVER A LA FIN
            cv2.putText(image, str(vib), 
                           tuple(np.multiply(ear[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 0, 66), 2, cv2.LINE_AA
                                )
            
            cv2.putText(image, str(dist_hip/dist_hip_init), 
                           tuple(np.multiply(shoulder[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
            cv2.putText(image, str(ligne_knees), 
                           tuple(np.multiply(hip[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (79, 121, 66), 2, cv2.LINE_AA
                                )
            
            cv2.putText(image, str(ligne_hips_init - ligne_hips), 
                           tuple(np.multiply(knee[1], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 2, cv2.LINE_AA
                                )
            

            ###  Algorithm of the Squat Sensor

            text_pb = "good"

            ## if a first problem has been detected on one squat, the second problem will have a higher delay
            if squat_pb1 == False : lim_count = 10
            else : lim_count = 50

            # if a problem is detected a sufficient number of times, we play the audio and launch the vibrator boolean
            if tab_pb_int != [] and count > lim_count : 
                counter_pb = Counter(tab_pb_int)
                if counter_pb.most_common(1)[0][0] != 0 and counter_pb.most_common(1)[0][1] > 7 :
                    most_pb = counter_pb.most_common(1)[0][0]
                    playsound(f"{path}/{audio_files[most_pb]}", block=False)
                    list_pb.append(most_pb)
                    vib_bool = True
                    squat_pb1 = True
                    squat_ok = False
                    tab_pb_int = []
                    count = 0 

            #vibrator part for errors on knees, shoulders and hips
            if vib_bool :
                vib, vibreur_id = vib_live(most_pb, ligne_shoulders, ligne_shoulders_init, dist_shoulder, dist_shoulder_init,  dist_hip, dist_hip_init, ligne_hips_init, ligne_hips, angle_knee, ind_autre_cote, angle_hip, dist_knee, dist_knee_init )
                message = bytes(vib, "utf8")
                print("vibration = ", message)
                sock.sendto(message, (UDP_IP[vibreur_id], UDP_PORT))
                print("vibration envoyée")
                    

            # when the person is doing a squat, we collect all the errors by order of priority
            if any(abs(i)<160 for i in angle_knee) : 
                count +=1
                squat = True

                ## pieds
                # if the toes are closer than the heels
                if dist_feet < dist_heel :
                    text_pb = f"NOT GOOD, pied rentres {dist_feet - dist_heel}"
                    tab_pb_int.append(1)

                #if the heel is rising up
                elif any(heel_init[i][1] - heel[i][1] > 0.015 for i in range(2)):
                        text_pb = f"NOT GOOD talons, {heel_init[ind_cote][1] - heel[ind_cote][1]}"
                        tab_pb_int.append(2)

                ## head 
                # if the orientation between both ears varies and the distance ear-shoulder decreases
                elif abs(ligne_ear - ligne_ear_init) > 7 and any(dist_ear_should_x_init[i]- dist_ear_should_x[i] > 0.04 for i in range (2)): 
                    if dist_ear_should_x_init[ind_cote]- dist_ear_should_x[ind_cote] > 0.04 : 
                        text_pb = f"NOT GOOD, tete inclinee {cote} : {round(ligne_ear - ligne_ear_init,3),round(dist_ear_should_x_init[ind_cote]- dist_ear_should_x[ind_cote],4)}"
                        tab_pb_int.append(4)
                    elif dist_ear_should_x_init[ind_autre_cote]- dist_ear_should_x[ind_autre_cote] > 0.04 : 
                        text_pb = f"NOT GOOD, tete inclinee {autre_cote}: {round(ligne_ear - ligne_ear_init,3),round(dist_ear_should_x_init[ind_autre_cote]- dist_ear_should_x[ind_autre_cote],3)}"
                        tab_pb_int.append(5)
                    else : text_pb = "NOT GOOD, tete inclinee"

                # if the angle shoulder-ear-nose is increasing and the distance nose-shoulder decreases
                elif (angle_head_init[ind_cote]-angle_head[ind_cote] < -6 )  and (nose_init[0]  - shoulder_init[ind_autre_cote][0]- (nose[0] - shoulder[ind_autre_cote][0] )>0.03) : #or angle_head_init[ind_cote]-angle_head[ind_cote]> 250 # < -4,5
                        text_pb = f"NOT GOOD, tete trop avancée : {round(angle_head_init[ind_cote]-angle_head[ind_cote], 4), round(nose_init[0]  - shoulder_init[ind_autre_cote][0]- (nose[0] - shoulder[ind_autre_cote][0] ),4)}"
                        tab_pb_int.append(6)
                
                # if the orientation between nose and left ear varies
                elif abs(ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]) > 7 : #8
                        if ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote] < 0 : 
                            text_pb = f"NOT GOOD, tete  vers le haut : {ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]}"
                            tab_pb_int.append(7)
                        else : 
                            text_pb = f"NOT GOOD, tete  vers le bas : {ligne_gaze_init[ind_cote] - ligne_gaze[ind_cote]}"
                            tab_pb_int.append(8)
                                           
                ##shoulders      
                elif abs(abs(ligne_shoulders) - abs(ligne_shoulders_init)) > 7 and  0.9 < dist_shoulder / dist_shoulder_init < 1.05 : #-0.005 < dist_shoulder_init - dist_shoulder < 0.05 : 
                    if ligne_shoulders - ligne_shoulders_init > 0 : 
                        text_pb = f"NOT GOOD epaule {autre_cote} trop haute, {ligne_shoulders}"
                        tab_pb_int.append(9)
                    else : 
                        text_pb = f"NOT GOOD epaule {cote} trop haute, {ligne_shoulders}"
                        tab_pb_int.append(10)
                        
                elif dist_shoulder / dist_shoulder_init > 1.05 : #dist_shoulder_init - dist_shoulder < -0.005 #dist_shoulder/dist_shoulder_init > 1.08 :  #(0.92+0.012*ligne_feet_init)*dist_shoulder_init : #1.09*dist_shoulder_init (pour 14): 
                    text_pb = f"NOT GOOD epaule {autre_cote} en avant, {dist_shoulder / dist_shoulder_init}"
                    tab_pb_int.append(11)
                elif dist_shoulder / dist_shoulder_init  < 0.9 : #dist_shoulder_init - dist_shoulder > 0.07 : #dist_shoulder/dist_shoulder_init <0.7 : #(0.94-0.003*ligne_feet_init) * dist_shoulder_init : #< 0.89 avec 18 #0.99 avec 14 d'angle 0.87 avec 25
                    text_pb = f"NOT GOOD epaule {cote} en avant, {dist_shoulder / dist_shoulder_init}"
                    tab_pb_int.append(12)

                ## hips
                elif dist_hip/dist_hip_init > 1.1 : #dist_hip_init- dist_hip < - 0.002 : #and dist_hip/dist_hip_init >  1.15 : #(1.01+ligne_feet_init*0.005)*dist_hip_init : #1.08 pour 14 et 1.13 pour 25
                    text_pb = f"NOT GOOD hanche {autre_cote} en avant, {dist_hip_init- dist_hip}"
                    tab_pb_int.append(13)     
                elif dist_hip/dist_hip_init < 0.85 : #dist_hip_init- dist_hip > 0.02 : #dist_hip/dist_hip_init < 0.88 : #(1.06 - ligne_feet_init*0.01)*dist_hip_init : #0.88 à 16 et 0.92 avec 14 d'angle
                    text_pb = f"NOT GOOD hanche {cote} en avant, {dist_hip_init- dist_hip}"
                    tab_pb_int.append(14)
                
                elif ligne_hips_init - ligne_hips < -2.5 :#abs(abs(ligne_hips) - abs(ligne_hips_init)) > 8.5:
                    text_pb = f"NOT GOOD hanche {cote} trop basse, {round(ligne_hips_init - ligne_hips, 4)}"
                    tab_pb_int.append(15)

                elif ligne_hips_init - ligne_hips > 6  : 
                    text_pb = f"NOT GOOD hanche {autre_cote} trop basse, {round(ligne_hips_init - ligne_hips, 4)}"
                    tab_pb_int.append(16)

                

                ##torso
                elif abs(angle_knee[ind_autre_cote])<160 and (abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) < 0 or  abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) > 30): 
                    if abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote]) > 30: 
                        text_pb=f"NOT GOOD, trop penche {abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote])}"
                        tab_pb_int.append(17)
                    else:               
                        text_pb=f"NOT GOOD, buste trop droit {abs(angle_knee[ind_autre_cote]) - abs(angle_hip[ind_autre_cote])}"
                        tab_pb_int.append(18)


                ## knees
                #if the knee gap is too wide
                elif dist_knee/dist_knee_init >= 1.6 : 
                    if knee[ind_cote][0] > ankle[ind_cote][0] :
                        text_pb=f"NOT GOOD, genou {cote} vers l'exterieur {round(ligne_knees,2)}"
                        tab_pb_int.append(22)

                    else : 
                        text_pb=f"NOT GOOD, genou {autre_cote} vers l'exterieur {round(ligne_knees,2)}"
                        tab_pb_int.append(23)

                #if the contralateral knee extends beyond toes
                elif knee[ind_autre_cote][0] < foot[ind_autre_cote][0] :
                    text_pb=f"NOT GOOD, genou en avant {round(knee[ind_autre_cote][0] - foot[ind_autre_cote][0],2)}"
                    tab_pb_int.append(19)

                #if the knee spacing is too small or the contralateral knee is lower
                elif dist_knee/dist_knee_init < 1.1 or (any(abs(i)<150 for i in angle_knee) and (dist_knee/dist_knee_init < 1.3  or  knee[ind_autre_cote][1]>knee[ind_cote][1])):
                    #depending on knee line angle: 
                    if  ligne_knees < -10 or knee[ind_autre_cote][0] > heel[ind_autre_cote][0] or knee[ind_autre_cote][1]>knee[ind_cote][1] : #ligne_knees < - 5
                        text_pb=f"NOT GOOD, genou {autre_cote} vers l'interieur {round(ligne_knees_init - ligne_knees,2)}"
                        tab_pb_int.append(20)
                    elif ligne_knees > -7 : 
                        text_pb=f"NOT GOOD, genou {cote} vers l'interieur {round(ligne_knees,2)}"
                        tab_pb_int.append(21)
                    else : text_pb=f"NOT GOOD, genou vers l'intérieur {round(ligne_knees,2)}"
                
                else : 
                    tab_pb_int.append(0)


             #at the end of each squat, the data is reset
            else : 
                if squat==True and not list_pb : 
                    if squat_ok == False : playsound(f"{path}/{audio_files[0]}", block = False)
                    squat_ok = True 
                vib_bool, squat, squat_pb1 = False, False, False
                tab_pb_int, list_pb = [], []
                count, vib = 0, 0

                    
        except:
            pass
        

        # Render squat counter
        # Setup status box and text + landmarks on the person
        cv2.rectangle(image, (0,0), (500,20), (255,255,255), -1) 
        cv2.putText(image, f'{text_pb}', (15,10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 )               
        
        #writing the video with landmarks 
        out.write(image)
        cv2.imshow('Squat Correction',image)

        #stopping the recording if CTRL+C or if the person leaves the scene
        if cv2.waitKey(10) & 0xFF == ord('q') or any(val < 0 or val > 1 for sublist in foot for val in sublist) : # or foot[0][1] > 1 or foot[1][1] > 1:
            break

    cap.release()
    cv2.destroyAllWindows()
    
