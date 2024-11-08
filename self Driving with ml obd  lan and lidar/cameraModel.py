import cv2
from picamera2 import Picamera2
'''
This class is used to capture video frames using the PiCamera and share them with the main program.
'''
class Kamera:
    def __init__(self):
        ''' 
        Initialize the Kamera class with the following attributes:
        - picam2: The PiCamera object.
        - config: The configuration of the PiCamera.
        - size: The size of the frame.
        - encode: The encoding of the frame.
        - lores: The low resolution of the frame.
        - main: The main resolution of the frame.
        - start: The start of the PiCamera.
        '''
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(main={"size": (2048, 1536)}, lores={"size": (720, 480)}, encode="lores")
        self.picam2.configure(config)
        self.picam2.start()

    def getVideo(self,display=False,size=[480,240]):
        '''
         To capture a video frame, 
         1_use the capture_array() function from the picam2 library to obtain the frame
         2_initially in RGB format. 
         3_Convert this frame to OpenCV’s BGR format for compatibility using the OpenCV library. 
         Once converted, adjust the frame size as needed to ensure compatibility with subsequent functions 
         4_add the capability to display the frame as desired.
        '''
        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        img=cv2.resize(frame,(480,240))
        if display:
            cv2.imshow('Frame', img)
            cv2.waitKey(1)
        return img

if __name__ == "__main__":
    pass
 