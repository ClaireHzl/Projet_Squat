# SQUAT Correction Project

This code allows to get an auditory and vibrotactile feedback on a squat workout. It has been specifically thought to be used by visually impaired people, but it could be used by anyone. 

## Material

### Physical Material 

- 1 or 2 Camera RGB
- 3 wireless vibrators composed of
     - electronics: 1 arduino ESP32 board + battery, 1 ERM motor, 1 switch and optionnaly 1 drv2605l driver (see schematics included)
     - 3d printed casing and elastic straps to fix on users body
- Computer with operational speakers and microphone
- Carpet with rope straps


### Softwares

- Code Editor (Visual Studio Code or else) - *Python language*
- Arduino IDE - *C++ language*

### Set-up
The carpet is placed on the floor. The 3 legs of the camera tripod are deployed to the maximum. The camera is placed at the end of the rope straps and is linked to the computer. The camera must be oriented in profile format (the image is rotated by -90° during pre-processing). 

One vibrator is put in the lower back, the other two are put above the knees. 

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

## How it is working


The algorithm is built as follow :

1. Initialization of all the parameters and the variables needed
   
2.  Speech Recognition : the program awaits for the user to say "oui" to the question "es-tu prêt ?"

3.  Image processing with CV2 and Mediapipe : 

     3.1. Calibration for 5 seconds : recording of all the coordinates, distances, angles of the initial body landmarks via the function *calibration*

     3.2. Detection of errors on the squat workout : calculation of parameters related to the posture of the head, torso, shoulders, hips, knees and feet for each squat.

    If an error is detected in > 7 frames on a single squat, there is an auditory feedback on how to improve the movement.
    
    If that error is linked to the shoulders, hips, torso or knees, the value of the error is sent to the correspondig vibrator and triggers a vibrotactile feedback proportional to this error.

4.  Algorithm exit when the user leaves the scene



## In details 

### MediaPipe

After preprocessing the image using OpenCV, we use Mediapipe to get human body landmarks as follow. MediaPipe is an opensource program of machine learning from Google. We use the [Pose Landmark Detection](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker) solution. 

![landmarks](https://camo.githubusercontent.com/54e5f06106306c59e67acc44c61b2d3087cc0a6ee7004e702deb1b3eb396e571/68747470733a2f2f6d65646961706970652e6465762f696d616765732f6d6f62696c652f706f73655f747261636b696e675f66756c6c5f626f64795f6c616e646d61726b732e706e67)



### Calibration

The function *calibration* is used as below. 

For 5 seconds, each landmarks coordinates on every frame is captured, then the median is saved as *landmark_init*.

From that, we extract :
- the *ind_side* and *ind_other_side* : integers  corresponding to the side closer to the camera and the other side (defined by the toe y-coordinate higher than the other). Useful to generalize to the symetric position. 
    
    *The* side *and* other_side *are the strings (left/right) corresponding to the closer side and the other one, used in the written feedback for the developer.*

- the *normal_dist* : distance between the left shoulder and the left heel. Used to normalize all the other distances between 2 points (useful to generalize the algorithm for people of all sizes).

- the *ligne_feet_init* : angle between the horizontal and the ligne between toes. Used to normalize all the ligne orientation values (useful to generalize the algorithm to the initial orientation of the person).

Then, all needed distances, line orientations and angles are determined according to the overlying values. 


### Errors ID

Each error type is characterized by an integer from 1 to 23. They are structured according to an order of priority based on the importance of the error, established by a sports professional.

Therefore, according to the coordinates, angles and distances of the landmarks, if an error is detected, the corresponding integer will be output. If not, it's a good squat, the corresponding integer is 0. 


### On each squat

Landmarks are updated on each frame (approximately every 60ms). The tab "tab_pb_int" is filled with the corresponding integer of each frame.

Then, the most common error triggers an auditory feedback and sets the vibration boolean to True. 
As Mediapipe can have punctual errors on the landmarks, we set a minimal threshold before taking into account the most common error. 


The tab is then reset to see if there is a second error on the same squat (considering that the user is trying to rectify his error during the squat). 

When the vibration boolean is on, if the problem is on the shoulders, the torso, the hips or the knees, the distance between the current value and the normal is calculated and the ID of the vibrator that needs to be on is defined. Then the socket message is sent each frame the error is still on, with real-time value adjustment. 


### At the end of a squat 
Each time the person has straight legs, the tab of integers is emptied. 
If the previous squat presented no errors, there is an audio feedback to tell the movement was good. 

The program is set to have only one "good squat" audio feedback until one later squat presents errors (that's the role of the squat_ok boolean). 

## Vibrators

### Electronics

### Code
The vibrators and computer are connected to a local Wi-Fi.
We chose Udp as communication protocol because there is no need to protect the data as they are not sensitive, and it was simpler and faster not to send data from the vibrators to the computer.
So there is only a Udp socket sending relevant data to each vibrator's IP adress : the type of problem switches on the matching vibrator, converts the error in bytes and send the message as long as the problem is on.The only drawback is that you have to know this IP beforehand and that the registration is not automatic.

Other than that the code is pretty straightforward : 
- for the first version the ESP32 board reads packages coming from the Udp socket, generates a PWM signal proportionnal to the value read and outputs it to the GPIO pin that is connected to the motor
- for the second version, two threads run in parallel in order to have a real time precise control of the vibratory frequence : one thread tasked to read the Udp socket and update the value of the message (global parameter), and the other one tasked with controlling the vibration through the driver.

## Areas of improving 

### Pose detection

Mediapipe has been much used on pose detection in scientific litterature, but the accuracy is not perfect, depending on the angle of image acquisition and the color conditions (mean REMS of 12.5° in estimation of the knee angle on a squat, in the article from Dill and al [[1]](https://www.researchgate.net/publication/374081734_Accuracy_Evaluation_of_3D_Pose_Estimation_with_MediaPipe_Pose_for_Physical_Exercises)). 

Another study seems to find a better performance with [MoveNet](https://www.tensorflow.org/hub/tutorials/movenet?hl=en) when the pose detection is made on a video capture [[2](https://www.mdpi.com/1999-5903/14/12/380)] and the opensource YOLO program seems to have very good results too, especially the new version [YOLO NAS POSE](https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS-POSE.md), but we couldn't find any litterature to have objective measures, as the version is very recent. 
