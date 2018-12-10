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
                        msg = data.decode('ascii')
                        print("Received message " + msg)

                        #     # Find command and run it
                        #     for command in commands:
                        #         if msg.startswith(command[0]):
                        #             command[1](robot[0], msg)
                        #             break

                        #     if re.match("\\d+ .+", msg):
                        #         seq = int(msg.split(' ')[0])
                        #         msg = msg.lstrip(string.digits+' ')

                        #         print("Sequence number " + str(seq))
                        #         print("Received command " + msg)
                        #         # Find requests and send result
                        #         for request in requests:
                        #             if msg.startswith(request[0]):
                        #                 result = request[1](robot[0], msg)
                        #                 sendtoserver(robot[0]._name + ": " + str(seq) + " " + result)
                        #                 break
                    
                    except Exception as e:
                        pass
            except Exception as e:
                pass

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

if robots == []:
    raise Exception("No robots in .robots file.")

# Connect to robots
robots = [RobotThread(robot.strip()) for robot in robots]

for robot in robots:
    robot.start()

while True:
    pass
    

    