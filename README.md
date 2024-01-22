# SQUAT Detection Project

This code allows to get an auditory and haptic feedback on a squat workout. It has been specifically thought to be used by visually impaired people, but it could be used by anyone. 

## Material

### Physical Material 

- 1 or 2 Camera RGB
- 3 wireless vibrators 
- Computer with operational speakers and microphone


### Softwares

- Code Editor (Visual Studio Code or else)
- Arduino IDE 

### Coding Material

If you don't already have them, some importations are needed.

On a terminal : 

```
pip install mediapipe
pip install cv2
pip install playsound==1.2.2
pip install pyaudio
pip install SpeechRecognition
```

## Set-up
The carpet is placed on the floor. The 3 legs of the camera tripod are deployed to the maximum. The camera is placed at the end of the rope straps and is linked to the computer.

One vibrator is put in the back, the other two are put above the knees. 

## How it is working
### Algorithm part

The algorithm is built as follow :

1. Speech Recognition : the program awaits for the user to say "oui" to the question "es-tu prêt ?"

2. Image processing with CV2 and Mediapipe  : 

     2.1. Calibration for 5 seconds : recording of all the coordinates, distances, angles of the initial body landmarks

     2.2. Detection of errors on squat workout : calculation of parameters related to the posture of the head, torso, shoulders, hips, knees and feet for each squat.
         If an error is detected in > 7 frames on a single squat, there is an auditory feedback on how to improve the movement.
         If that error is linked to the shoulders, hips, or torso, there is also a vibratory feedback on the back. If that error is linked to one of the knees, there is a vibratory feedback on the knee involved.

4. Stop when the user leaves the scene


- Image processing : CV2 


#### On each squat 

Landmarks are updated with each frame (approximately every 60ms). The tab "tab_pb_int" is filled with the integers corresponding to the errors spotted.
Then, the most common error triggers an auditory feedback and sets the vibration boolean to True. 
As Mediapipe can have punctual errors on the landmarks, we set a minimal threshold before taking into account the most common error. 

When the vibration boolean is on, if the problem is on the shoulders, or the torso, or the hips, or the knees,
we determine the error from the normal value and we set the ID of the vibrator that needs to be on. Then the message is sent each frame the error is still on. 


#### At the end of a squat 
Each time the person has straight legs, the tab is emptied. 
If the squat presents no errors, there is only one audio feedback until one later squat presents errors (that's the role of the squat_ok boolean). 

## Arduino part 
The vibrators are receiving data in Wi-Fi connexion : the computer need to be connected to the same Wi-Fi as the vibrators. This connexion between the laptop code and the Arduino code on the vibrators is done by the socket package. 

Parameters : 

- UDP_IP : to be set according to the IP of each of the 3 vibrators (in the following order : [back, right knee, left knee])

- message : string data converted in bytes, from 0 to 255. 

- the type of problem switches on the matching vibrator and sends the data as long as the problem is on.
