# import the opencv library
import cv2
import numpy as np

#finds the most dense contour and only labels that one
#clearity and seperating/combining these groups is the main issue to fix


#////////////////////////////////////////
def clr_iso(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # BLUE / GREEN / RED

    #orange
    #lower = np.array([0, 90, 90])
    #upper = np.array([30, 255, 255])

    #blue
    lower = np.array([101, 50, 38])
    upper = np.array([110, 255, 255])



    mask = cv2.inRange(hsv,lower,upper)
    return mask

#////////////////////////////////////////
# START



# define a video capture object
vid = cv2.VideoCapture(0)


#////////////////////////////////////////
#LOOP



while (True):

    # Capture the video frame by frame

    ret, frame = vid.read()
    mask = clr_iso(frame)

    #obj detection
    _, mask = cv2.threshold(mask, 254,255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    tobeat = 0.0
    #first run to find the highest percentile of area
    for cnt in contours:

        #print(tobeat)

        #calc area and remove small elments
        area = round(cv2.contourArea(cnt))

        if (area > 1000):
            cv2.drawContours(frame, [cnt], -1, (255, 165, 0), 2)
            x, y, w, h = cv2.boundingRect(cnt)

            perc = area/(w*h)

            #CHANGE THIS VALUE IF FAR/CLOSE
            if ( perc > tobeat ):

                #print(area,", ",perc,)

                tobeat = perc
                fx=x
                fy=y
                fw=w
                fh=h
        #print(tobeat)

    cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (255, 0, 0), 3)


    xystr = str(fx) + ", " + str(fy)
    cv2.putText(frame, xystr, (fx, fy - 5), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

    avgx = round(fx + (fw / 2))
    avgy = round(fy + (fh / 2))
    # print(avgx, avgy)
    cv2.putText(frame, str(avgx) + ", " + str(avgy), (avgx, avgy - 7), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

    cv2.putText(frame, "x", (avgx, avgy), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    print(fx,fy)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)

    # quits when pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#////////////////////////////////////////
# clean up after loop
vid.release()
cv2.destroyAllWindows()