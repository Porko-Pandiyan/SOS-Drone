# To use Inference Engine backend, specify location of plugins:
# export LD_LIBRARY_PATH=/opt/intel/deeplearning_deploymenttoolkit/deployment_tools/external/mklml_lnx/lib:$LD_LIBRARY_PATH
# usr/bin/bash -tt
import cv2 as cv
import numpy as np
import argparse
import math  
import collections

global stack_l
global stack_r
stack_l = collections.deque(maxlen=1)
stack_r = collections.deque(maxlen=1)
print("XOXOX")
stack_r.append((0,0,0))
stack_l.append((0,0,0))
def calculateDistance(x1,y1,x2,y2):  
	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
	return dist  
	# print calculateDistance(x1, y1, x2, y2)  

def intersecting(x1,y1,r1,x2,y2,r2):
	d = calculateDistance(x1,y1,x2,y2)
	assert(x1 >= 0)
	assert(y1 >= 0)
	assert(r1 >= 0)
	assert(x2 >= 0)
	assert(y2 >= 0)
	assert(r2 >= 0)
	if (d <= (r1 +r2)):
		a = r1**2
		b = r2**2
		x = ((a - b) + d**2) / (2 * d)
		z = x**2
		
		if (d < abs(r2 - r1)):
			return (math.pi * min(a, b))

		y = math.sqrt(a - z)
		
		return (a * math.asin(y / r1) + b * math.asin(y / r2) - y * (x + math.sqrt(z + b - a)))
	
	return 0

def Extract_hands(stack_l,stack_r,no,no_l,no_r,area_img,iou_thr,frame,buffer_fps = 7):
	print("YOYOYOY")
	global c11,c21,radius1,c12,c22,radius2
	if((no - no_r )%buffer_fps == 0):
		stack_r.append((0,0,0))

	if((no - no_l )%buffer_fps == 0):
		stack_l.append((0,0,0))
	# print(stack_l)
	# no_p = 0
	print(no)
	print(no_l)
	if(len(stack_l)==1):
		(c11,c21,radius1) = stack_l.pop()
	# stack_l.append((0,0,0))
	print(no_r)
	# print(stack_r)
	if(len(stack_r)==1):
		(c12,c22,radius2) = stack_r.pop()
	# stack_r.append((0,0,0))
	print("LLLLLLLLLLOOOOOOOOOOOOLLLLLLLLL")
	print(radius1,radius2)
	if ( radius1 and radius2 ):
			
		print("XXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxXXXXXXXXxxxxxxxxxx")
		intersecting_area = intersecting(c11,c21,radius1,c21,c22,radius2)
		
		total_area = math.pi*(radius2**2 + radius1**2)
		# iou_normalized = (iuo_area/(math.pi*radius*radius))*area_img
		print("VVVVVVVVVVVVVVVVVVvvvvvvvvvvvvvvvvvvvvVVVVVVVVVVVVVv")
		# print(np_p)
		iou = intersecting_area/total_area
		iou_normalized = iou/area_img
		print("iou==========>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",iou)
		print("iou_norm===================================================>>>>>>>",iou_normalized)
		flag = False
		if ((iou_normalized > iou_thr) and (y1 >= (y11 - (radius1+radius2)/2))):
			flag = True

		if(flag):
			cv.putText(frame,"Rescuse Detected",(300, 20), cv.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255))
			flag = False
		else:
			cv.putText(frame,"Searching for CHix",(100, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

	

	return stack_l,stack_r

def hello():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', help='Path to image or video. Skip to capture frames from camera')
	parser.add_argument('--thr', default=0.1, type=float, help='Threshold value for pose parts heat map')
	parser.add_argument('--width', default=368, type=int, help='Resize input to specific width.')
	parser.add_argument('--height', default=368, type=int, help='Resize input to specific height.')
	parser.add_argument('--iou_thr', default=0.1, type=float, help='Threshold value of IOU')

	args = parser.parse_args()

	BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
				   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
				   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
				   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

	POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
				   ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
				   ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
				   ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
				   ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

	inWidth = args.width
	inHeight = args.height
	iou_thr = args.iou_thr
	flag = False

	net = cv.dnn.readNetFromTensorflow("openpose_mobile_opt.pb")

	cap = cv.VideoCapture(args.input if args.input else 0)

	stack_r = collections.deque(maxlen=1)
	stack_l = collections.deque(maxlen=1)
	print("XOXOX")
	stack_r.append((0,0,0))
	stack_l.append((0,0,0))

	no_r = 0
	no_l = 0
	no = 0


	while cv.waitKey(1) < 0:
		hasFrame, frame = cap.read()
		if not hasFrame:
			cv.waitKey()
			break

		frameWidth = frame.shape[1]
		frameHeight = frame.shape[0]

		# img1 = np.zeros((frameWidth,frameHeight))
		# img2 = np.zeros((frameWidth,frameHeight))
		
		net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
		out = net.forward()
		out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

		assert(len(BODY_PARTS) == out.shape[1])


		points = []
		for i in range(len(BODY_PARTS)):
			# Slice heatmap of corresponging body's part.
			heatMap = out[0, i, :, :]

			# Originally, we try to find all the local maximums. To simplify a sample
			# we just find a global one. However only a single pose at the same time
			# could be detected this way.
			_, conf, _, point = cv.minMaxLoc(heatMap)
			x = (frameWidth * point[0]) / out.shape[3]
			y = (frameHeight * point[1]) / out.shape[2]
			# Add a point if it's confidence is higher than threshold.
			points.append((int(x), int(y)) if conf > args.thr else None)

		for pair in POSE_PAIRS:
			flag1 = False
			flag2 = False
			partFrom = pair[0]
			partTo = pair[1]
			assert(partFrom in BODY_PARTS)
			assert(partTo in BODY_PARTS)
			idFrom = BODY_PARTS[partFrom]
			idTo = BODY_PARTS[partTo]

			if points[idFrom] and points[idTo]:
				print("GENERALLLL")
				cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
				no = no + 1
				cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
				cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
				area_img = frameWidth * frameHeight
				# stack_l,stack_r = Extract_hands(stack_l,stack_r,no,no_l,no_r)
				# print(" pose")
				if ((((idFrom == 3) and (idTo == 4)) or ((idFrom == 4) and (idTo == 3)))): #or (((idFrom == 6) and (idTo == 7)) or ((idFrom == 7) and (idTo == 6)))):
					print("detecting left hand")
					x1,y1 = points[3]
					x2,y2 = points[4]
					z11,z21 = (math.floor((x1+x2)/2),math.floor((y1+y2)/2))
					radius1 = math.floor(calculateDistance(x1,y1,x2,y2))
					p1 = (z11,z21,radius1)
					stack_l.append(p1)
					cv.circle(frame,(z11,z21),radius1,(0,0,100),-1)
					# cv.circle(img1,centre,radius,(255,255,255),-1)  
					no_l = no_l + 1
					# cv.imshow('YSSSSSSS using OpenCV', img1)
					print("stack left")
					print(stack_l)
					print(flag1)
				if  ((idFrom == 6) and (idTo == 7)) or ((idFrom == 7) and (idTo == 6)):
					print("detecting right hand ")
					x3,y3 = points[6]
					x4,y4 = points[7]
					z12,z22 = (math.floor((x3+x4)/2),math.floor((y3+y4)/2))
					radius2 = math.floor(calculateDistance(x4,y4,x3,y3))
					p2 = (z12,z22,radius2)
					stack_r.append(p2)
					cv.circle(frame,(z12,z22),radius2,(0,0,100),-1)
					# cv.circle(img2,centre,radius,(255,255,255),-1)
					no_r = no_r + 1
					# print(str(flag2)+" ok")
					# cv.imshow('ZZZZZ using OpenCV', img2)
					print("stack right")
					print(stack_r)
				if ((((idFrom == 3) and (idTo == 4)) or ((idFrom == 4) and (idTo == 3)))) or (((idFrom == 6) and (idTo == 7)) or ((idFrom == 7) and (idTo == 6))):
					print("ZZZZZZZZZZZZZZzzzzzzzzzzzzZZZZZZZZZZZZZ")
					stack_l,stack_r = Extract_hands(stack_l,stack_r,no,no_l,no_r,area_img,iou_thr,frame)
			
			# if (points[idFrom] and points[idTo]):
				# print("GENERALLLL")
				# cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
				# no = no + 1
				# cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
				# cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
				# stack_l,stack_r = Extract_hands(stack_l,stack_r,no,no_l,no_r)

			# stack_l,stack_r = Extract_hands(stack_l,stack_r,no,no_l,no_r)


		t, _ = net.getPerfProfile()
		freq = cv.getTickFrequency() / 1000
		cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

		cv.imshow('OpenPose using OpenCV', frame)

if __name__ == '__main__':
	hello()
