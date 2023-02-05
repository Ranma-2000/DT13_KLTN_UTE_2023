import cv2 as cv
import numpy as np
from cv2 import VideoCapture
import time
from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Variable 
max_area = 0
list_angle=[]
list_color=[]
pulse=0
step=23
dire=25
motor=26
x24=19
x25=17
x26=22
sensor1=21
sensor2=16
y5b = 5

# set up
GPIO.setup(step, GPIO.OUT,initial=False)
GPIO.setup(dire, GPIO.OUT,initial=False)
GPIO.setup(motor, GPIO.OUT,initial=False)
GPIO.setup(x24, GPIO.OUT,initial=False)
GPIO.setup(x25, GPIO.OUT,initial=False)
GPIO.setup(x26, GPIO.OUT,initial=False)
GPIO.setup(sensor1, GPIO.IN) 
GPIO.setup(sensor2, GPIO.IN) 
GPIO.setup(y5b, GPIO.IN) 

now_sensor1 = GPIO.input(sensor1)  
now_sensor2 = GPIO.input(sensor2) 
status_system = 'run'

cam = VideoCapture(0)    
cam.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc('M','J','P','G'))

while True:
    
    pre_sensor1 = now_sensor1
    now_sensor1 = GPIO.input(sensor1) 
    result, img = cam.read()
    if (now_sensor1 ==True) and (pre_sensor1 == False):  
        #time.sleep(0.6)
        result, img = cam.read()                   
        #cam.release()
        if result:
            #print('    ')
            img=img[100:360,200:700]
            gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)[1]
            img_a = cv.inpaint(img,thresh,3,cv.INPAINT_TELEA)
            
            # color bounds
            # red (B G R)
            # Co upper_bound va lower_bound de loc mau do tuy theo do sang va goc chieu sang
            lower_bound = np.array([30,10,150],dtype = "uint8")   
            upper_bound = np.array([130,110,255],dtype = "uint8")
            mask_r= cv.inRange(img_a, lower_bound, upper_bound)
            check_r=np.where(mask_r!=0)
            # violet
            lower_bound = np.array([120,110,125],dtype = "uint8")   
            upper_bound = np.array([255,210,230],dtype = "uint8")
            mask_v= cv.inRange(img_a, lower_bound, upper_bound)
            check_v=np.where(mask_v!=0)
            # orange 
            lower_bound = np.array([0,80,170],dtype = "uint8")   
            upper_bound = np.array([100,180,255],dtype = "uint8")
            mask_o= cv.inRange(img_a, lower_bound, upper_bound)
            check_o=np.where(mask_o!=0)
        
            # Check color type
            if np.size(np.where(mask_v!=0)) > 30000 :
                mask = mask_v                    
                list_color.append(1)
                print('violet')
                print(' ')
            elif np.size(np.where(mask_o!=0)) > 30000:
                mask = mask_o
                list_color.append(3)          
                print('orange')
                print(' ')
            elif np.size(np.where(mask_r!=0)) > 40000 :
                mask = mask_r
                list_color.append(2)
                print('red')               
            else:
                mask = 0
            
            mask=cv.morphologyEx(mask,cv.MORPH_OPEN ,cv.getStructuringElement(cv.MORPH_RECT,(1,3)),iterations=2) 
            
            
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
                    rect = cv.minAreaRect(contour)  # (x1, y1) (x2, y2) angle
                    box = cv.boxPoints(rect)  # Tu 3 gia tri o tren, ham nay se tinh ra 4 dinh cua hinh chu nhat
                    box = np.int0(box)  # int0 is int64
                    cv.drawContours(img_a,[box],0,(0,0,255),2)
                    angle = int(rect[2])
                    print('1.',angle)
                    if angle > 45:
                        angle = angle - 90
                        
                    print('2.',angle)
                    list_angle.append(angle)
                    cv.imshow('img',img_a)   
                    cv.imshow('mask',mask)         
                    cv.waitKey(500)
                    
        print('color ',list_color)
        print('angle ',list_angle)
        print(' ')
                
    
    pre_sensor2 = now_sensor2
    now_sensor2 = GPIO.input(sensor2)
    status_motor = GPIO.input(y5b)     
    if status_motor == True and status_system == 'run':
        GPIO.output(motor, True)
    elif status_motor == False:
        GPIO.output(motor, False)
        
    if now_sensor2 == True and pre_sensor2 == False and status_motor == True: # cạnh lên sensor 2         
        if len(list_angle)!=0 and len(list_color) != 0: 
            time.sleep(abs(list_angle[0]/150) + 0.3)
            GPIO.output(motor, False) 
            status_system = 'wating'       
            
            
            pulse = int(list_angle[0]/1.8) 
            if pulse < 0: # Step về home
                GPIO.output(dire,True)  
                GPIO.output(dire,True)
            else:
                GPIO.output(dire,False) 
                GPIO.output(dire,False)  
            
            time.sleep(0.1)    
            for i in  range(0,abs(pulse)):                
                GPIO.output(step,True) 
                time.sleep(.001)
                GPIO.output(step,False)
                time.sleep(.001)  
          
            sleep(0.5)               
            print('Waiting ...')
            print(' ')
            color = 0
            color =list_color[0]            
            if color == 1: # Violet
                GPIO.output(x24,True)
                GPIO.output(x24,True)
                GPIO.output(x25,False) 
                GPIO.output(x25,False)
                GPIO.output(x26,False) 
                GPIO.output(x26,False)
            elif color == 2: # Red
                GPIO.output(x25,True)
                GPIO.output(x25,True)
                GPIO.output(x24,False)                
                GPIO.output(x24,False)
                GPIO.output(x26,False) 
                GPIO.output(x26,False)
            elif color == 3: # Orange 
                GPIO.output(x26,True)
                GPIO.output(x26,True) 
                GPIO.output(x24,False) 
                GPIO.output(x24,False)
                GPIO.output(x25,False) 
                GPIO.output(x25,False)
     
            
    if now_sensor2 == False and pre_sensor2 == True and status_motor == True: # cạnh xuống sensor 2
        if len(list_angle)!=0 and len(list_color) != 0:
            status_system = 'run' 
            if pulse > 0: # Step về home
                GPIO.output(dire,True)  
                GPIO.output(dire,True)
            else:
                GPIO.output(dire,False) 
                GPIO.output(dire,False) 
            
            time.sleep(0.1)    
            for i in  range(0,abs(pulse)):
                GPIO.output(step,True) 
                time.sleep(.001)
                GPIO.output(step,False)     
                time.sleep(.001)       
             
            del list_angle[0] 
            del list_color[0]
        
            pulse = 0
            GPIO.output(motor,True) 
            GPIO.output(x24,False) 
            GPIO.output(x24,False)
            GPIO.output(x25,False) 
            GPIO.output(x25,False)
            GPIO.output(x26,False) 
            GPIO.output(x26,False)
            print('delete color ',list_color)
            print('delete angle ',list_angle)
            print('Rotary complete')
            print(' ')
        
      

        
  
