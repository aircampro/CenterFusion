#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Library for Realsense Camera
#
import pyrealsense2 as rs
import numpy as np

class RealsenseCapture:

    def __init__(self, d=1):
        self.WIDTH = 640
        self.HEGIHT = 480
        self.FPS = 30
        # Configure depth and color streams and decimate filter 
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, self.WIDTH, self.HEGIHT, rs.format.bgr8, self.FPS)
        self.config.enable_stream(rs.stream.depth, self.WIDTH, self.HEGIHT, rs.format.z16, self.FPS)
        self.dec_val = d
        self.decimate = rs.decimation_filter() 
        self.decimate.set_option(rs.option.filter_magnitude, 2 ** self.dec_val)
        
    def start(self):
        # Start streaming with a check to see that the camera actually has a RGB color sensor if not we exit
        self.pipeline = rs.pipeline()
        # Serial number required when connecting multiple units. Not necessary for a single unit.
        self.config.enable_device()
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()
        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with a Color sensor.. exiting")
            exit(0)        
        self.pipeline.start(self.config)
        print('pipline start')
        align_to = rs.stream.color
        self.align = rs.align(align_to)

    def read(self, is_array=True, dec=False):
        # Flag capture available
        ret = True
        # get frames
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        self.aligend_depth_frame = aligned_frames.get_depth_frame()
        self.aligend_color_frame = aligned_frames.get_color_frame()
        self.aligend_depth_frame_distance = self.aligend_depth_frame.as_depth_frame()
        # separate RGB and Depth image
        self.color_frame = frames.get_color_frame()                                                     # RGB
        self.depth_frame = frames.get_depth_frame()                                                     # Depth
        if dec == True:                                                                                 # dec == True for decimate filter
            self.depth_frame = self.decimate.process(self.depth_frame)
        if not self.color_frame or not self.depth_frame:
            ret = False
            return ret, (None, None)
        elif is_array:
            # Convert images to numpy arrays
            color_image = np.array(self.color_frame.get_data())
            depth_image = np.array(self.depth_frame.get_data())
            return ret, (color_image, depth_image)
        else:
            return ret, (self.color_frame, self.depth_frame)

    def release(self):
        # Stop streaming
        self.pipeline.stop()
