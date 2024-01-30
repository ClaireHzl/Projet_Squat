'''
Squat correction with two cameras
---------------------------------

Parallel program for comparison with the one with one camera.
Using the library vidgear to use two cameras at the same time (predifined threads)

Same structure than the 1 cam program but combining the errors of the two cameras. 
With prioritization of the problems, count of the problem that occures the most for a chosen time.
Only audio feedback, no vibration on this code

'''

# Basic import
import math
import numpy as np
import sys
import time
import os, sys

# Video import 
from vidgear.gears import VideoGear
import cv2
#from cv2 import destroyAllWindows
import mediapipe as mp
from collections import Counter

# Definitions from other files to clear the main script
from getmarkers import getmarkers
from camface import camface
from camside import camside
from functions import * 

# Audio imports
from playsound import playsound
import pyaudio
#from speech_recognition import Recognizer, Microphone, AudioFile

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


# Audio files
path = "Audios"
audio_files = os.listdir(path) # 27 audios
audio_files.sort() # Mettre dans l'ordre alphabetique

# Mediapipe markers 
mp_drawing1 = mp.solutions.drawing_utils
mp_pose1 = mp.solutions.pose

mp_drawing2 = mp.solutions.drawing_utils
mp_pose2 = mp.solutions.pose



# Define and start the stream 
# First source 
stream1 = VideoGear(source=0, logging=True).start() # Number source can be 1 
# Second source
stream2 = VideoGear(source=2, logging=True).start() # and here 2

# Initilization mediapipe one both cameras
with mp_pose1.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose1:
    with mp_pose2.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose2:
        # Infinite loop
        while True:
            # Read frames
            frame1 = stream1.read()
            #frame1 = cv2.rotate(frame1, cv2.ROTATE_90_COUNTERCLOCKWISE) # Rotation for portrait format
            frame2 = stream2.read()
            frame2 = cv2.rotate(frame2, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Recolor image to RGB
            image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            image1.flags.writeable = False
            image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            image2.flags.writeable = False

            # Make detection
            results1 = pose1.process(image1)
            # Recolor back to BGR
            image1.flags.writeable = True
            image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
            
            results2 = pose2.process(image2)
            image2.flags.writeable = True
            image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)

            try :

                ## if a first problem has been detected on one squat, the second problem will have a higher delay
                if squat_pb1 == False : lim_count = 10
                else : lim_count = 50

                # if a problem is detected a sufficient number of times, we play the audio and launch the vibrator boolean
                if tab_pb_int != [] and count > lim_count : 
                    counter_pb = Counter(tab_pb_int)
                    #if the most common is an error and is more frequent than the arbitrary threshold
                    if counter_pb.most_common(1)[0][0] != 0 and counter_pb.most_common(1)[0][1] > 4 :
                        most_pb = counter_pb.most_common(1)[0][0]
                        playsound(f"{path}/{audio_files[most_pb]}", block=False)        # we play the audio feedback
                        list_pb.append(most_pb)         #we append the problem to the list of problems of this specific squat
                        vib_bool = True                 #we unlock the vibration boolean
                        squat_pb1 = True                #boolean to say a first problem has been detected
                        squat_ok = False                #boolean to say that the squat has error
                        
                        #we reset the tab and the counter
                        tab_pb_int = []
                        count = 0 


                # Using def getmarkers to extract the useful markers to identify the posture of the user
                markers1 = getmarkers(results1, mp_pose1)
                markers2 = getmarkers(results2, mp_pose2)


                # Calculation of the angle of the knee to take into account error during squat (<60°)
                angle_back_knee_left = calculate_angle(markers2[2], markers2[3],markers2[4])
                if abs(angle_back_knee_left) < 160 : 
                    # Track squat
                    count += 1
                    squat = True 
                    
                    # Using def camface and camside to extract each of their top priority problem 
                    # 1 : Face camera
                    pb_int1 = camface(markers1)
                    # 2 : Side camera
                    pb_int2 = camside(markers2)

                    # Identify which is the most important problem knoiwing that pb_int = 0 -> no problem
                    if pb_int1 !=0 or pb_int1 !=0 :
                        # If one of them equal to zero has the lowest priority
                        if pb_int1 == 0 : pb_int1 = 100 
                        if pb_int2 == 0 : pb_int2 = 100 
                        # Smallest number = higher priority
                        if pb_int1 <= pb_int2 :
                            pb_int = pb_int1
                        else : 
                            pb_int = pb_int2
                    else :
                        pb_int =0
                    
                    tab_pb_int.append(pb_int)
                    
                # Rest position knee angle > 160°
                else :
                    if squat==True and not list_pb : 
                        if squat_ok == False : playsound(f"{path}/{audio_files[0]}", block = False)
                        squat_ok = True 
                    vib_bool, squat, squat_pb1 = False, False, False
                    tab_pb_int, list_pb = [], []
                    count, vib = 0, 0

         
            
                # Mediapipe markers on the first video visible on the screen 
                mp_drawing1.draw_landmarks(image1, results1.pose_landmarks, mp_pose1.POSE_CONNECTIONS,
                                        mp_drawing1.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                        mp_drawing1.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

                # Mediapipe markers on the second video visible on the screen 
                mp_drawing2.draw_landmarks(image2, results2.pose_landmarks, mp_pose2.POSE_CONNECTIONS,
                                        mp_drawing2.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                        mp_drawing2.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            except: pass
            
            # Display frames
            cv2.imshow("Stream 1", image1)
            cv2.imshow("Stream 2", image2)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Release video streams and close all windows
stream1.stop()
stream2.stop()
cv2.destroyAllWindows()





