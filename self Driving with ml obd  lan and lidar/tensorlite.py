import argparse
import sys
import time
import asyncio

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from cameraModel import Kamera
from utilsRect import visualize
import json 
class ObjectDetection:
    def __init__(self,img,model: str, max_results: int, score_threshold: float, 
                  width: int, height: int) -> None:
        """Initialize the object detection class.

        Args:
            model: Name of the TFLite object detection model.
            max_results: Max number of detection results.
            score_threshold: The score threshold of detection results.
            camera_id: The camera id to be passed to OpenCV.
            width: The width of the frame captured from the camera.
            height: The height of the frame captured from the camera.
        """
        self.model = model
        self.max_results = max_results
        self.score_threshold = score_threshold
        #self.camera_id = camera_id
        self.width = width
        self.height = height
        self.camera=img
        
        # Global variables to calculate FPS
        self.COUNTER, self.FPS = 0, 0
        self.START_TIME = time.time()

        # Visualization parameters
        self.row_size = 50  # pixels
        self.left_margin = 24  # pixels
        self.text_color = (0, 0, 0)  # black
        self.font_size = 1
        self.font_thickness = 1
        self.fps_avg_frame_count = 10
        self.detection_frame = None
        self.detection_result_list = []
        
        # Dictionary that contains all detected information with the highest probability
        self.detected_object_info = {"category_name": None, "probability": 0}
    
    def setCamera(self,camera):
        self.camera=camera
    def save_result(self, result: vision.ObjectDetectorResult, unused_output_image: mp.Image, timestamp_ms: int):
        """Callback function to save the detection result."""
        # Calculate the FPS
        if self.COUNTER % self.fps_avg_frame_count == 0:
            self.FPS = self.fps_avg_frame_count / (time.time() - self.START_TIME)
            self.START_TIME = time.time()

        self.detection_result_list.append(result)
        self.COUNTER += 1

    def get_detected_object_info(self):
       
        """Returns the detected object information as a printable string."""
        category_name = self.detected_object_info["category_name"]
        probability = self.detected_object_info["probability"]
        with open('data/detected_object_info.json', 'w') as f:
            if category_name is not None:
                json.dump({"Detected Object": category_name, "Probability": probability},f,indent=4)
            else:
                json.dump({"Detected Object": None, "Probability": 0},f,indent=4)
    async def capture_frames(self, display=0,cap=None):
        """Capture frames from the camera and run object detection."""
        cap = self.camera.getVideo()
        frame_skip = 2  # Process every other frame
        frame_count = 0
        
        # Initialize the object detection model without delegate
        base_options = python.BaseOptions(model_asset_path=self.model)
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            max_results=self.max_results,
            score_threshold=self.score_threshold,
            result_callback=self.save_result
        )
        detector = vision.ObjectDetector.create_from_options(options)
        temp={"category_name":None,"probability":0}
        
        while True:
            image = self.camera.getVideo()
            frame_count += 1

            if frame_count % frame_skip != 0:
                await asyncio.sleep(0.1)  # Yield control to the event loop
                continue
            image = cv2.resize(image, (self.width, self.height))  # Lower resolution for faster processing
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            detector.detect_async(mp_image, time.time_ns() // 1_000_000)
            
            fps_text = 'FPS = {:.1f}'.format(self.FPS)
            text_location = (self.left_margin, self.row_size)
            current_frame = image
            cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                        self.font_size, self.text_color, self.font_thickness, cv2.LINE_AA)
    	    
            if self.detection_result_list:
                for detection in self.detection_result_list[0].detections:
                    category = detection.categories[0]
                    category_name = category.category_name
                    probability = round(category.score, 2)
                    temp["category_name"] = category_name
                    temp["probability"] = probability
                self.detected_object_info["category_name"] = temp["category_name"]
                self.detected_object_info["probability"] = temp["probability"]
                
                current_frame,pp = visualize(current_frame, self.detection_result_list[0])
                if pp is None:
                    self.detected_object_info["category_name"] = None
                    self.detected_object_info["probability"] = 0
                self.detection_frame = current_frame
                self.detection_result_list.clear()
            

            if self.detection_frame is not None and display == 1:
                cv2.imshow('object_detection', self.detection_frame)

            if cv2.waitKey(1) == 27:  # ESC key to exit
                break
            await asyncio.sleep(0)  # Yield control to the event loop
        detector.close()
        cap.release()
        cv2.destroyAllWindows()

    async def monitor_detection_info(self):
        """Monitor and print detection information at regular intervals."""
        while True:
            self.get_detected_object_info()
            await asyncio.sleep(0)
    async def start(self):
        """Start the object detection process and monitor detection info."""
        capture_task = asyncio.create_task(self.capture_frames(display=0))
        monitor_task = asyncio.create_task(self.monitor_detection_info()) 
        await asyncio.gather(capture_task, monitor_task)
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model',
        help='Path of the object detection model.',
        required=False,
        default='tensor/last.tflite')
    parser.add_argument(
        '--maxResults',
        help='Max number of detection results.',
        required=False,
        default=5)
    parser.add_argument(
        '--scoreThreshold',
        help='The score threshold of detection results.',
        required=False,
        type=float,
        default=0.25)
    parser.add_argument(
        '--cameraId', help='Id of camera.', required=False, type=int, default=0)
    parser.add_argument(
        '--frameWidth',
        help='Width of frame to capture from camera.',
        required=False,
        type=int,
        default=480)
    parser.add_argument(
        '--frameHeight',
        help='Height of frame to capture from camera.',
        required=False,
        type=int,
        default=240)
    args = parser.parse_args()
    camera = Kamera()
    
    object_detection = ObjectDetection(camera,
        args.model, int(args.maxResults),
        args.scoreThreshold, args.frameWidth, args.frameHeight)
    img=camera.getVideo()
    asyncio.run(object_detection.start(img=img))
    
if __name__ == '__main__':
    main()
