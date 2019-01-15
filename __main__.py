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

    def __init__(self, serial : str, key_length : int = 4):
        super().__init__()

        # Serial number of robot
        self.serial = serial 

        # Used to keep track of touches for hardware key trigger
        self.touch_count = 0

        # # HW key size in numbers
        # self.key_length = key_length
        self.receiving_key = False
        self.key_buff = []

        # Status of virtual LEDs for display
        self.leds = [0, 0]
        self.ledtimer = threading.Timer(0.1, self.drawLEDs)

    # Update value of virtual LED
    def updateLED(self, pos, value):
        # Validate length
        if(pos > len(self.leds)):
            return
        
        self.leds[pos] = value

    # Display virtual LEDs on screen
    def drawLEDs(self):
        lastledstate = [0, 0]
        
        # Default to blank image
        image = PIL.Image.new('RGBA', anki_vector.screen.dimensions(), (0,0,0,255))
        image = anki_vector.screen.convert_image_to_screen_data(image)

        while True:
            # Don't redraw image if unneeded
            if not all([lastledstate[i] == self.leds[i] for i in range(0,len(self.leds))]):
                try:
                    image = PIL.Image.new('RGBA', anki_vector.screen.dimensions(), (0,0,0,255))
                    context = PIL.ImageDraw.Draw(image)

                    for i in range(0,len(self.leds)):
                        value = self.leds[i]
                        context.ellipse([0 + 64 * i, 0, 32 + 64 * i, 32], fill=(value * 255,value * 255,value * 255,255))

                    image = anki_vector.screen.convert_image_to_screen_data(image)
                    lastledstate = [self.leds[i] for i in range(0,len(self.leds))]
                except Exception as e:
                    print(e)
                              
            self.robot.screen.set_screen_with_image_data(image, 0.2, interrupt_running=True)
            time.sleep(0.2)

    def run(self):
        while True:
            # Attempt to connect to robot
            try:
                self.robot = anki_vector.AsyncRobot(self.serial.strip(), enable_face_detection=False, enable_camera_feed=False)
                self.robot.connect()
                self.ledtimer.start()
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
                        elif command == 'L': #LED
                            if self.receiving_key:
                                self.key_buff.append(data)

                                if len(self.key_buff) == 16:
                                    self.receiving_key = False
                                    print(self.key_buff)
                            else:
                                self.updateLED(data[1], data[2])
                        elif command == 'l': # Lift
                            h = struct.unpack('f', data[1:])[0]
                            print(h)
                            self.robot.behavior.set_lift_height(h)
                        elif command == 's': # Speak
                            self.robot.say_text(data[1:].decode('utf-8'))
                    
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
            else:
                self.ledtimer.cancel()
                self.sock.close()

            time.sleep(1)

# Read settings
env = Env()
env.read_env()
server = env('SERVER')
port = int(env('PORT'))

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
