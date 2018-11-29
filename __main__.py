import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps
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


# Commands list
commands = []
commands.append(("say ", lambda robot, msg : robot.say_text(msg[4:])))
commands.append(("spin", lambda robot, msg : robot.behavior.turn_in_place(degrees(360))))
commands.append(("turn ", lambda robot, msg : robot.behavior.turn_in_place(degrees(int(msg[5:])))))

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
    except:
        pass