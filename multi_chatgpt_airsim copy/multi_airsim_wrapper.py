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
        self.drones = drone_names

    def takeoff(self, drone_name=None):
        if drone_name:
            self.drones[drone_name].takeoff()
        else:
            for drone in self.drones.values():
                drone.takeoff()

    def land(self, drone_name=None):
        if drone_name:
            self.drones[drone_name].land()
        else:
            for drone in self.drones.values():
                drone.land()

    def get_drone_position(self, drone_name):
        if drone_name:
            return self.drones[drone_name].get_drone_position()
        else:
            return {
                name: drone.get_drone_position() for name, drone in self.drones.items()
            }

    def fly_to(self, point, drone_name=None):
        if drone_name:
            self.drones[drone_name].fly_to(point)
        else:
            for drone in self.drones.values():
                drone.fly_to(point)

    def fly_path(self, points, drone_name=None):
        if drone_name:
            self.drones[drone_name].fly_path(points)
        else:
            for drone in self.drones.values():
                drone.fly_path(points)

    def set_yaw(self, yaw, drone_name=None):
        if drone_name:
            self.drones[drone_name].set_yaw(yaw)
        else:
            for drone in self.drones.values():
                drone.set_yaw(yaw)

    def get_yaw(self, drone_name):
        if drone_name:
            return self.drones[drone_name].get_yaw()
        else:
            return {name: drone.get_yaw() for name, drone in self.drones.items()}

    def get_position(self, object_name, drone_name=None):
        if drone_name:
            return self.drones[drone_name].get_position(object_name)
        else:
            return {
                name: drone.get_position(object_name)
                for name, drone in self.drones.items()
            }
