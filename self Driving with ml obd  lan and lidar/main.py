import asyncio
import websockets
import datetime
import cv2
from cameraModel import Kamera
from helpFunctions import helpFunctions
from lane import getLaneCurve
from reifen import Robot
from time import sleep
import numpy as np
from lidar import Lidar
import json
import os
import threading
from testlite import ObjectDetection
import argparse

class MD:
    def __init__(self, ip, port, path):
        ''' Initialize the MD class with the following attributes:
        - uri: The URI of the server.
        - camera: The Kamera object.
        - reifenSteurung: The Robot object.
        - lidar: The Lidar object.
        - help: The helpFunctions object.
        '''
        self.rPath = path
        self.uri = f"ws://{ip}:{port}"
        self.camera = Kamera()
        self.reifenSteurung = Robot(self.rPath)
        self.lidar = Lidar(self.rPath)
        self.help = helpFunctions()
        self.speed = 0.0
        self.detectedObjTensor = None
        # Initialize object detection with appropriate arguments
        self.object_detection = ObjectDetection(
        self.camera,
        model='/home/yousef/Desktop/selfDrivingD/last.tflite',
        max_results=5,
        score_threshold=0.25,
        width=480,
        height=240
        )
       
    # def monitor_ranges(self, data, tolerance=5):
    #     '''Monitor the ranges and return the status of the robot.
    #     Parameters:
    #         data (dict): The range data from the Lidar sensor.
    #         tolerance (int): The tolerance value for the range data.
    #     Returns:
    #         str: The status of the robot.
    #     '''
    #     def is_close(val1, val2):
    #         ''' Check if two values are within the tolerance. '''
    #         #print(abs(val2 - val1),'--------',abs(val1 - val2))
    #         return abs(val2 - val1) <= tolerance

    #     def check_position(value, status, x):
    #         #print(value, status, x)
    #         ''' Update the status based on the position value. '''
    #         if 15 <= value <= 45:
    #             status["FrontR"] = x
    #         elif 315 < value < 345:
    #             status["FrontL"] = x
    #         elif 0 <= value < 15 or 345 <= value < 360:
    #             status["FrontM"] = x
    #         return status

    #     def check_series(range_data):
    #         ''' Check series in the range data and update the status accordingly. '''
    #         if len(range_data) < 29:
    #             return  # No series to check
            
    #         current_value = None
    #         series_start = None
    #         series_length = 0
    #         in_series = False
    #         status = {"FrontR": 1, "FrontM": 1, "FrontL": 1}

    #         for i, (key, value) in enumerate(range_data):
    #             if current_value is None:
    #                 current_value = value
    #                 series_start = key
    #                 series_length = 1
    #                 in_series = True
    #             elif is_close(value, current_value):
    #                 series_length += 1
    #                 in_series = True
    #             else:
    #                 if in_series and series_length > 3:
    #                     if current_value != 0:
    #                         if current_value < 30:
    #                             status = check_position(series_start, status, 0)
    #                         elif 30 <= current_value < 45:
    #                             status = check_position(series_start, status, 2)
    #                         else:
    #                             status = check_position(series_start, status, 1)
    #                 current_value = value
    #                 series_start = key
    #                 series_length = 1
    #                 in_series = True

    #         if in_series and series_length > 3:
    #             if current_value != 0:
    #                 if current_value < 30:
    #                     status = check_position(series_start, status, 0)
    #                 elif 30 <= current_value < 45:
    #                     status = check_position(series_start, status, -1)
    #                 else:
    #                     status = check_position(series_start, status, 1)
            
    #         return status

    #     def extract_clusters(data):
    #         ''' Extract clusters from the data. '''
    #         frontc1 = [(int(k), v) for k, v in data.items() if 0 <= int(k) <= 45]
    #         frontc2 = [(int(k), v) for k, v in data.items() if 315 <= int(k) <= 360]
    #         frontc1.sort()
    #         frontc2.sort()
    #         return frontc1 + frontc2

    #     def process_clusters(clusters):
    #         ''' Process clusters to check errors and series. '''
    #         frontR = [(k, v) for k, v in clusters if 15 <= int(k) <= 45]
    #         frontR = self.help.check_error(sorted(frontR, reverse=True))
            
    #         frontM1 = [(k, v) for k, v in clusters if 0 <= int(k) < 15]
    #         frontM2 = [(k, v) for k, v in clusters if 345 <= int(k) < 360]
    #         frontM = self.help.check_error(sorted(frontM1 + frontM2, reverse=True))
            
    #         frontL = [(k, v) for k, v in clusters if 315 < int(k) < 345]
    #         frontL = self.help.check_error(sorted(frontL, reverse=True))
            
    #         return frontR + frontM + frontL

    #     clusters = extract_clusters(data)
    #     processed_clusters = process_clusters(clusters)
    #     msg = check_series(processed_clusters)
    #     status = self.help.check_status(msg)
        
    #     return [msg, status]
    
    
    def monitor_ranges(self, data, tolerance=5):
        '''Monitor the ranges and return the status of the robot.
        Parameters:
            data (dict): The range data from the Lidar sensor.
            tolerance (int): The tolerance value for the range data.
        Returns:
            str: The status of the robot.
        '''
        def is_close(val1, val2, rel_tol=tolerance):
            ''' Check if two values are within the relative tolerance. '''
            return abs(val1 - val2) <= rel_tol

        def check_position_Front(value, status, x):
            ''' Update the status based on the position value. '''
            if 15 <= value <= 45:
                status["FrontR"] = x
            elif 315 < value < 345:
                status["FrontL"] = x
            elif 0 <= value < 15 or 345 <= value < 360:
                status["FrontM"] = x
            return status
        def check_position_Back(value, status, x):
            ''' Update the status based on the position value. '''
            if 135 <= value <= 255:
                status["Back"] = x
            return status
        def check_position_Left(value, status, x):
            ''' Update the status based on the position value. '''
            if 225 <= value <= 315:
                status["Left"] = x
            return status
        def check_position_Right(value, status, x):
            ''' Update the status based on the position value. '''
            if 45 <= value <= 135:
                status["Right"] = x
            return status

        def check_series(range_data,cluster):
            ''' Check series in the range data and update the status accordingly. '''
            if cluster == 0:
                #cluster = 0 means the cluster is in the front
                if len(range_data) < 30:
                    return {}
                current_value = None
                series_start = None
                series_length = 0
                in_series = False
                status = {"FrontR": 0, "FrontM": 0, "FrontL": 0} 
                for key, value in range_data:
                    if current_value is None:
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True
                    elif is_close(value, current_value):
                        series_length += 1
                        in_series = True
                    else:
                        if in_series and series_length > 3:
                            x=3
                            if current_value != 0:
                                if current_value < 25+x:
                                    status = check_position_Front(series_start, status, 0)
                                elif 25+x <= current_value <45+x:
                                    status = check_position_Front(series_start, status, 2)
                                else:
                                    status = check_position_Front(series_start, status, 1)
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True

                if in_series and series_length > 3:
                    x=3
                    if current_value != 0:
                        if current_value < 25+x:
                                    status = check_position_Front(series_start, status, 0)
                        elif 25+x <= current_value <45+x:
                                    status = check_position_Front(series_start, status, 2)
                        else:
                                    status = check_position_Front(series_start, status, 1)
                
                return status
            elif cluster == 1:
                #cluster = 1 means the cluster is in the left
                if len(range_data) < 30:
                    return {}
                current_value = None
                series_start = None
                series_length = 0
                in_series = False
                status = {"Left": 0}
                for key, value in range_data:
                    if current_value is None:
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True
                    elif is_close(value, current_value):
                        series_length += 1
                        in_series = True
                    else:
                        if in_series and series_length > 3:
                            x=4
                            if current_value != 0:
                                if current_value < 6+x:
                                    status = check_position_Left(series_start, status, 0)
                                elif 6+x <= current_value < 25+x:
                                    status = check_position_Left(series_start, status, 2)
                                else:
                                    status = check_position_Left(series_start, status, 1)
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True

                if in_series and series_length >3:
                            x=4
                            if current_value != 0:
                                if current_value < 6+x:
                                    status = check_position_Left(series_start, status, 0)
                                elif 6+x <= current_value < 25+x:
                                    status = check_position_Left(series_start, status, 2)
                                else:
                                    status = check_position_Left(series_start, status, 1)
                
                return status
            elif cluster == 2:
                print(range_data)
                #cluster = 2 means the cluster is in the right
                if len(range_data) < 30:
                    return {}
                current_value = None
                series_start = None
                series_length = 0
                in_series = False
                status = {"Right": 0} 
                for key, value in range_data:
                    if current_value is None:
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True
                    elif is_close(value, current_value):
                        series_length += 1
                        in_series = True
                    else:
                        if in_series and series_length >3:
                            x=4
                            if current_value != 0:
                                if current_value < 6+x:
                                    status = check_position_Right(series_start, status, 0)
                                elif 6+x <= current_value < 25+x:
                                    status = check_position_Right(series_start, status, 2)
                                else:
                                    status = check_position_Right(series_start, status, 1)
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True

                if in_series and series_length > 3:
                            print('right',series_length)
                            x=4
                            if current_value != 0:
                                if current_value < 6+x:
                                    status = check_position_Right(series_start, status, 0)
                                elif 6+x <= current_value < 25+x:
                                    status = check_position_Right(series_start, status, 2)
                                else:
                                    status = check_position_Right(series_start, status, 1)
                
                return status
            elif cluster == 3:
                #cluster = 3 means the cluster is in the back
                if len(range_data) < 30:
                    return {}
                current_value = None
                series_start = None
                series_length = 0
                in_series = False
                status = {"Back": 0}
                for key, value in range_data:
                    if current_value is None:
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True
                    elif is_close(value, current_value):
                        series_length += 1
                        in_series = True
                    else:
                        if in_series and series_length > 3:
                            x=17
                            if current_value != 0:
                                if current_value < 5+x:
                                    status = check_position_Back(series_start, status, 0)
                                elif 10+x <= current_value < 40+x:
                                    status = check_position_Back(series_start, status, 2)
                                else:
                                    status = check_position_Back(series_start, status, 1)
                        current_value = value
                        series_start = key
                        series_length = 1
                        in_series = True

                if in_series and series_length > 3:
                            x=17
                            if current_value != 0:
                                if current_value < 5+x:
                                    status = check_position_Back(series_start, status, 0)
                                elif 10+x <= current_value < 40+x:
                                    status = check_position_Back(series_start, status, 2)
                                else:
                                    status = check_position_Back(series_start, status, 1)
                
                return status      
        def extract_clusters_Front(data): 
            ''' Extract clusters from the data. '''
            frontc1 = [(int(k), v) for k, v in data.items() if 0 <= int(k) <= 45]
            frontc2 = [(int(k), v) for k, v in data.items() if 315 <= int(k) <= 360]
            frontc1.sort()
            frontc2.sort()
            return frontc1 + frontc2
            
        def extract_clusters_Back(data):
            back = [(int(k), v) for k, v in data.items() if 135 <= int(k) <= 225]
            return back
            
        def extract_clusters_Left(data):
            left = [(int(k), v) for k, v in data.items() if 225 <= int(k) <= 315]
            return left
            
        def extract_clusters_Right(data):
            right = [(int(k), v) for k, v in data.items() if 45 <= int(k) <=135]
            return right
        
            

        def processed_clusters_Front(clusters):
            ''' Process clusters to check errors and series. '''
            frontR = [(k, v) for k, v in clusters if 15 <= int(k) <= 45]
            frontR = self.help.check_error(sorted(frontR, reverse=True))
            
            frontM1 = [(k, v) for k, v in clusters if 0 <= int(k) < 15]
            frontM2 = [(k, v) for k, v in clusters if 345 <= int(k) < 360]
            frontM = self.help.check_error(sorted(frontM1 + frontM2, reverse=True))
            
            frontL = [(k, v) for k, v in clusters if 315 < int(k) < 345]
            frontL = self.help.check_error(sorted(frontL, reverse=True))
            
            return frontL + frontM + frontR
        def processed_clusters_Back(clusters):
            ''' Process clusters to check errors and series. '''
            backR = [(k, v) for k, v in clusters if 135 <= int(k) <= 165]
            backR = self.help.check_error(sorted(backR, reverse=True))
            
            backC = [(k, v) for k, v in clusters if 165 <= int(k) <= 195]
            
            backC = self.help.check_error(sorted(backC, reverse=True))
            
            backL = [(k, v) for k, v in clusters if 195 <= int(k) <= 225]
            backL = self.help.check_error(sorted(backL, reverse=True))
            
            return backL + backC + backR

        def processed_clusters_Left(clusters):
            ''' Process clusters to check errors and series. '''
            leftR = [(k, v) for k, v in clusters if 225 <= int(k) <= 255]
            leftR = self.help.check_error(sorted(leftR, reverse=True))
            
            leftC = [(k, v) for k, v in clusters if 255 <= int(k) <= 285]
            leftC = self.help.check_error(sorted(leftC, reverse=True))
            
            leftL = [(k, v) for k, v in clusters if 285 <= int(k) <= 315]
            leftL = self.help.check_error(sorted(leftL, reverse=True))
            
            return leftL + leftC + leftR
        def processed_clusters_Right(clusters):
            ''' Process clusters to check errors and series. '''
            rightR = [(k, v) for k, v in clusters if 45 <= int(k) < 75]
            rightR = self.help.check_error(sorted(rightR, reverse=True))
            
            rightC = [(k, v) for k, v in clusters if 75 <= int(k) < 105]
            rightC = self.help.check_error(sorted(rightC, reverse=True))
            
            rightL = [(k, v) for k, v in clusters if 105 <= int(k) <= 135]
            rightL = self.help.check_error(sorted(rightL, reverse=True))
            
            return rightL + rightC + rightR
        
        clusters_Front = extract_clusters_Front(data)
        clusters_Back = extract_clusters_Back(data)
        clusters_Left = extract_clusters_Left(data)
        clusters_Right = extract_clusters_Right(data)
        processed_cluster_front = processed_clusters_Front(clusters_Front)
        processed_cluster_back = processed_clusters_Back(clusters_Back)
        processed_cluster_left= processed_clusters_Left(clusters_Left)
        processed_cluster_right = processed_clusters_Right(clusters_Right)
        
        msgf = check_series(processed_cluster_front,0)
        msgl = check_series(processed_cluster_left,1)
        msgr = check_series(processed_cluster_right,2)
        msgb = check_series(processed_cluster_back,3) 
        merged_dict = {}
        for d in (msgb,msgr,msgl,msgf):
            merged_dict.update(d)
        status = self.help.check_status(merged_dict)
        return [merged_dict, status]

    async def communicate(self):
        ''' Communicate with the server. '''
        async with websockets.connect(self.uri) as websocket:
            while True:  # Loop indefinitely
                message = f"Hello, server! Time: {datetime.datetime.now()}"
                await websocket.send(message)
                print(f"Sent: {message}")
                response = await websocket.recv()
                print(f"Received: {response}")
                await asyncio.sleep(0)  # Wait for 2 seconds before sending the next message
    async def object_detection_task(self):
        ''' Asynchronous task to run object detection. '''
        while True:
            await self.object_detection.start()    
            
    async def curve(self):
        ''' Perform lane detection and control based on lidar data. '''
        frame = self.camera.getVideo()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        _, thresholded = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_saturation = np.array([0, 0, 0])
        upper_saturation = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_saturation, upper_saturation)
        result = cv2.bitwise_and(frame, frame, mask=mask)
        
        curve = getLaneCurve(result, display=0)
        curveVal = max(-1, min(1, curve[0]))  # Ensure curve is between -1 and 1
        driver = curve[1]
        lidar_data = self.lidar.get_scan_data()
        
        with open('selfDrivingD/data/detected_object_info.json', 'r') as f:
                detectObj=json.load(f)
                if detectObj is not None:
                    Obj=detectObj["Detected Object"]
                    prob=detectObj["Probability"]
                    if(prob>0.65):
                        self.detectedObjTensor = Obj
                    else:
                        self.detectedObjTensor = None
                        
        if self.help.all_values_non_zero(lidar_data):
            async with websockets.connect(self.uri) as websocket:
                message = {"lidarData": self.monitor_ranges(lidar_data)[0],"speed": self.speed, "object": self.detectedObjTensor}
                message_json = json.dumps(message)  # Convert the dictionary to a JSON string
                await websocket.send(message_json)
            print(self.monitor_ranges(lidar_data)[1] )
            if self.monitor_ranges(lidar_data)[1] == 1:
                    self.speed = 1.0
                    turn = 0
                    if driver == 1.0:
                        sen = 1.3  # SENSITIVITY
                        maxVal = 0.5  # MAX SPEED
                        if curveVal > maxVal: curveVal = maxVal
                        if curveVal < -maxVal: curveVal = -maxVal
                        if curveVal > 0:
                            sen = 10
                            if curveVal < 0.01: curveVal = 0
                        else:
                            if curveVal > -0.01: curveVal = 0
                        if self.detectedObjTensor=="green":
                            
                            self.speed =self.speed 
                        elif self.detectedObjTensor=="red" or self.detectedObjTensor=="stop":
                            self.speed =self.speed 
                        elif self.detectedObjTensor=="50Zone" :
                            self.speed =self.speed -0.2
                        elif self.detectedObjTensor=="30Zone":
                            self.speed =self.speed -0.4
                        elif  self.detectedObjTensor=="Car" or self.detectedObjTensor=="human":
                            self.speed =self.speed -0.2
                        else:
                            self.speed =self.speed
                        # message = {"speed": self.speed, "object": self.detectedObjTensor}
                        # async with websockets.connect(self.uri) as websocket: 
                        #     message = {"speed": self.speed, "object": self.detectedObjTensor}
                        #     message_json = json.dumps(message) # Convert the dictionary to a JSON string
                        #     await websocket.send(message_json)
                        turn=-curveVal * sen
                        print(f"Drive: {driver},Curve:{curveVal},speed:{self.speed },detectedObj:{self.detectedObjTensor}") 
                        #print(curveVal, -curveVal *self.speed sen)
                        self.reifenSteurung.move(self.speed ,turn , 0.005)
                    else:
                            self.reifenSteurung.allStop()
            elif self.monitor_ranges(lidar_data)[1] == 2:
                    self.speed  = 1.0
                    turn=0
                    if driver == 1.0:
                        sen = 1.3  # SENSITIVITY
                        maxVal = 0.6  # MAX SPEED
                        if curveVal > maxVal: curveVal = maxVal
                        if curveVal < -maxVal: curveVal = -maxVal
                        if curveVal > 0:
                            sen = 10
                            if curveVal < 0.1: curveVal = 0
                        else:
                            if curveVal > -0.1: curveVal = 0
                        # # print(curveVal, -curveVal * sen)
                        if self.detectedObjTensor=="green":
                            self.speed =self.speed 
                            turn=-curveVal * sen
                        elif self.detectedObjTensor=="red"or self.detectedObjTensor=="stop":
                            self.speed =0
                            turn=0
                        elif self.detectedObjTensor=="50Zone":
                            self.speed =self.speed -0.2
                            turn=-curveVal * sen
                        elif self.detectedObjTensor=="30Zone":
                            self.speed =self.speed -0.4
                            turn=-curveVal * sen  
                        elif  self.detectedObjTensor=="Car" or self.detectedObjTensor=="human":
                            self.speed =self.speed -0.4
                            turn=-curveVal * sen
                        else:
                            self.speed =self.speed 
                            turn=-curveVal * sen
                        # async with websockets.connect(self.uri) as websocket: 
                        #     message_json = json.dumps(message) # Convert the dictionary to a JSON string
                        #     await websocket.send(message_json) 
                        print(f"Drive: {driver},Curve:{curveVal},speed:{self.speed },detectedObj:{self.detectedObjTensor}") 
                        self.reifenSteurung.move(self.speed , turn, 0.05)
                    else:
                            self.reifenSteurung.allStop()
            else:
                print(self.detectedObjTensor)
                if self.detectedObjTensor=="green" or self.detectedObjTensor=="50Zone" or self.detectedObjTensor=="30Zone":
                            self.speed =1
                            sen = 1.3  # SENSITIVITY
                            maxVal = 0.5  # MAX SPEED
                            if curveVal > maxVal: curveVal = maxVal
                            if curveVal < -maxVal: curveVal = -maxVal
                            if curveVal > 0:
                                sen = 10
                                if curveVal < 0.1: curveVal = 0
                            else:
                                if curveVal > -0.1: curveVal = 0
                            print(f"Drive: {driver},Curve{curveVal},") 
                        # print(curveVal, -curveVal * sen)
                            self.reifenSteurung.move(self.speed , -curveVal * sen, 0.05)
                            # async with websockets.connect(self.uri) as websocket: 
                            #     message_json = json.dumps(message) # Convert the dictionary to a JSON string
                            #     await websocket.send(message_json)
                elif self.detectedObjTensor=="red" or self.detectedObjTensor=="stop":
                            self.speed =0
                            self.reifenSteurung.move(self.speed , 0, 0.05)
                            # async with websockets.connect(self.uri) as websocket: 
                            #     message_json = json.dumps(message) # Convert the dictionary to a JSON string
                            #     await websocket.send(message_json) 
                elif self.detectedObjTensor=="Car" or self.detectedObjTensor=="human":
                            self.speed =0
                            self.reifenSteurung.move(self.speed , 0, 0.05)
                            # async with websockets.connect(self.uri) as websocket: 
                            #     message_json = json.dumps(message) # Convert the dictionary to a JSON string
                            #     await websocket.send(message_json)
                else:        
                    print("stop Car")
                    self.reifenSteurung.allStop()       
    
    
    async def continuous_curve(self):
        while True:
            await self.curve()
            await asyncio.sleep(0.01)  # Slight delay to prevent overloading
    async def run(self):
        self.reifenSteurung.allStop()
        lidar_thread = threading.Thread(target=self.lidar.run)
        lidar_thread.start()
        #asyncio.create_task(self.lidar.run())
        while True:
            if self.lidar.getLidarState()==True:
                try:
                    curve_task = asyncio.create_task(self.continuous_curve())
                    tensor_task = asyncio.create_task(self.object_detection_task())
                    await asyncio.gather(curve_task, tensor_task)
                except KeyboardInterrupt:
                    lidar_thread.join()
                    cv2.destroyAllWindows()
                    self.reifenSteurung.allStop()
                finally:
                    lidar_thread.join()
                    cv2.destroyAllWindows()
                    self.reifenSteurung.allStop()
                    print("Exiting...")


# Usage
IP = "192.168.68.66"
PORT = "8765"
PATH = os.getcwd()
client = MD(IP, PORT, PATH)
asyncio.run(client.run())
