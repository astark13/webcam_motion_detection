from cv2 import cv2
import time, pandas
from datetime import datetime

# !!! The script currently detects motion, BUT doesn't detect when motion stops !!!!

first_frame=None        # none allows you to have a variable without content
status_list=[None,None] # list has to be initiated with two placeholders in order for the motion detection timestamp to work;\
                        # this works based on the change of status from 0 to 1(motion detected) and from 1 to 0 (no more motion)
times=[]
df=pandas.DataFrame(columns=["Start","End"])

video=cv2.VideoCapture(0, cv2.CAP_DSHOW)    # captures image from webcam 0; if there are multiple webcams\
                                            # you can specify which webcam's image to capture (0, 1, 2,...)
                                            # !!! This turns on the camera!!!

while True:
    check, frame = video.read()   # "check" is a boolean variable that has the value TRUE if the video is running;\
                                  # the images are loaded in the "frame" variable
    status=0                      # there is no motion in the frame
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # converts image to grayscale
    gray=cv2.GaussianBlur(gray,(21,21),0)       # blurs image, removes noise, increases accuracy in the calculation\
                                                # of the difference between the original frame and coming frames
                                                # (21,21) = (width,height) of the gaussian kernel ~ blurriness parameters
                                                # 0 = standard deviation
                                                # https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html

    if first_frame is None:        # the first picture recorder by the camera is assigned to the "first_frame" variable
        first_frame=gray           # !!! The first frame must be empty (no one must be in it)\
                                   # so it can stand as reference when someone/-thing enters the frame 
        continue                   # go to the begining of the while loop; stop processing coming lines

    delta_frame=cv2.absdiff(first_frame,gray)              # compare the current frame with the "first_frame"; absolute difference
    
    thresh_frame=cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1] 
                # if the difference between the "first_frame" and the current frame\
                # is more than 30, change the color of those pixels to 255(white)
                # "cv2.THRESH_BINARY" is the threshold method
                # [1] - the cv2.treshold method returns a tuple; from this tuple we need the second value which is the frame itself

    thresh_frame=cv2.dilate(thresh_frame, None, iterations=2)  # remove black holes from the big white areas
                                                               # the idea is that the contur is outlined by a black line???

    (cnts,_)=cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)   
                # find the contours in a copy of "thresh_frame" so it doesn't\
                # modify the original  
                # the "cv2.RETR_EXTERNAL" method draws the external contour of the objects 
                # "cv2.CHAIN_APPROX_SIMPLE" is an approximation method used for retrieving contours                                                     

    for contour in cnts:          
        if cv2.contourArea(contour) < 1000:  # if the area of the contour is smaller than 1000, the loop stops and goes to its beginning
            continue   
        status=1     
        (x, y, w, h)=cv2.boundingRect(contour)          # gets the coordinates for the upper left corner, width and length of the rectangle 
        cv2.rectangle(frame, (x, y), (x+w,y+h), (0,255,0), 3)   # drawsthe rectangle corresponding to "frame"
                                                                # (x, y) - upper left corner
                                                                # (x+w,y+h) - lower left corner
                                                                # (0,255,0) - color of the rectangle
                                                                # 3 - width of the rectangle
    
    status_list.append(status)

    if status_list[-1]==1 and status_list[-2]==0:  # detects status change from 0 to 1 (start of motion)
        times.append(datetime.now())
    if status_list[-1]==0 and status_list[-2]==1:  # detects status change from 1 to 0 (end of motion)
        times.append(datetime.now())

    cv2.imshow("Gray Frame",gray)   # displays the images/video from the camera
    cv2.imshow("Delta Frame",delta_frame)
    cv2.imshow("Threshold Frame",thresh_frame)
    cv2.imshow("Color Frame",frame)

    key=cv2.waitKey(1)             # Waits 1 milisecond until it shows the next frame; basically a video

    if key==ord('q'):              # press "q" to quit
        if status==1:
            times.append(datetime.now())
        break

print(status_list)
print(times)

for i in range(0,len(times),2):   # measures the length of "times" and makes an interration for each pair\
                                  # motion start-motion stop
    df=df.append({"Start":times[i],"End":times[i+1]},ignore_index=True)

df.to_csv("Times.csv")

video.release()                 # !!!This turns off the camera!!!
cv2.destroyAllWindows() 