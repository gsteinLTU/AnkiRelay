import anki_vector
import socket
import os
import re
import string
from environs import Env
from commands import commands, requests
import threading 
import time

class RobotThread(threading.Thread):
    lastport = 32323

    # Sends a message to the server
    def sendtoserver(self, msg):
        print(msg)
        self.sock.sendto(msg.encode("ascii"), (server, port))

    def __init__(self, serial):
        super().__init__()
        self.serial = serial
        
    def run(self):
        while True:
            # Attempt to connect to robot
            try:
                self.robot = anki_vector.AsyncRobot(self.serial.strip())
                self.robot.connect()

                # Setup server connection
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind(('localhost', RobotThread.lastport))
                self.sock.settimeout(2)

                RobotThread.lastport = RobotThread.lastport + 1
                # Begin waiting for commands
                while True:
                    # Send announcement
                    self.sendtoserver(self.serial)

                    # Wait for message
                    try:
                        data, addr = self.sock.recvfrom(128)
                        #msg = data.decode('ascii')
                        #print("Received message " + msg)

                        command = chr(data[0])
                        commandargs = data[1:]

                        print("Command: " + str(command))

                        if command == 'D':
                            l = int.from_bytes(data[1:2], 'big', signed=True)
                            r = int.from_bytes(data[3:4], 'big', signed=True)
                            print(l, r)
                            self.robot.motors.set_wheel_motors(l, r)
                        if command == 'S':
                            l = int.from_bytes(data[1:2], 'big', signed=True)
                            r = int.from_bytes(data[3:4], 'big', signed=True)
                            self.robot.motors.set_wheel_motors(l, r)
                    
                    except Exception as e:
                        print(e)
            except Exception as e:
                pass
            else:
                self.sock.close()

            time.sleep(1)

    


# Read settings
env = Env()
env.read_env()
server = env('SERVER')
port = 1973

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

# Let robots do their thing
while True:
    pass