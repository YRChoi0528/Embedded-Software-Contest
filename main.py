import cv2
import math
import numpy as np
import serial
import time
import motion
import alpha_dir
from threading import Thread

def Receiving(ser):
    global receiving_exit

    global X_255_point
    global Y_255_point
    global X_Size
    global Y_Size
    global Area, Angle

    receiving_exit = 1
    while True:
        if receiving_exit == 0:
            break
        time.sleep(threading_Time)
        while ser.inWaiting() > 0:
            result = ser.read(1)
            RX = ord(result)
            print("RX=" + str(RX))

serial_use = 1

serial_port = None
Read_RX = 0
receiving_exit = 1
threading_Time = 0.01

BPS = 4800

serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
serial_port.flush()

serial_t = Thread(target=Receiving, args=(serial_port,))

serial_t.daemon = True
serial_t.start()
time.sleep(0.1)

yr = motion.Robot(serial_port)

abcd = 0
step = 0
leg = 0

direction = 0
cardinal_points_finish = 0
cardinal_points_start = 1 #user choice

def walk(leg):
    if leg == 0:
        yr.go_left()
        return 1;
    else:
        yr.go_right()
        return 0;

def check_point(new_array, num, x_y): #0=up,left, height-1=down, width-1=right//x_y=0=up,down, x_y=1=right,left
    d_v = [0,0]
    n=0
    if x_y ==0:
        k=1
    else:
        k=0
    for i in range(0,new_array.shape[0]):
        if new_array[i][k] == num:
            d_v[n] = new_array[i][x_y]
            if n == 1:
                d_v.sort()
                return d_v
            n=1

def line_point_check():
    right_point = [0,0]
    left_point = [0,0]
    up_point = [0,0]
    down_point = [0,0]
    
    l_yellow = (20, 70, 70)
    u_yellow = (45, 255, 255)

    W_View_size = 320
    H_View_size = int(W_View_size / 1.333)
    
    cap = cv2.VideoCapture(0)
    cap.set(3, W_View_size) #320
    cap.set(4, H_View_size) #240
    _,frame = cap.read()
    line_frame = frame[0:200,0:320].copy()
    height, width, _ = line_frame.shape #height:150, width:320
    blur = cv2.GaussianBlur(line_frame, (3,3), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, l_yellow, u_yellow)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        contour_array = c.shape
        
        new_array = np.squeeze(c, axis=1) 
        
        right_p = check_point(new_array, width-1, 1)
        left_p = check_point(new_array, 0, 1)
        up_p = check_point(new_array, 0, 0)
        down_p = check_point(new_array, height-1, 0)
        
        y_min = np.min(new_array,axis=0)[1]
        y_max = np.max(new_array,axis=0)[1]
        x_min = np.min(new_array,axis=0)[0]
        x_max = np.max(new_array,axis=0)[0]
        
        cv2.imwrite(f'cap/hi.jpg', line_frame)
        
    cv2.destroyAllWindows()
    return right_p, left_p, up_p, down_p, y_min, y_max, x_min, x_max, width, height

yr.head_180()
q = 0
while True:
    if step != 4:
        try:
            right_point, left_point, up_point, down_point, y_min, y_max, x_min, x_max, width, height = line_point_check()
        except:
            alpha_dir.capimg(name = q)
            q+=1
            #leg = walk(leg)
        else:
            print(right_point)
            print(left_point)
            print(up_point)
            print(down_point)
            print(y_min,y_max,x_min,x_max)
            
            if step == 0: # Start Point
                direction = 1
                cardinal_points_finish = 4
                step = 1
                
            elif step == 1: # Before T
                if down_point != None:
                    if up_point != None:
                        if right_point == None and left_point == None:
                            if up_point[1] - down_point[1] > 30:
                                yr.right_turn()
                            elif down_point[1] - up_point[1] > 30:
                                yr.left_turn()
                            elif down_point[0] > 160:
                                yr.right_walk()
                            elif down_point[1] < 100:
                                yr.left_walk()
                            else:
                                leg = walk(leg)
                        else:
                            if down_point[0] > 160:
                                yr.right_walk()
                            elif down_point[1] < 100:
                                yr.left_walk()
                            elif np.median(up_point) - np.median(down_point) > 30:
                                yr.left_turn()
                            elif np.median(down_point) - np.median(up_point) > 30:
                                yr.right_turn()
                            else:
                                leg = walk(leg)
                    else: #up_point X
                        if right_point != None and left_point != None:
                            if right_point[1] - left_point[1] > 30:
                                yr.right_turn()
                            elif left_point[1] - right_point[1] > 30:
                                yr.left_turn()
                            elif down_point[0] > 160:
                                yr.right_walk()
                            elif down_point[1] < 100:
                                yr.left_walk()
                            elif np.median(right_point) > height*0.5 and np.median(left_point) > height*0.5:
                                if direction == 1:
                                    yr.right_turn90()
                                    leg = walk(leg)
                                else:
                                    yr.left_turn90()
                                    leg = walk(leg)
                                step = 2
                            else:
                                leg = walk(leg)
                            
                        
            elif step == 2: # After T
                if down_point != None:
                    if down_point[1] - down_point[0] > 60 and left_point == None and right_point == None:
                        leg = walk(leg)
                        continue
                    if up_point != None:
                        if right_point == None and left_point == None:
                            if up_point[1] - up_point[0] > 60:
                                if direction == -1:
                                    yr.left_turn()
                                else:
                                    yr.right_turn()
                            else:
                                if up_point[1] - down_point[1] > 30:
                                    yr.right_turn()
                                elif down_point[1] - up_point[1] > 30:
                                    yr.left_turn()
                                elif down_point[0] > 160:
                                    yr.right_walk()
                                elif down_point[1] < 100:
                                    yr.left_walk()
                                else:
                                    leg = walk(leg)
                        else:
                            step = 3
                            
                    else: #up_point X
                        if down_point[0] > 160:
                            yr.right_walk()
                            continue
                        elif down_point[1] < 100:
                            yr.left_walk()
                            continue
                        if right_point != None and left_point == None:
                            if right_point[1] - right_point[0] > 60:
                                yr.right_turn()
                                continue
                            else:
                                if right_point[0] - y_min > 30:
                                    yr.right_turn()
                                    continue
                                elif down_point[0] - x_min > 30:
                                    yr.left_turn()
                                    continue
                            if np.median(right_point) > height*0.5:
                                step = 4
                            else:
                                leg = walk(leg)
                            
                        elif right_point == None and left_point != None:
                            if left_point[1] - left_point[0] > 60:
                                yr.left_turn()
                                continue
                            else:
                                if left_point[0] - y_min > 30:
                                    yr.left_turn()
                                    continue
                                elif x_max - down_point[1] > 30:
                                    yr.right_turn()
                                    continue
                            if np.median(left_point) > height*0.5:
                                step = 4
                            else:
                                leg = walk(leg)
                else: #down_point X
                    if right_point != None:
                        yr.right_walk()
                    elif left_point != None:
                        yr.left_walk()
                
            if step == 3: #down O, up O
                if direction == 1:
                    if left_point != None and right_point == None:
                        if down_point[0] > 160:
                            yr.right_walk()
                        elif down_point[1] < 100:
                            yr.left_walk()
                        else:
                            leg = walk(leg)
                    elif left_point == None and right_point != None:
                        if up_point[0] - down_point[0] > 30:
                            yr.right_turn()
                            continue
                        elif down_point[0] - up_point[0] > 30:
                            yr.left_turn()
                            continue
                        elif down_point[0] > 160:
                            yr.right_walk()
                            continue
                        elif down_point[1] < 100:
                            yr.left_walk()
                            continue
                        if np.median(right_point) > height*0.5:
                            if cardinal_points_start == cardinal_points_finish:
                                yr.right_turn90()
                                leg = walk(leg)
                                step = 6
                            else:
                                leg = walk(leg)
                        else:
                            leg = walk(leg)
                    else:
                        yr.left_walk()
                else: #direction = -1
                    if left_point == None and right_point != None:
                        if down_point[0] > 160:
                            yr.right_walk()
                        elif down_point[1] < 100:
                            yr.left_walk()
                        else:
                            leg = walk(leg)
                    elif left_point != None and right_point == None:
                        if up_point[1] - down_point[1] > 30:
                            yr.left_turn()
                            continue
                        elif down_point[1] - up_point[1] > 30:
                            yr.right_turn()
                            continue
                        elif down_point[0] > 160:
                            yr.right_walk()
                            continue
                        elif down_point[1] < 100:
                            yr.left_walk()
                            continue
                        if np.median(left_point) > height*0.5:
                            if cardinal_points_start == cardinal_points_finish:
                                yr.left_turn90()
                                leg = walk(leg)
                                step = 6
                            else:
                                leg = walk(leg)
                        else:
                            leg = walk(leg)
                    else:
                        yr.left_walk()
                step = 2
                
            elif step == 5:
                if up_point != None:
                    if up_point[1] - up_point[0] > 60:
                        leg = walk(leg)
                    else:
                        if up_point[1] < 100:
                            yr.left_walk()
                            continue
                        elif up_point[0] > 160:
                            yr.right_walk()
                            continue
                        if direction == 1:
                            if right_point != None:
                                if np.median(right_point) > height*0.5:
                                    yr.right_turn90()
                                    leg = walk(leg)
                                    step = 2
                                else:
                                    leg = walk(leg)
                        else:
                            if left_point != None:
                                if np.median(left_point) > height*0.5:
                                    yr.left_turn90()
                                    leg = walk(leg)
                                    step = 2
                                else:
                                    leg = walk(leg)
                
                    
            elif step == 6:
                leg=walk(leg)
                if right_point == None and left_point == None and up_point == None and down_point == None:
                    print("Clear!")
                    break
        
        
         
    elif step == 4:
        if not abcd:
            yr.head_110()
            abcd = alpha_dir.abcd()
        if direction == 1:
            yr.left_walk()
        else:
            yr.right_walk() 
        yr.walk12()
        if direction == 1:
            yr.right_turn90()
        else:
            yr.left_turn90()
        print('1')
        yr.head_140()
        print('2')
        mission = alpha_dir.mission()
        print(mission)
        if mission == 'stair':
            yr.head_180()
            while True:
                clr = alpha_dir.color_green()
                if clr[0] - clr[1] > 40:
                    if clr[1] == 0:
                        yr.left_walk()
                    else:
                        yr.left_turn()
                elif clr[1] - clr[0] > 40:
                    if clr[1] == 0:
                        yr.right_walk()
                    else:
                        yr.right_turn()
                else:
                    if clr[0] > 160 and clr[1] > 160:
                        yr.up_stair()
                        break
                    else:
                        leg = walk(leg)
                if direction == 1:
                    yr.right_turn180()
                else:
                    yr.left_turn180()
                    
                yr.down_stair()  
            
        else:
            print('4')
            flag = 0
            yr.head_120()
            while True:
                middle = alpha_dir.dangerous()
                if middle[0] < 120:
                    yr.left_walk()
                elif middle[0] > 200:
                    yr.right_walk()
                else:
                    if middle[1] < 180:
                        leg = walk(leg)
                    else:
                        if flag == 0:
                            yr.head_140()
                            flag = 1
                        elif flag == 1:
                            yr.head_160()
                            flag = 2
                        elif flag == 2:
                            alpha_dir.capimg(name = 'pickup')
                            yr.pick_up()
                            break
            yr.head_180()
                
        if cardinal_points_start == 4 and direction == 1:
            cardinal_points_start = 1
        elif cardinal_points_start == 1 and direction == -1:
            cardinal_points_start = 4
        else:
            cardinal_points_start = cardinal_points_start + direction
        step = 5
    
