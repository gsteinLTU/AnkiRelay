import anki_vector
import socket
import os
from environs import Env

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
robots = [anki_vector.Robot(robot) for robot in robots]

for robot in robots:
    robot.connect()

# Setup server connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4791))
sock.settimeout(2)

while True:
    # Send announcement
    for robot in robots:
        msg = robot._name
        print(msg.encode("ascii"))
        sock.sendto(msg.encode("ascii"), (server, port))
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

        if robot == []:
            print("Invalid robot")
        else:
            msg = msg[1]

            print("Received command " + msg)
            if msg.startswith("say "):
                robot[0].say_text(msg[4:])
    except:
        pass