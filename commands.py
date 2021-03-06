import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps

# Commands list
commands = []
commands.append(("say ", lambda robot, msg : robot.say_text(msg[4:])))
commands.append(("spin", lambda robot, msg : robot.behavior.turn_in_place(degrees(360))))
commands.append(("turn ", lambda robot, msg : robot.behavior.turn_in_place(degrees(int(msg[5:])))))
commands.append(("drivemm ", lambda robot, msg : robot.behavior.drive_straight(distance_mm(int(msg[8:])), speed_mmps(50))))
commands.append(("set lift ", lambda robot, msg : robot.behavior.set_lift_height(float(msg[9:]))))
commands.append(("set head ", lambda robot, msg : robot.behavior.set_head_angle(degrees((float(msg[9:]))))))
commands.append(("set speed ", lambda robot, msg : robot.motors.set_wheel_motors(float(msg.split(' ')[2]), float(msg.split(' ')[3]))))

# Requests
requests = []
requests.append(("get range", lambda robot, msg : str(int(robot.proximity.last_sensor_reading.distance.distance_mm))))
