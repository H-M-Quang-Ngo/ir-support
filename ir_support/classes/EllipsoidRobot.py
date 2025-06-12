# Require libraries
from typing import Optional, Union
from roboticstoolbox.backends import PyPlot
from scipy import linalg
from ir_support.functions import make_ellipsoid
import numpy as np
import matplotlib.pyplot as plt
import roboticstoolbox as rtb
import keyboard
import warnings

# ---------------------------------------------------------------------------------------#
class EllipsoidRobot:
    """
    Generate and animate a DH skeleton robot with ellipsoid for each link
    """
    def __init__(self, robot: rtb.DHRobot,
                 q: Optional[Union[np.ndarray, list]] = None,
                 fig: Optional[PyPlot.PyPlot] = None,
                 default_height: float = 0.1,
                 default_width: float = 0.1):
        """
        Generate and animate a DH skeleton robot with ellipsoid for each link

        Parameters
        ____________
        robot: rtb.DHRobot
            Robot object
        q: list or np.ndarray, optional
            Joint configuration of the robot. Default is None
        fig: PyPlot.PyPlot, optional
            Figure object. Default is None
        default_height: float, optional
            Default height of the ellipsoid. Default is 0.1
        default_width: float, optional
            Default width of the ellipsoid. Default is 0.1
        """

        if isinstance(robot, rtb.DHRobot):
            self.robot = robot
        else:
            raise TypeError('Invalid input robot type. Requires DHRobot!')
        if q == None:
            self.q = robot.q
        else:
            self.q = q
        if fig == None or not isinstance(fig, PyPlot.PyPlot):
            warnings.warn("No input figure or invalid input figure. Use the robot's plot method instead")
            self.fig = robot.plot(self.q)
        else:
            self.fig = fig

        self.default_height = default_height
        self.default_width = default_width
        self.ellipsoid_matrices = []
        self.ellipsoids_h = []
        self.colors = [[np.random.random() for _ in range(3)] for _ in range(robot.n)]

        self.ellipsoid_for_robot_links(self.q)
        self.plot_ellipsoids()

    # ---------------------------------------------------------------------------------------#
    def ellipsoid_for_robot_links(self,q):
        """
        Function to create ellipsoid for each link of robot
        """
        transforms = self._get_transforms(q)

        ellipsoids_info = []
        for i in range(len(transforms)-1):
            ax1 = transforms[i+1][:3,3]- transforms[i][:3,3]
            ax2 = np.array([-ax1[1], ax1[0], 0])
            ax3 = np.cross(ax1, ax2)
            ellipsoids_info.append({'ax1':ax1, 'ax2':ax2, 'ax3':ax3,
                                    'center': (transforms[i+1][:3,3]+ transforms[i][:3,3])/2})

        self.ellipsoid_matrices = []
        for ellipsoid in ellipsoids_info:
            ax1 = ellipsoid['ax1']
            ax2 = ellipsoid['ax2']
            ax3 = ellipsoid['ax3']

            # Normalize ax1, ax2, ax3 if their norms are not zero
            if linalg.norm(ax1) != 0:
                ax1 = ax1 / linalg.norm(ax1)
            if linalg.norm(ax2) != 0:
                ax2 = ax2 / linalg.norm(ax2)
            if linalg.norm(ax3) != 0:
                ax3 = ax3 / linalg.norm(ax3)

            axes_matrix = np.column_stack((ax1, ax2, ax3))
            diagonal_matrix = np.diag(np.square([np.linalg.norm(ellipsoid['ax1']/2),
                                        self.default_height,
                                        self.default_width]))
            ellipsoid_matrix = axes_matrix @ diagonal_matrix @ axes_matrix.T
            self.ellipsoid_matrices.append({'matrix': ellipsoid_matrix,
                                            'center': ellipsoid['center']})

    # ---------------------------------------------------------------------------------------#
    def plot_ellipsoids(self):
        """
        Function to plot the ellipsoids
        """
        self.remove_ellipsoid()
        for i, ellipsoid in enumerate(self.ellipsoid_matrices):
            ellipsoid_h, _ = make_ellipsoid(ellipsoid['matrix'], ellipsoid['center'],
                    ax = self.fig.ax, color = self.colors[i])
            self.ellipsoids_h.append(ellipsoid_h)

    # ---------------------------------------------------------------------------------------#
    def remove_ellipsoid(self):
        for ellipsoid_h in self.ellipsoids_h:
            ellipsoid_h.remove()
        self.ellipsoids_h = []

    # ---------------------------------------------------------------------------------------#
    def _get_transforms(self,q):
        transforms = [self.robot.base.A]
        L = self.robot.links
        for i in range(self.robot.n):
            transforms.append(transforms[i] @ L[i].A(q[i]).A)
        return transforms

    # ---------------------------------------------------------------------------------------#
    def teach(self):
        """
        Move the ellipsoids around with robot
        """
        self.fig._add_teach_panel(self.robot, self.robot.q)
        print("Teach mode. Press Enter to discard ellipsoids!")

        # Set up a flag to stop the loop
        stop_flag = False

        # Define a callback function to set the stop flag when Enter is pressed
        def on_enter_press(event):
            nonlocal stop_flag
            stop_flag = True

        # Register the callback function with the keyboard listener
        keyboard.on_press_key("enter", on_enter_press)

        # Main loop to update the ellipsoids
        while not stop_flag:
            self.ellipsoid_for_robot_links(self.robot.q)
            self.plot_ellipsoids()
            self.fig.step(0.05)

        # Clean up
        self.remove_ellipsoid()
        keyboard.unhook_all()  # Unhook all keyboard listeners

# ---------------------------------------------------------------------------------------#
if __name__ == "__main__":
    robot = rtb.models.DH.Planar3()
    q = robot.q
    fig = robot.plot(q)
    ellipsoid_robot = EllipsoidRobot(robot, fig = fig, default_height= 0.15, default_width= 0.15)
    input("Enter to try teach!\n")
    ellipsoid_robot.teach()
    fig.hold()
