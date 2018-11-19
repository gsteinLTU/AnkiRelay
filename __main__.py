import anki_vector
import socket
import os
from environs import Env

# Read settings
env = Env()
env.read_env()
server = env('SERVER')
port = env('PORT')

# Read robot list
robots = []
with open(".robots") as robotfile:
    robots = robotfile.readlines()

if robots == []:
    raise Exception("No robots in .robots file.")

print(robots)

# Setup connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 1974))

while True:


    data, addr = sock.recvfrom(1024)
    print("Received message " + str(data))