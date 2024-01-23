# SQUAT Correction Project

This code allows to get an auditory and haptic feedback on a squat workout. It has been specifically thought to be used by visually impaired people, but it could be used by anyone. 

## Material

### Physical Material 

- 1 or 2 Camera RGB
- 3 wireless vibrators 
- Computer with operational speakers and microphone


### Softwares

- Code Editor (Visual Studio Code or else)
- Arduino IDE 


### Set-up
The carpet is placed on the floor. The 3 legs of the camera tripod are deployed to the maximum. The camera is placed at the end of the rope straps and is linked to the computer. The camera must be oriented in profile format (the image is rotated by -90° during pre-processing). 

One vibrator is put in the back, the other two are put above the knees. 

## Algorithm part
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

### How it is working
The algorithm is built as follow :

1.  Speech Recognition : the program awaits for the user to say "oui" to the question "es-tu prêt ?"

2.  Image processing with CV2 and Mediapipe  : 

     2.1. Calibration for 5 seconds : recording of all the coordinates, distances, angles of the initial body landmarks via the function *calibration*

     2.2. Detection of errors on squat workout : calculation of parameters related to the posture of the head, torso, shoulders, hips, knees and feet for each squat.

    If an error is detected in > 7 frames on a single squat, there is an auditory feedback on how to improve the movement.
    
    If that error is linked to the shoulders, hips, or torso, there is also a vibratory feedback on the back. If that error is linked to one of the knees, there is a vibratory feedback on the knee involved.

3.  Stop when the user leaves the scene



### In details 

#### Calibration

The function *calibration* is used as below. 

For 5 seconds, each landmarks coordinates on every frame is captured, then the median is saved as *landmark_init*.

From that, we extract :
- the *ind_side* and *ind_other_side* : integers  corresponding to the side closer to the camera and the other side (defined by the toe y-coordinate higher than the other). Useful to generalize to the symetric position. 
    
    *The* side *and* other_side *are the strings (left/right) corresponding to the closer side and the other one, used in the written feedback for the developer.*

- the *normal_dist* : distance between the left shoulder and the left heel. Used to normalize all the other distances between 2 points (useful to generalize the algorithm for people of all sizes).

- the *ligne_feet_init* : angle between the horizontal and the ligne between toes. Used to normalize all the ligne orientation values (useful to generalize the algorithm to the initial orientation of the person).

Then, all needed distances, line orientations and angles are determined according to the overlying values. 


#### Errors ID

Each error type is characterized by an integer from 1 to 23. They are structured according to an order of priority based on the importance of the error, established by a sports professional.

Therefore, according to the coordinates, angles and distances of the landmarks, if an error is detected, the corresponding integer will be output. If not, it's a good squat, the corresponding integer is 0. 


#### On each squat

Landmarks are updated on each frame (approximately every 60ms). The tab "tab_pb_int" is filled with the corresponding integer of each frame.

Then, the most common error triggers an auditory feedback and sets the vibration boolean to True. 
As Mediapipe can have punctual errors on the landmarks, we set a minimal threshold before taking into account the most common error. 


The tab is then reset to see if there is a second error on the same squat (considering that the user is trying to rectify his error during the squat). 

When the vibration boolean is on, if the problem is on the shoulders, the torso, the hips or the knees, the distance between the current value and the normal is calculated and the ID of the vibrator that needs to be on is defined. Then the socket message is sent each frame the error is still on, with real-time value adjustment. 


#### At the end of a squat 
Each time the person has straight legs, the tab of integers is emptied. 
If the previous squat presented no errors, there is an audio feedback to tell the movement was good. 

The program is set to have only one "good squat" audio feedback until one later squat presents errors (that's the role of the squat_ok boolean). 

## Arduino part 
The vibrators are receiving data in Wi-Fi connexion : the computer need to be connected to the same Wi-Fi as the vibrators. This connexion between the laptop code and the Arduino code on the vibrators is done by the socket package. 

Parameters : 

- UDP_IP : to be set according to the IP of each of the 3 vibrators (in the following order : [back, right knee, left knee])

- message : string data converted in bytes, from 0 to 255. 

- the type of problem switches on the matching vibrator and sends the data as long as the problem is on.
