import threading
import cv2
import pyttsx3
import speech_recognition as sr

from roomscan import yolo
from detect_obstacles import detect_obstacle

engine = pyttsx3.init()
engine.setProperty("rate", 130)
LANGUAGE = 'en'

r = sr.Recognizer()

cap = cv2.VideoCapture(0)


def mic_run():
    keyWord = 'scan'
    with sr.Microphone() as source:
        # print('Please start speaking..\n')
        while True:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                if keyWord.lower() in text.lower():
                    _ret, frame = cap.read()
                    print("Scanning Room...")
                    yolo(frame)
            except Exception as e:
                print('exception occured')


def cam_run():

    frame_count = 0
    qr_detect_flag = 0
    flag_frame_count = 0
    while(True):
        # Capture frame-by-frame
        _ret, frame = cap.read()
        if(frame is None):
            break
        qrCodeDetector = cv2.QRCodeDetector()
        decodedText, points, _ = qrCodeDetector.detectAndDecode(frame)
        if(decodedText is not ''):
            nrOfPoints = len(points[0])
            points = points.astype(int)
            for i in range(nrOfPoints):
                nextPointIndex = (i+1) % nrOfPoints
                cv2.line(frame, tuple(points[0][i]), tuple(
                    points[0][nextPointIndex]), (255, 0, 0), 20)

            frame = cv2.putText(frame, 'QR Detected', (int(points[0][0][0]), int(
                points[0][0][1]-20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 4, cv2.LINE_AA)

            if qr_detect_flag != 1:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.resize(frame, (360, 640))
                cv2.imshow('Frame', frame)
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                print(decodedText)
                engine.say(decodedText)
                engine.runAndWait()
                qr_detect_flag = 1

        if frame_count % 50 == 0 and qr_detect_flag != 1:
            edges, mask, ratio = detect_obstacle(frame)
            # print(ratio)
            if(ratio > 0.55):  # r_thresh_not decided
                print('Obstacle Detected')
                engine.say('Obstacle has been detected!')
                engine.runAndWait()
            else:
                print('No obstacle detected')

            mask = cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE)
            mask = cv2.resize(mask, (360, 640))
            cv2.imshow('Contours', mask)

        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.resize(frame, (360, 640))
        cv2.imshow('Frame', frame)

        frame_count += 1
        if qr_detect_flag:
            flag_frame_count += 1

        if flag_frame_count >= 100:
            flag_frame_count = 0
            qr_detect_flag = 0

        if cv2.waitKey(1) & 0xFF == ord('y'):
            print("Scanning the Room")
            yolo(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


thread1 = threading.Thread(target=mic_run)
thread2 = threading.Thread(target=cam_run)

thread1.start()
thread2.start()
