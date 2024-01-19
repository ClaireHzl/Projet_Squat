# SQUAT Detection Project

This code allows to get an auditory and haptic feedback on squat workout. It has been specifically thought to be used by visually impaired people, but it could be used by anyone.

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

## Algorithm part

The algorithm is built as follow :

1. Speech Recognition : the program awaits for the user to say "oui" to the question "es-tu prêt ?"

2. Image processing with CV2 and Mediapipe  : 

     2.1. Calibration for 5 seconds : recording of all the coordinates, distances, angles of the initial body landmarks

     2.2. Detection of errors on squat workout : calculation of parameters related to the posture of the head, torso, shoulders, hips, knees and feet for each squat.
         If an error is detected in > 7 frames on a single squat, there is an auditory feedback on how to improve the movement.
         If that error is linked to the shoulders, hips, or torso, there is also a vibratory feedback on the back. If that error is linked to one of the knees, there is a vibratory feedback on the knee involved.

4. Stop when the user leaves the scene


## Arduino part 
