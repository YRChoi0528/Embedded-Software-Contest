import cv2
import math
import numpy as np
import serial
import time
import motion
import copy
import os
from threading import Thread

def line_trace():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	
	l_yellow = (20, 70, 70)
	u_yellow = (45, 255, 255)
	
	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size) - 90
	
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size
	
	right_point = [0,0]
	left_point = [0,0]
	up_point = [0,0]
	down_point = [0,0]
	
	_,frame = cap.read()
	line_frame = frame[y0:y1, x0:x1].copy()
	height, width, _ = line_frame.shape
	blur = cv2.GaussianBlur(line_frame, (3,3), 0)
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, l_yellow, u_yellow)
	contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	if len(contours) > 0:
		c = max(contours, key=cv2.contourArea)
		contour_array = c.shape
		new_array = np.squeeze(c, axis=1)
		n = 0
		for i in range(0, new_array.shape[0]):
			if new_array[i][0] == width-1:
				right_point[n] = new_array[i][1]
				if n == 1:
					right_point.sort()
					n=0
				n=1
		n = 0
		for i in range(0, new_array.shape[0]):
			if new_array[i][0] == 0:
				left_point[n] = new_array[i][1]
				if n == 1:
					left_point.sort()
					n=0
				n=1
		n = 0
		for i in range(0, new_array.shape[0]):
			if new_array[i][1] == 0:
				up_point[n] = new_array[i][0]
				if n == 1:
					up_point.sort()
					n=0
				n=1
		n = 0
		for i in range(0, new_array.shape[0]):
			if new_array[i][1] == height-1:
				down_point[n] = new_array[i][0]
				if n == 1:
					down_point.sort()
					n=0
				n=1
		y_min = np.min(new_array,axis=0)[1]
		y_max = np.max(new_array,axis=0)[1]
		x_min = np.min(new_array,axis=0)[0]
		x_max = np.max(new_array,axis=0)[0]
		cv2.destroyAllWindows()
		return right_point, left_point, up_point, down_point, y_min, y_max, x_min, x_max, height, width

def direction():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, FPS) 
	
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size - 40
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	lth = [0]*v #rlfdl
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape
	frame = frame[y0:y1, x0:x1].copy()
	check_box = frame[y0:y1, x0:x1].copy()
	cv2.rectangle(frame,(x0,y0),(x1,y1),(0,255,0),2,cv2.LINE_4,0)

	hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	for x in range(0,x1-x0,10):
		for y in range(0,y1-y0):
			pixel2 = hsv2[y,x]
			V_value = pixel2[2]
			
			if V_value < 30:
				pixel2[0] = 100
				pixel2[1] = 100
				pixel2[2] = 100
				cnt += 1
			else:
				pixel2[0] = 255
				pixel2[1] = 255
				pixel2[2] = 255
				if cnt >= 1:
					lth[i] = cnt
					cnt = 0
		i+=1
	i = 0
	vs = ve = 0
	for j in range(v):
		if lth[j] != 0:
			vs = j
			break
	for j in range(v-1,-1,-1):
		if lth[j] != 0:
			ve = j
			break

	cv2.destroyAllWindows()
	if vs != ve:
		if (lth.index(max(lth))-vs) > (ve-vs)/2:
			return 'right'
		else:
			return 'left'
def directionWC():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, FPS) 
	
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size - 40
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)
	
	lth = [0]*v #rlfdl
	i = 0

	_,frame = cap.read()
	height, width, _ = frame.shape
	frame = frame[y0:y1, x0:x1].copy()
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	for x in range(0,x1-x0,10):
		for y in range(0,y1-y0):
			pixel2 = hsv2[y,x]
			V_value = pixel2[2]
			
			if V_value < 30:
				pixel2[0] = 100
				pixel2[1] = 100
				pixel2[2] = 100
				cnt += 1
			else:
				pixel2[0] = 255
				pixel2[1] = 255
				pixel2[2] = 255
				if cnt >= 1:
					lth[i] = cnt
					cnt = 0
		i+=1
	i = 0
	vs = ve = 0
	for j in range(v):
		if lth[j] != 0:
			vs = j
			break
	for j in range(v-1,-1,-1):
		if lth[j] != 0:
			ve = j
			break

	cv2.destroyAllWindows()
	if vs != ve:
		if (lth.index(max(lth))-vs) > (ve-vs)/2:
			print('right')
		else:
			print('left')
	flag = 0
	mx = my = 1
	nparr = np.array([100,100,100])
	hsv_mask = cv2.inRange(hsv, nparr, nparr)  
	hsv = cv2.bitwise_and(hsv, hsv, mask = hsv_mask) #black line extract
	hsv_mask = cv2.inRange(hsv2, nparr, nparr)  
	hsv2 = cv2.bitwise_and(hsv2, hsv2, mask = hsv_mask)
	while(True):
		cv2.imshow('result0', hsv2)
		cv2.imshow('result', frame)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	return frame

def news():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, FPS)
	
	x0 = 0
	x1 = 320
	y0 = 90
	y1 = 220
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)
	 
	vrc = [0]*v #tpfh (380 - 265)/10
	wid = [0]*w #rkfh (340 - 180)/5
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	check_box = frame[y0:y1, x0:x1].copy()
	cv2.rectangle(frame,(x0,y0),(x1,y1),(0,255,0),2,cv2.LINE_4,0)

	hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	count = 0 #black line count

	for y in range(0, y1-y0, 5):    
		count = 0
		for x in range(0,x1-x0):
			pixel = hsv[y,x]
			V_value = pixel[2]
			if V_value < 65:
				pixel[0] = 100
				pixel[1] = 100
				pixel[2] = 100
				cnt = 1
			else:
				pixel[0] = 255
				pixel[1] = 255
				pixel[2] = 255
				if cnt == 1:
					count = count + 1
					cnt = 0
		wid[i] = count
		i+=1
	i = 0
	cnt = 0
	count = 0
	for x in range(0,x1-x0,10):
		count = 0
		for y in range(0,y1-y0):
			pixel2 = hsv2[y,x]
			V_value = pixel2[2]
			
			if V_value < 85:
				pixel2[0] = 100 
				pixel2[1] = 100
				pixel2[2] = 100
				cnt = 1
			else:
				pixel2[0] = 255
				pixel2[1] = 255
				pixel2[2] = 255
				if cnt == 1:
					count = count + 1
					cnt = 0
		vrc[i] = count
		i+=1
	i = 0
	ws = we = 0
	vs = ve = 0

	for j in range(w):
		if wid[j] != 0:
			ws = j
			break
	for j in range(w-1,-1,-1):
		if wid[j] != 0:
			we = j
			break
	for j in range(v):
		if vrc[j] != 0:
			vs = j
			break
	for j in range(v-1,-1,-1):
		if vrc[j] != 0:
			ve = j
			break
	cv2.destroyAllWindows()
	if wid[ws] == 3 or wid[ws+1]:
		return('W')
	elif wid[ws] == 2:
		return('N')
	elif wid[ws] == 1:
		if vrc[ve] == 3:
			return('E')
		elif vrc[ve] == 2:
			return('S')
			
def newsWC():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, FPS)
	
	x0 = 0
	x1 = 320
	y0 = 90
	y1 = 220
	w = int((y1-y0)/5) #48
	v = int((x1-x0)/10)#32
	
	vrc = [0]*v #tpfh (380 - 265)/10
	wid = [0]*w #rkfh (340 - 180)/5
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	check_box = frame[y0:y1, x0:x1].copy()
	cv2.rectangle(frame,(x0,y0),(x1,y1),(0,255,0),2,cv2.LINE_4,0)

	hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	count = 0 #black line count

	for y in range(0, y1-y0, 5):    
		count = 0
		for x in range(0,x1-x0):
			pixel = hsv[y,x]
			V_value = pixel[2]
			if V_value < 40:
				pixel[0] = 100
				pixel[1] = 100
				pixel[2] = 100
				cnt = 1
			else:
				pixel[0] = 255
				pixel[1] = 255
				pixel[2] = 255
				if cnt == 1:
					count = count + 1
					cnt = 0
		wid[i] = count
		i+=1
	i = 0
	cnt = 0
	count = 0
	for x in range(0,x1-x0,10):
		count = 0
		for y in range(0,y1-y0):
			pixel2 = hsv2[y,x]
			V_value = pixel2[2]
			
			if V_value < 40:
				pixel2[0] = 100 
				pixel2[1] = 100
				pixel2[2] = 100
				cnt = 1
			else:
				pixel2[0] = 255
				pixel2[1] = 255
				pixel2[2] = 255
				if cnt == 1:
					count = count + 1
					cnt = 0
		vrc[i] = count
		i+=1
	i = 0
	ws = we = 0
	vs = ve = 0

	for j in range(w):
		if wid[j] != 0:
			ws = j
			break
	for j in range(w-1,-1,-1):
		if wid[j] != 0:
			we = j
			break
	for j in range(v):
		if vrc[j] != 0:
			vs = j
			break
	for j in range(v-1,-1,-1):
		if vrc[j] != 0:
			ve = j
			break
	cv2.destroyAllWindows()
	if wid[ws] == 3 or wid[ws+1] == 3:
		print('W')
	elif wid[ws] == 2:
		print('N')
	elif wid[ws] == 1:
		if vrc[ve] == 3:
			print('E')
		elif vrc[ve] == 2:
			print('S')
	print(vrc[ve])
	nparr = np.array([100,100,100])
	hsv_mask = cv2.inRange(hsv, nparr, nparr)  
	hsv = cv2.bitwise_and(hsv, hsv, mask = hsv_mask) #black line extract
	hsv_mask = cv2.inRange(hsv2, nparr, nparr)  
	hsv2 = cv2.bitwise_and(hsv2, hsv2, mask = hsv_mask)
	while(True):
		merged = np.hstack((hsv,hsv2))
		cv2.imshow('result0', merged)
		cv2.imshow('result', check_box)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	return frame
			
def abcd():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 

	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 240
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	vrc = [0]*v #tpfh
	wid = [0]*w #rkfh
	lth = [0]*v #rlfdl
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	count = 0 #black line count

	for y in range(0, y1-y0, 5):    
		count = 0
		for x in range(0,x1-x0):
		    pixel = hsv[y,x]
		    H_value = pixel[0]
		    S_value = pixel[1]
		    V_value = pixel[2]
		    
		    if S_value > 120:
			    pixel[0] = 100
			    pixel[1] = 100
			    pixel[2] = 100
			    cnt = 1
		    else:
			    pixel[0] = 255
			    pixel[1] = 255
			    pixel[2] = 255
			    if cnt == 1:
				    count = count + 1
				    cnt = 0
		wid[i] = count
		i+=1
	i = 0
	cnt = 0
	count = 0
	for x in range(0,x1-x0,10):
		count = 0
		for y in range(0,y1-y0):
		    pixel2 = hsv2[y,x]
		    H_value = pixel2[0]
		    S_value = pixel2[1]
		    V_value = pixel2[2]
		    
		    if S_value > 120:
			    pixel2[0] = 100
			    pixel2[1] = 100
			    pixel2[2] = 100
			    cnt += 1
		    else:
			    pixel2[0] = 255
			    pixel2[1] = 255
			    pixel2[2] = 255
			    if cnt >= 1:
				    count = count + 1
				    lth[i] = cnt
				    cnt = 0
		vrc[i] = count
		i+=1
	i = 0
	mlth = -1
	ws = vs = we = ve = -1
	for j in range(w):
		if wid[j] != 0:
			ws = j
			break
	for j in range(v):
		if vrc[j] != 0:
			vs = j
			break
	for j in range(w-1,-1,-1):
		if wid[j] != 0:
			we = j
			break
	for j in range(v-1,-1,-1):
		if vrc[j] != 0:
			ve = j
			break
	cv2.destroyAllWindows()
	if vrc[int((vs+ve)/2)] == 3:
		return('B')
	elif vrc[ve] == 2 or vrc[ve-1] == 2:
		return('C')
	elif wid[we] == 2:
		return('A')
	elif wid[we] == 1:
		return('D')
		
def abcdWC():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 
	
	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 240
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	vrc = [0]*v #tpfh
	wid = [0]*w #rkfh
	lth = [0]*v #rlfdl
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	hsv2 = hsv.copy()

	cnt = 0 #cnt=1 => black line start
	count = 0 #black line count

	for y in range(0, y1-y0, 5):    
		count = 0
		for x in range(0,x1-x0):
		    pixel = hsv[y,x]
		    H_value = pixel[0]
		    S_value = pixel[1]
		    V_value = pixel[2]
		    
		    if S_value > 120:
			    pixel[0] = 100
			    pixel[1] = 100
			    pixel[2] = 100
			    cnt = 1
		    else:
			    pixel[0] = 255
			    pixel[1] = 255
			    pixel[2] = 255
			    if cnt == 1:
				    count = count + 1
				    cnt = 0
		wid[i] = count
		i+=1
	i = 0
	cnt = 0
	count = 0
	for x in range(0,x1-x0,10):
		count = 0
		for y in range(0,y1-y0):
		    pixel2 = hsv2[y,x]
		    H_value = pixel2[0]
		    S_value = pixel2[1]
		    V_value = pixel2[2]
		    
		    if S_value > 120:
			    pixel2[0] = 100
			    pixel2[1] = 100
			    pixel2[2] = 100
			    cnt += 1
		    else:
			    pixel2[0] = 255
			    pixel2[1] = 255
			    pixel2[2] = 255
			    if cnt >= 1:
				    count = count + 1
				    lth[i] = cnt
				    cnt = 0
		vrc[i] = count
		i+=1
	i = 0
	mlth = -1
	ws = vs = we = ve = -1
	for j in range(w):
		if wid[j] != 0:
			ws = j
			break
	for j in range(v):
		if vrc[j] != 0:
			vs = j
			break
	for j in range(w-1,-1,-1):
		if wid[j] != 0:
			we = j
			break
	for j in range(v-1,-1,-1):
		if vrc[j] != 0:
			ve = j
			break
	cv2.destroyAllWindows()
	if vrc[int((vs+ve)/2)] == 3:
		print('B')
	elif vrc[ve] == 2 or vrc[ve-1] == 2:
		print('C')
	elif wid[we] == 2:
		print('A')
	elif wid[we] == 1:
		print('D')
	nparr = np.array([100,100,100])
	hsv_mask = cv2.inRange(hsv, nparr, nparr)  
	hsv = cv2.bitwise_and(hsv, hsv, mask = hsv_mask) #black line extract
	hsv_mask = cv2.inRange(hsv2, nparr, nparr)  
	hsv2 = cv2.bitwise_and(hsv2, hsv2, mask = hsv_mask)
	while(True):
		merged = np.hstack((hsv,hsv2))
		cv2.imshow('result0', merged)
		cv2.imshow('result', frame)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	return frame
	
def mission():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 
	
	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 240
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	vrc = [0]*v #tpfh
	wid = [0]*w #rkfh
	lth = [0]*v #rlfdl
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	cap.release()
	pixel = hsv[y0,x0]
	if pixel[1] < 30:
		return 'dan'
	pixel = hsv[y0,x1-1]
	if pixel[1] < 30:
		return 'dan'
	pixel = hsv[y1-1,x0]
	if pixel[1] < 30:
		return 'dan'
	pixel = hsv[y1-1,x1-1]
	if pixel[1] < 30:
		return 'dan'
	else:
		return 'stair'

def color_black():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 
	
	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 200
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	vrc = [0]*v #tpfh
	wid = [0]*w #rkfh
	lth = [0]*v #rlfdl
	i = 0
	qwe = 1

	_,frame = cap.read()
	height, width, _ = frame.shape

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	pixel = hsv[y1,int(x1/2)]
	if pixel[1] < 30:
		return True
	else:
		return False

def color_green():
	cap = cv2.VideoCapture(0)
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, 90) 

	k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size-60 #226
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)
	
	cnt = 0
	clr = [0]*2
	qwe = 1
	for i in range(2):
		_,frame = cap.read()
		height, width, _ = frame.shape
			
		check_box = frame[y0:y1, x0:x1].copy() 
			
		hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
		hsv_Lower = np.array([45, 100, 140])
		hsv_Upper = np.array([60, 160, 255])
			
		mask = cv2.inRange(hsv, hsv_Lower, hsv_Upper)
			
		cnt = 0 #cnt=1 => black line start
		count = 0 #black line count
		for y in range(y1):
			pixel = mask[y,x0+1]
			if pixel == 255:
				cnt+=1
		
		clr[0] = cnt
		cnt = 0
				#break
			
		for y in range(y1):
			pixel = mask[y,x1-1]
			if pixel == 255:
				cnt+=1
		
		clr[1] = cnt
				#break
				
	cv2.destroyAllWindows()
	return clr
	
def color_blue():
	cap = cv2.VideoCapture(0)
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, 90) 

	k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size-60 #226
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	clr = [0]*2
	qwe = 1
	for i in range(2):
		_,frame = cap.read()
		height, width, _ = frame.shape
			
		check_box = frame[y0:y1, x0:x1].copy() 
			
		hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
		hsv_Lower = np.array([45, 100, 170])
		hsv_Upper = np.array([255, 255, 255])
			
		mask = cv2.inRange(hsv, hsv_Lower, hsv_Upper)
			
		cnt = 0 #cnt=1 => black line start
		count = 0 #black line count
		for y in range(y1):
			pixel = mask[y,x0+1]
			if pixel == 255:
				cnt+=1
		
		clr[0] = cnt
		cnt = 0
				#break
			
		for y in range(y1):
			pixel = mask[y,x1-1]
			if pixel == 255:
				cnt+=1
		
		clr[1] = cnt
	cv2.destroyAllWindows()
	return clr
	
def color_red():
	cap = cv2.VideoCapture(0)
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, 90) 

	k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	x0 = 0
	x1 = W_View_size
	y0 = 0
	y1 = H_View_size-60 #226
	w = int((y1-y0)/5)
	v = int((x1-x0)/10)

	clr = [0]*2
	qwe = 1
	for i in range(2):
		_,frame = cap.read()
		height, width, _ = frame.shape
			
		check_box = frame[y0:y1, x0:x1].copy() 
			
		hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
		hsv_Lower = np.array([160, 110, 70])
		hsv_Upper = np.array([255, 255, 255])
			
		mask = cv2.inRange(hsv, hsv_Lower, hsv_Upper)
			
		cnt = 0 #cnt=1 => black line start
		count = 0 #black line count
		for y in range(y1):
			pixel = mask[y,x0+1]
			if pixel == 255:
				cnt+=1
		
		clr[0] = cnt
		cnt = 0
				#break
			
		for y in range(y1):
			pixel = mask[y,x1-1]
			if pixel == 255:
				cnt+=1
		
		clr[1] = cnt
				
	cv2.destroyAllWindows()
	return clr
def dir():
	W_View_size = 320
	H_View_size = int(W_View_size / 1.333)
	FPS         = 90  #PI CAMERA: 320 x 240 = MAX 90

	cap = cv2.VideoCapture(0)
	cap.set(3, W_View_size)
	cap.set(4, H_View_size)
	cap.set(5, FPS)
	_,frame = cap.read()
	return frame
	
def dangerous():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 

	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 240
	area = 0
	_,frame = cap.read()
	height, width, _ = frame.shape
	check_box = frame[y0:y1, x0:x1].copy()

	hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
	hsv_Lower = np.array([100, 75,65])
	hsv_Upper = np.array([255, 255, 255])
	mask = cv2.inRange(hsv, hsv_Lower, hsv_Upper)
	contour, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	middle = [160, 200]
	if contour:
		for i in contour:
			x_,y_,w_,h_ = cv2.boundingRect(i)
			if area < w_*h_:
				area = w_*h_
				x = x_
				y = y_
				w = w_
				h = h_
		middle[0] = (x+x+w)/2
		middle[1] = (y+y+h)/2 
	return middle
def dangerousWC():
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 

	x0 = 0
	x1 = 320
	y0 = 0
	y1 = 240
	area = 0
	_,frame = cap.read()
	height, width, _ = frame.shape
	check_box = frame[y0:y1, x0:x1].copy()

	hsv = cv2.cvtColor(check_box, cv2.COLOR_BGR2HSV)
	hsv_Lower = np.array([100, 75,65])
	hsv_Upper = np.array([255, 255, 255])
	mask = cv2.inRange(hsv, hsv_Lower, hsv_Upper)
	contour, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for i in contour:
		x_,y_,w_,h_ = cv2.boundingRect(i)
		if area < w_*h_:
			area = w_*h_
			x = x_
			y = y_
			w = w_
			h = h_
	print((x+x+w)/2,(y+y+h)/2)
	while True:
		img = cv2.line(check_box, (int((x+x+w)/2), int((y+y+h)/2) ),(int((x+x+w)/2), int((y+y+h)/2) ), (0,255,0),5)
		cv2.rectangle(check_box, (x,y), (x+w, y+h), (0,0,0), 3)
		cv2.imshow('contour', check_box)
		cv2.imshow('contr', mask)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	cv2.destroyAllWindows()
	
def capimg(x0 = 0, x1 = 320, y0 = 0, y1 = 240, name = 'cap'):
	cap = cv2.VideoCapture(0)

	cap.set(3, 320)
	cap.set(4, 240)
	cap.set(5, 90) 

	_,frame = cap.read()
	height, width, _ = frame.shape
	check_box = frame[y0:y1, x0:x1].copy()
	cv2.imwrite(f'cap/{name}.jpg', check_box)
