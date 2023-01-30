# Playing Video using Python
# Source: https://www.youtube.com/watch?v=vvq6xRziKns

import cv2
from time import sleep

video_file_name = "/home/carlosm/Videos/carlosm_video_test.mp4"

# Open video file
print(f"Playing file: {video_file_name}")
cap = cv2.VideoCapture(video_file_name)

# Loop through all frames
while(cap.isOpened()):
    ret, frame = cap.read()
    frame = cv2.resize(frame, (600,350) )
    cv2.imshow("video", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        print("User quit...")
        break

    sleep(0.05)

# Cleanup
print(f"The End! \nCapture Status={cap.isOpened()}")
sleep(5)
cap.release()
cv2.destroyAllWindows()




