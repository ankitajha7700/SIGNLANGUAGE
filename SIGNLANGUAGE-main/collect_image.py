

import os
import cv2

DATA_DIR = "D:/b.tech cse/anisha details/website works/signlanguage/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 9
dataset_size = 100

def find_valid_camera():
    for index in range(10):  
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cap.release()
            return index
    return -1

camera_index = find_valid_camera()
if camera_index == -1:
    print("Error: No valid camera found.")
    exit()

cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

for j in range(number_of_classes):
    class_dir = os.path.join(DATA_DIR, str(j))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)
    
    print('Collecting data for class {}'.format(j))

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("Error: Failed to capture image. Please check the camera connection.")
            cap.release()
            cv2.destroyAllWindows()
            exit()
      
        cv2.putText(frame, 'Ready? Press "q"!', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow('frame', frame)
        
        if cv2.waitKey(25) == ord('q'):
            break
    
    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("Error: Failed to capture image. Exiting...")
            cap.release()
            cv2.destroyAllWindows()
            exit()
       
        cv2.imshow('frame', frame)
       
        cv2.imwrite(os.path.join(class_dir, '{}.jpg'.format(counter)), frame)
        counter += 1
        
        cv2.waitKey(25)

cap.release()
cv2.destroyAllWindows()
