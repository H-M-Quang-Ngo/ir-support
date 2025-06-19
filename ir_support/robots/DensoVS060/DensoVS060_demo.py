# import keyboard
# import numpy as np
# import time
# from roboticstoolbox import Robot
# import swift
# from pathlib import Path
# from spatialmath import SE3
# # from spatialgeometry import Axes 
# from ir_support.functions import create_frame_cylinders, update_frame_cylinders, add_frame_cylinders, keyboard_joint_control_loop

# # Define the directory and filename
# tld = Path(__file__).parent  # or use an absolute Path if needed
# urdf_file = "DensoVS060.urdf"

# # Read the URDF using the top-level directory (tld) override
# links, name, urdf_string, resolved_path = Robot.URDF_read(urdf_file, tld=str(tld))

# # Create the robot manually
# robot = Robot(links, name=name)
# robot.q = np.zeros(robot.n)
# robot.base = robot.base @ SE3(0, 0, 0.2)  # Adjust Z height slightly so it doesn't clip through the ground
# joint_index = 0
# print(f"Robot name: {robot.name}")

# # Launch Swift environment
# env = swift.Swift()
# env.launch(realtime=True, browser=None)
# env.add(robot)
# T = robot.fkine(robot.q)

# # ee_coordinate_frame_lines = Axes(length=0.1)
# # env.add(ee_coordinate_frame_lines)
# # ee_coordinate_frame_lines.T = T

# ee_coordinate_frame_cylinders = add_frame_cylinders(env, length=0.1, radius=0.005)
# update_frame_cylinders(ee_coordinate_frame_cylinders, T)

# def update_visuals(q, T):
#     # ee_coordinate_frame_lines.T = T
#     update_frame_cylinders(ee_coordinate_frame_cylinders, T)

# keyboard_joint_control_loop(robot, env, update_visuals)


from ir_support.models import create_denso_vs060
from ir_support.functions import create_frame_cylinders, update_frame_cylinders, add_frame_cylinders, keyboard_joint_control_loop
import swift
import numpy as np

robot = create_denso_vs060()
env = swift.Swift()
env.launch(realtime=True)
env.add(robot)

ee_coordinate_frame_cylinders = add_frame_cylinders(env, length=0.1, radius=0.005)
update_frame_cylinders(ee_coordinate_frame_cylinders, robot.fkine(robot.q))

def update_visuals(q, T):
    update_frame_cylinders(ee_coordinate_frame_cylinders, T)

keyboard_joint_control_loop(robot, env, update_visuals, step=0.05)
