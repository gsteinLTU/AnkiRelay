import os
import random
import re
import socket
import string
import struct
import threading
import time
import types

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from environs import Env

import anki_vector
import anki_vector.events
import anki_vector.screen
import anki_vector.util


# Controls a single robot
class RobotThread(threading.Thread):

    # Sends a message to the server
    def _sendtoserver(self, msg):
        print(msg)
        self.sock.sendto(msg, (server, port))

    # More user-friendly option to send to server, includes header
    def send_info_to_server(self, msg):
        self._sendtoserver(self.serial[2:].encode('ascii') + int(time.time()).to_bytes(4,'big') + msg)

    def state_listener(self, _, msg):
        try:
            # Generate hardware key after sufficient flipped time
            if msg.accel.z < -3000:
                if self.flipped_count == 15:
                    self.send_info_to_server(b'' + ord('P').to_bytes(1, 'big') + b'\x00')
                    time.sleep(0.001)
                    self.send_info_to_server(b'' + ord('P').to_bytes(1, 'big') + b'\x01')
                self.flipped_count = self.flipped_count + 1
            else:
                self.flipped_count = 0
        except Exception as e:
            print(e)

    def __init__(self, serial : str, key_length : int = 4):
        super().__init__()

        # Serial number of robot
        self.serial = serial 

        # Used to keep track of time spend upside down for hardware key trigger
        self.flipped_count = 0

    def run(self):
        while True:
            # Attempt to connect to robot
            try:
                self.robot = anki_vector.AsyncRobot(self.serial.strip(), enable_face_detection=False, enable_camera_feed=False)
                self.robot.connect()
                self.robot.events.subscribe_by_name(self.state_listener, event_name='robot_state')
                self.robot.behavior.set_head_angle(anki_vector.util.degrees(45))
                
                # Setup server connection
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
                self.sock.bind(('', 0))
                
                self.sock.settimeout(2)
                
                # Begin waiting for commands
                while True:
                    # Send announcement
                    self.send_info_to_server('A'.encode('utf-8'))

                    # Wait for message
                    try:
                        data, addr = self.sock.recvfrom(128)

                        command = chr(data[0])
                        commandargs = data[1:]

                        print("Command: " + str(data))

                        # TODO: Change commands to be stored in more elegant manner
                        if command == 'D' or command =='S': # Drive
                            l = int.from_bytes(data[1:2], 'big', signed=True)
                            r = int.from_bytes(data[3:4], 'big', signed=True)
                            self.robot.motors.set_wheel_motors(l, r)
                        elif command == 'R': # Distance
                            dist = int(self.robot.proximity.last_sensor_reading.distance.distance_mm)
                            dist = dist.to_bytes(2, 'little')
                            output = b''
                            output += ord('R').to_bytes(1, 'big')
                            output += dist
                            self.send_info_to_server(output)
                        elif command == 'l': # Lift
                            h = struct.unpack('f', commandargs)[0]
                            print(h)
                            self.robot.behavior.set_lift_height(h)
                        elif command == 's': # Speak
                            self.robot.say_text(commandargs.decode('utf-8'))
                        elif command == 'K': # Display key

                            # Assemble key string
                            if key_mode == 'int':
                                key = [str(int(byte)) for byte in commandargs[1:]]
                                keytext = ' '.join(key)
                            elif key_mode == 'binary':
                                key = [bin(byte)[2:].zfill(4) for byte in commandargs[1:]]
                                keytext = '\n'.join(key)
                                
                            # Generate and display image
                            keyimage = PIL.Image.new('RGBA', (184, 96), (0,0,0,255))
                            context = PIL.ImageDraw.Draw(keyimage)
                            context.text((0,0), keytext, fill=(255,255,255,255), font=PIL.ImageFont.truetype("arial.ttf", 21))
                            keyimage = anki_vector.screen.convert_image_to_screen_data(keyimage)
                            self.robot.screen.set_screen_with_image_data(keyimage, 0.5, interrupt_running=True)
                            time.sleep(0.1)
                            self.robot.screen.set_screen_with_image_data(keyimage, 5.0, interrupt_running=True)
                    
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
            else:
                self.sock.close()

            time.sleep(1)

# Read settings
env = Env()
env.read_env()
server = env('SERVER')
port = int(env('PORT'))
key_mode = env('KEYMODE', default='int')

# Read robot list
robots = []
with open(".robots") as robotfile:
    robots = robotfile.readlines()

# Quit if no robots found
if robots == []:
    raise Exception("No robots in .robots file.")

# Connect to robots
robots = [RobotThread(robot.strip()) for robot in robots]

# Run robots on their own threads
for robot in robots:
    robot.start()

# Let the robots do their thing
while True:
    pass
