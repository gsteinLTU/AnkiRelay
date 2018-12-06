import anki_vector
import socket
import os
import re
import string
from environs import Env
from commands import commands, requests

def sendtoserver(msg):
    print(msg)
    sock.sendto(msg.encode("ascii"), (server, port))

# Read settings
env = Env()
env.read_env()
server = env('SERVER')
port = int(env('PORT'))

# Read robot list
robots = []
with open(".robots") as robotfile:
    robots = robotfile.readlines()

if robots == []:
    raise Exception("No robots in .robots file.")

# Connect to robots
robots = [anki_vector.AsyncRobot(robot.strip()) for robot in robots]

for robot in robots:
    robot.connect()

# Setup server connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4791))
sock.settimeout(2)

while True:
    # Send announcement
    for robot in robots:
        sendtoserver(robot._name)
        print('.')
    
    print('\n')

    # Wait for message
    try:
        data, addr = sock.recvfrom(128)
        msg = data.decode('ascii')
        print("Received message " + msg)

        # Extract ID
        msg = msg.split(':')

        robot = [robot for robot in robots if robot._name == msg[0]]

        # Verify robot 
        if robot == []:
            print("Invalid robot")
        else:
            msg = msg[1]

            print("Received command " + msg)

            # Find command and run it
            for command in commands:
                if msg.startswith(command[0]):
                    command[1](robot[0], msg)
                    break

            if re.match("\\d+ .+", msg):
                seq = int(msg.split(' ')[0])
                msg = msg.lstrip(string.digits+' ')

                print("Sequence number " + str(seq))
                print("Received command " + msg)
                # Find requests and send result
                for request in requests:
                    if msg.startswith(request[0]):
                        result = request[1](robot[0], msg)
                        sendtoserver(robot[0]._name + ": " + str(seq) + " " + result)
                        break
    except:
        pass