#!/usr/bin/python
import cv2
from math import atan2,degrees
import numpy as np
import rospy
from geometry_msgs.msg import Twist

def nothing(x):
    pass

rospy.init_node('hander')

pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
msg = Twist()

cap=cv2.VideoCapture(0)

cv2.namedWindow('HSV_TrackBar')
cv2.createTrackbar('h', 'HSV_TrackBar',24,255,nothing)

while(cap.isOpened()):
	_,feed=cap.read()
	image=feed[0:480,0:640]
	image=cv2.flip(image,1)
	img=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	blur=cv2.GaussianBlur(img,(35,35),0)
	h=cv2.getTrackbarPos('h','HSV_TrackBar')
	ret,thresh = cv2.threshold(blur,h,255,cv2.THRESH_BINARY_INV)
	_,contours,hierarchy = cv2.findContours(thresh,1,1)
	max_area=0
	pos=0
	for i in contours:
		area=cv2.contourArea(i)
		if area>max_area:
			max_area=area
			pos=i

	try:
	    cnt = contours[0]
	    M = cv2.moments(cnt)
	    rect=cv2.minAreaRect(cnt)
	    box=cv2.boxPoints(rect)
	    box=np.int0(box)
	    x1=(box[2,0]+box[1,0])/2.0
	    y1=box[1,1]
	    x2=(box[3,0]+box[0,0])/2.0
	    y2=box[0,1]
	    ang=degrees(atan2(y2-y1,x2-x1))
	except:
	    print('OpenCV Error')
	    continue
	
	cv2.drawContours(thresh,[box],-1,(255,255,255),2)
	
	try:
	    cx = int(M['m10']/M['m00'])
	    cy = int(M['m01']/M['m00'])
	    cv2.circle(thresh,(cx,cy),5,(0,255,0),-1)
	except ZeroDivisionError:
	    print('Error')
	    continue
	  
	s='Hello'
	g,v = 1,1
	if abs(cx-320)>150:
		g=(abs(cx-320)/100.0)
	if abs(cy-240)>130:
		v=(abs(cy-240)/80.0)
	
	if 15<ang<40:
		msg.angular.z = -1;
	elif 50<ang<75:
		msg.angular.z = 1;
	else:
		msg.angular.z = 0;
	
	if (cx<220 and cy<110) or (cx<170 and 110<cy<160):
		s='Forward&Left'
		msg.linear.x = 0.1*v;
		msg.linear.y = 0.1*g;
	elif (cx<220 and cy>370) or (cx<170 and 320<cy<370):
		s='Back&Left'
		msg.linear.x = -0.1*v;
		msg.linear.y = 0.1*g;
	elif (cx>420 and cy<110) or (cx>470 and 110<cy<160):
		s='Forward&Right'
		msg.linear.x = 0.1*v;
		msg.linear.y = -0.1*g;
	elif (cx>420 and cy>370) or (cx>470 and 320<cy<370):
		s='Back&Right'
		msg.linear.x = -0.1*v;
		msg.linear.y = -0.1*g;
	elif 220<cx<420 and cy<110:
		s='Forward'
		msg.linear.x = 0.1*v;
		msg.linear.y = 0;
	elif 220<cx<420 and cy>370:
		s='Back'
		msg.linear.x = -0.1*v;
		msg.linear.y = 0;
	elif cx<170 and 160<cy<320:
		s='Left'
		msg.linear.x = 0;
		msg.linear.y = 0.1*g;
	elif cx>470 and 160<cy<320:
		s='Right'
		msg.linear.x = 0;
		msg.linear.y = -0.1*g;
	else:
		s='Stop'
		msg.linear.x = 0;
		msg.linear.y = 0;

	pub.publish(msg)
	
	cv2.rectangle(thresh,(170,110),(470,370),(255,255,255),3)

	cv2.line(thresh,(220,0),(220,110),(255,255,255),3)
	cv2.line(thresh,(420,0),(420,110),(255,255,255),3)
	cv2.line(thresh,(0,160),(170,160),(255,255,255),3)
	cv2.line(thresh,(0,320),(170,320),(255,255,255),3)

	cv2.line(thresh,(220,370),(220,480),(255,255,255),3)
	cv2.line(thresh,(420,370),(420,480),(255,255,255),3)
	cv2.line(thresh,(470,160),(640,160),(255,255,255),3)
	cv2.line(thresh,(470,320),(640,320),(255,255,255),3)

	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.putText(thresh,s,(100,100), font, 2,(255,255,10),2,cv2.LINE_AA)

	cv2.imshow('Feed',image)
	cv2.imshow('image',thresh)
	k=cv2.waitKey(10)
	if k==27:
		break
cv2.destroyAllWindows()
