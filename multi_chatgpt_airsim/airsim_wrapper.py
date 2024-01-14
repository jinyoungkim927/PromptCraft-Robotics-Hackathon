import base64
import json
import math
import os
import random
import threading
import time

import airsim
import cv2
import numpy as np
import openai
import requests

objects_dict = {
    "turbine1": "BP_Wind_Turbines_C_1",
    "turbine2": "StaticMeshActor_2",
    "solarpanels": "StaticMeshActor_146",
    "crowd": "StaticMeshActor_6",
    "car": "StaticMeshActor_10",
    "tower1": "SM_Electric_trellis_179",
    "tower2": "SM_Electric_trellis_7",
    "tower3": "SM_Electric_trellis_8",
}


class AirSimWrapper:
    def __init__(self):
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True, "Drone1")
        self.client.enableApiControl(True, "Drone2")
        self.client.armDisarm(True, "Drone1")
        self.client.armDisarm(True, "Drone2")
        self.stop_thread = False
        self.flutter_thread = None
        print(self.client.listVehicles())

    def takeoff(self, vehicle_name):
        self.client.takeoffAsync(vehicle_name=vehicle_name).join()

    def land(self, vehicle_name):
        self.client.landAsync(vehicle_name=vehicle_name).join()

    def get_drone_position(self, vehicle_name):
        pose = self.client.simGetVehiclePose(vehicle_name=vehicle_name)
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]

    def fly_to(self, point, vehicle_name):
        if point[2] > 0:
            self.client.moveToPositionAsync(point[0], point[1], -point[2], 5, vehicle_name=vehicle_name).join()
        else:
            self.client.moveToPositionAsync(point[0], point[1], point[2], 5, vehicle_name=vehicle_name).join()

    def fly_path(self, points, vehicle_name):
        airsim_points = []
        for point in points:
            if point[2] > 0:
                airsim_points.append(airsim.Vector3r(point[0], point[1], -point[2]))
            else:
                airsim_points.append(airsim.Vector3r(point[0], point[1], point[2]))
        self.client.moveOnPathAsync(
            airsim_points,
            5,
            120,
            airsim.DrivetrainType.ForwardOnly,
            airsim.YawMode(False, 0),
            20,
            1,
            vehicle_name=vehicle_name
        ).join()

    def set_yaw(self, yaw, vehicle_name):
        self.client.rotateToYawAsync(yaw, 5, vehicle_name=vehicle_name).join()

    def get_yaw(self, vehicle_name):
        orientation_quat = self.client.simGetVehiclePose(vehicle_name=vehicle_name).orientation
        yaw = airsim.to_eularian_angles(orientation_quat)[2]
        return yaw

    def get_position(self, object_name, vehicle_name):
        query_string = objects_dict[object_name] + ".*"
        object_names_ue = []
        while len(object_names_ue) == 0:
            object_names_ue = self.client.simListSceneObjects(query_string)
        pose = self.client.simGetObjectPose(object_names_ue[0], vehicle_name=vehicle_name)
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]