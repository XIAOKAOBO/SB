#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
import socket


import memory_buffer as mb

# import camera driver
# if os.environ.get('CAMERA'):
#     # Camera = import_module('camera_' + os.environ['CAMERA']).Camera
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
from base_camera import BaseCamera


app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""

    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed_1')
def video_feed_1():
    cam1=BaseCamera(5001)
    # cam1.setup()
    return Response(gen(cam1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_2')
def video_feed_2():
    cam1=BaseCamera(5002)
    # cam1.setup()
    return Response(gen(cam1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
              

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)