import cv2 as cv
import numpy as np
from cv2 import VideoCapture
from gpiozero import LED
import time
from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#cam = VideoCapture(0)
#cam.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))
max_area = 0
count_violet=0
count_red=4
count_orange=8
list_angle=[]
list_color=[]
pulse=0
step=LED(23)
dire=LED(24)
motor=LED(20)
x24=LED(4)
x25=LED(17)
x26=LED(27)
x27=LED(22)
x28=LED(5)
sensor1=6
sensor2=13
rotary=21
status = 'home'
now_sensor1 = False
now_sensor2 = False

# set up
GPIO.setup(sensor1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # sensor 1
GPIO.setup(sensor2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # sensor 2
GPIO.setup(rotary, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # run
motor.on()

while True:
    '''cam.release()
    cam = VideoCapture(0)    
    cam.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))
    result, img = cam.read()''' 
    time.sleep(.15)
    pre_sensor1 = now_sensor1
    now_sensor1 = GPIO.input(sensor1)    
    if (now_sensor1 ==True) and (pre_sensor1 == False):   
            cam = VideoCapture(0)    
            cam.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))
            result, img = cam.read()
            time.sleep(.1)
            '''while result == False:
                #cam.release()
                #cam = VideoCapture(0)    
                #cam.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))
                result, img = cam.read()'''                
            cam.release()
            if result:
                img=img[50:450,225:495]  % Lay mot vung anh nhat dinh (ROI) boi vi vat the luon xuat hien trong vung do
                hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)                
                # hsv for orange color
                lower_bound = np.array([0,0,0])   
                upper_bound = np.array([20,255,255])
                mask_o= cv.inRange(hsv, lower_bound, upper_bound)
                #check_o=np.where(mask_o!=0)
                # hsv for violet color
                lower_bound = np.array([110,0,200])   
                upper_bound = np.array([145,255,255])
                mask_v= cv.inRange(hsv, lower_bound, upper_bound)
                #check_v=np.where(mask_v!=0) 
                # hsv for red color
                lower_bound = np.array([150,0,0])   
                upper_bound = np.array([175,150,255])
                mask_r= cv.inRange(hsv, lower_bound, upper_bound)
                #check_r=np.where(mask_r!=0)
            
                # Check kind signs
                if np.size(np.where(mask_v!=0)) > 30000 :
                    mask = mask_v
                    if count_violet>=4:
                        count_violet=1
                        
                    else:
                        count_violet+=1
                    list_color.append(count_violet)
                    print('violet',count_violet)
                elif np.size(np.where(mask_o!=0)) > 20000:
                    mask = mask_o
                    if count_orange>=12:
                        count_orange=9
                    else:
                        count_orange+=1
                    list_color.append(count_orange)          
                    print('orange',count_orange)
                elif np.size(np.where(mask_r!=0)) > 40000 :
                    mask = mask_r
                    if count_red>=8:
                        count_red=5
                    else:
                        count_red+=1
                    list_color.append(count_red)
                    print('red',count_red)
                
                else:
                    mask = 0
                
                #element= cv.getStructuringElement(cv.MORPH_RECT,(1,3))
                mask=cv.morphologyEx(mask,cv.MORPH_OPEN ,cv.getStructuringElement(cv.MORPH_RECT,(1,3)),iterations=2)    
                #check=np.where(mask!=0)
                cv.imshow('mask',mask)            
                cv.waitKey(1000)
                
                # calcular angle
                if np.size(np.where(mask!=0))>10000:                
                    contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_NONE) 
                    for c in contours: 
                        area = cv.contourArea(c)
                        if area>max_area:   
                            contour = c 
                            max_area = area                        
                      
                    if max_area != 0: 
                        max_area = 0                   
                        rect = cv.minAreaRect(contour)
                        box = cv.boxPoints(rect)
                        box = np.int0(box)
                        cv.drawContours(img,[box],0,(0,0,255),2)
                        angle = int(rect[2])
                        print('1.',angle)
                        if angle > 45:
                            angle = angle - 90
                            
                        print('2.',angle)
                        list_angle.append(angle)
    
    pre_sensor2 = now_sensor2
    now_sensor2 = GPIO.input(sensor2)        
    if now_sensor2 == True and pre_sensor2 == False: # cạnh lên sensor 2
             
        if len(list_color) != 0 and len(list_angle) != 0:
            time.sleep(abs(list_angle[0]/450))
            motor.off()
            color =list_color[0]            
            if color == 1:
                x24.on()
                x25.off()
                x26.off()
                x27.off()
            elif color == 2:
                x24.off()
                x25.on()
                x26.off()
                x27.off()
            elif color == 3:
                x24.on()
                x25.on()
                x26.off()
                x27.off()
            elif color == 4:
                x24.off()
                x25.off()
                x26.on()
                x27.off()
            elif color == 5:
                x24.on()
                x25.off()
                x26.on()
                x27.off()
            elif color == 6:
                x24.off()
                x25.on()
                x26.on()
                x27.off()
            elif color == 7:
                x24.on()
                x25.on()
                x26.on()
                x27.off()
            elif color == 8:
                x24.off()
                x25.off()
                x26.off()
                x27.on()
            elif color == 9:
                x24.on()
                x25.off()
                x26.off()
                x27.on()
            elif color == 10:
                x24.off()
                x25.on()
                x26.off()
                x27.on()
            elif color == 11:
                x24.on()
                x25.on()
                x26.off()
                x27.on()
            elif color == 12:
                x24.off()
                x25.off()
                x26.on()
                x27.on()
                
        x28.on()      
            
    if pre_sensor2 == True and now_sensor2==False: # Cạnh xuống sensor 2
        x24.off()    
        x25.off()
        x26.off()
        x27.off()  
        x28.off()  
        '''if len(list_color)!= 0:            
            del list_color[0] '''
            
        #time.sleep(.1)
        motor.on()     
             
    if (GPIO.input(rotary)==True) and (status == 'home'): # Quay step
        if len(list_angle)!=0 :        
            pulse = int(list_angle[0]/0.9)
            if pulse > 0:
                dire.off()   
            else:
                dire.on()    
            
            for i in  range(0,abs(pulse)):
                step.on()
                time.sleep(.001)
                step.off()
                
            status = 'complete'
        
        
    if (GPIO.input(rotary)==False) and (status =='complete'): # Home step
        if pulse > 0:
            dire.on()   
        else:
            dire.off()
            
        for i in  range(0,abs(pulse)):
            step.on()
            time.sleep(.001)
            step.off()
                        
        status = 'home'
        pulse = 0
        
        if len(list_angle)!=0 : 
            del list_angle[0]
            
        if len(list_color)!=0 : 
            del list_color[0]
    
