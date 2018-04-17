import cv2

cap = cv2.VideoCapture("rtsp://192.168.1.199/Streaming/Channels/102")
while(True):
	ret, frame = cap.read()
	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF==ord('q'):
		break
cap.release()
cv2.destroyAllWindows()
