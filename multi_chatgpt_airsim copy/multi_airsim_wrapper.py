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


class MultiDroneAirSimWrapper:
    def __init__(self, drone_names):
        self.clients = {}
        for drone_name in drone_names:
            client = airsim.MultirotorClient()
            client.confirmConnection()
            client.enableApiControl(True, drone_name)
            client.armDisarm(True, drone_name)
            self.clients[drone_name] = client
        self.stop_thread = False
        self.flutter_thread = None

    def takeoff(self, drone_name):
        self.clients[drone_name].takeoffAsync().join()

    def land(self, drone_name):
        self.clients[drone_name].landAsync().join()

    def get_drone_position(self, drone_name):
        pose = self.clients[drone_name].simGetVehiclePose()
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]

    def fly_to(self, drone_name, point):
        if point[2] > 0:
            self.clients[drone_name].moveToPositionAsync(
                point[0], point[1], -point[2], 5
            ).join()
        else:
            self.clients[drone_name].moveToPositionAsync(
                point[0], point[1], point[2], 5
            ).join()

    def fly_path(self, drone_name, points):
        airsim_points = []
        for point in points:
            if point[2] > 0:
                airsim_points.append(airsim.Vector3r(point[0], point[1], -point[2]))
            else:
                airsim_points.append(airsim.Vector3r(point[0], point[1], point[2]))
        self.clients[drone_name].moveOnPathAsync(
            airsim_points,
            5,
            120,
            airsim.DrivetrainType.ForwardOnly,
            airsim.YawMode(False, 0),
            20,
            1,
        ).join()

    def set_yaw(self, drone_name, yaw):
        self.clients[drone_name].rotateToYawAsync(yaw, 5).join()

    def get_yaw(self, drone_name):
        orientation_quat = self.clients[drone_name].simGetVehiclePose().orientation
        yaw = airsim.to_eularian_angles(orientation_quat)[2]
        return yaw

    def get_position(self, drone_name, object_name):
        query_string = objects_dict[object_name] + ".*"
        object_names_ue = []
        while len(object_names_ue) == 0:
            object_names_ue = self.clients[drone_name].simListSceneObjects(query_string)
        pose = self.clients[drone_name].simGetObjectPose(object_names_ue[0])
        return [pose.position.x_val, pose.position.y_val, pose.position.z_val]
