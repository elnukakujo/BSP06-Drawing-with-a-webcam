# BSP06-Drawing-with-a-webcam
This project consists in understanding and using the existing features to produce a webcam drawing program.
It has been made with the supervision of Luis Leiva, researcher at University of Luxembourg, as part of my studies.

The produced program uses mainly Mediapipe to detect users' hands, and gives them two simple possibilities: draw and change colors.
This program helped me to take a step forward in Computer Vision, and how to treat the informations collected.

![image_2022-05-29_103351155](https://user-images.githubusercontent.com/61209679/170859413-5f662fdb-8b7c-4dc0-baed-8b0122b3c74d.png)

The program detects users hands and has two possibilities: if the hand has only its index up, it starts to draw a line from it, if the index and the middle are up, it detects the color right above the index, and apply it to the existing and future lines.

To detects if a finger is raised or not, it uses the Mediapipe hand landmarks of the concerned fingers and compare its tip coordinates with the landmark coordinates right below. For the index, it compares the coordinates of 8 and 7. Finally, if all the fingers are closed, it ends the program.
![hand_landmarks](https://user-images.githubusercontent.com/61209679/170859033-88c92191-c6f4-4582-aac3-45b0998c78be.png)

As more lines are draw, previous lines slowly disappears. When 40 lines have been draw, it removes the oldest one.

To avoid unexpected program closures, I implemented a system of finger state (open/close) remembrance, so that if, by mistake, the program detects that the hand is closed for less than half their remembrance, it won't apply this command. This allows the program to not close at each landmarks error.
