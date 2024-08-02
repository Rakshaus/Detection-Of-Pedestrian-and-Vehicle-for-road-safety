import cv2
import smtplib,ssl
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
f=filename.split("/")
f1=f[len(f)-1]
f2=f1.split(".")
location=f2[0]

# our video file
video = cv2.VideoCapture(filename)

# our pre-trained car and  pedestrian classifiers
car_tracker_file = 'car_detector.xml'
pedestrian_tracker_file = 'haarcascade_fullbody.xml'

# create car and pedestrian classifiers
car_tacker = cv2.CascadeClassifier(car_tracker_file)
pedestrian_tacker = cv2.CascadeClassifier(pedestrian_tracker_file)

# run until the car stops
cnt=0
while True:
    # read the current frame
    (read_successful, frame) = video.read()

    if read_successful:
        # if read successfully converted to grayscale
        grayscaled_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        break

    # detect cars AND pedestrians
    cars = car_tacker.detectMultiScale(grayscaled_frame)
    pedestrians = pedestrian_tacker.detectMultiScale(grayscaled_frame)
    # print(cars)

    # draw rectangle around the cars in red color
    for (x, y, w, h) in cars:
        cv2.rectangle(frame, (x + 1, y + 2), (x + w, y + h), (255, 0, 0), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, "Car",(x+15,y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        #print('car detected')

    # draw rectangle around the pedestrians in yellow color
    for (x, y, w, h) in pedestrians:
        cv2.putText(frame, "Alert-Chance of Accident",(x,y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(frame, "Pedestrian",(x+15,y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        #print('pedestrian detected Alert Chance of accident')
        cnt+=1
        if cnt >20:
            import pymongo
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            mydb = myclient["accident"]
            mycol = mydb["a"]

            myquery = { "location": location }

            mydoc = mycol.find(myquery)

            email=""
            for x in mydoc:
               email=x["email"]
            print(email)
            
            smtp_server = "smtp.gmail.com"
            port = 465  # For starttls
            sender_email = "traffic_project@jnnce.ac.in"
            password = "Pedestrian123"
            receiver_email=email
            print('Traffic police informed....')
            messagebox.showerror("showerror", "Alert of Accident zone")
            cnt=0
            message = """\
                Subject: Alert of Accident zone

                    Too much fast traffic kindly control with suitable traffic policing.."""

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
            
    # display the image (frame) with the faces spotted
    cv2.imshow("Cars and Pedestrians Detector", frame)

    # don't auto close, wait for the any key to press
    key = cv2.waitKey(2)

    # if that key = q or Q, so then close the video
    if key == 81 or key == 113:
        break

# Release the VideoCapture object
video.release()

print("Done!")
