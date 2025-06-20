##  @file
#   @brief A 3D Robot Class defined by standard DH parameters.
#   @author Ho Minh Quang Ngo
#   @date Jul 20, 2023

import swift
import numpy as np
import roboticstoolbox as rtb
import spatialgeometry as geometry
import spatialmath.base as spb
import os
from abc import ABC
from typing import List, Dict, Union, Tuple, Optional

# Useful variables
from math import pi

# -----------------------------------------------------------------------------------#
class DHRobot3D(rtb.DHRobot, ABC):
    """
    This abstract class inherits from the DHRobot class of the `Robotics Toolbox in Python`.
    It represents a 3D Robot defined in standard DH parameters, that can be displayed in the `Swift` simulator.

    Parameters:
    -----------------------------------------------------------
    - `links`: list of DH links `roboticstoolbox.DHLink` to construct the robot
    - `link3D_names`: dictionary for names of the 3D file for each robot link in the directory, e.g. {link0: 'base', link1: 'shoulder'...}. File extension can be ply, dae, stl
    - `link3D_dir`: absolute path to the 3D files
    - `name`: name of the robot
    - `qtest`: an input joint config as a list to calibrate the 3D model. Number of elements in `qtest` is the number of robot joints
    - `qtest_transforms`: transforms of the 3D models to match the config by `qtest`.
                          Number of elements in `qtest_transforms` = number of elements in `qtest` plus 1.
                          The first element is the transform of the global coordinate to the robot.
    """

    def __init__(self, links:List[rtb.DHLink],
                 link3D_names:Dict[str, Union[str, Tuple[float, float, float, float]]],
                 link3d_dir: str,
                 name: Optional[str] = None,
                 qtest: Optional[List[float]] = None,
                 qtest_transforms: Optional[List[np.ndarray]] = None):
        """
        Initialize the 3D robot with the given DH links and 3D models

        Parameters:
        ____________
        `robot`: rtb.DHRobot
            DHRobot object
        `link3D_names`: dict
            Dictionary for names of the 3D file for each robot link in the directory, e.g. {link0: 'base', link1: 'shoulder'...}. File extension can be ply, dae, stl
        `link3D_dir`: str
            Absolute path to the 3D files
        `name`: str, optional
            Name of the robot. Default is None
        `qtest`: list, optional
            An input joint config as a list to calibrate the 3D model. Number of elements in `qtest` is the number of robot joints. Default is None
        `qtest_transforms`: list, optional
            Transforms of the 3D models to match the config by `qtest`. Number of elements in `qtest_transforms` = number of elements in `qtest` plus 1.
            The first element is the transform of the global coordinate to the robot. Default is None
        """

        super().__init__(links, name = name)
        self.link3D_names = link3D_names

        if qtest is None: # default qtest
            qtest = [0 for _ in range(self.n)]
        if qtest_transforms is None: # default transforms
            qtest_transforms = [np.eye(4) for _ in range(self.n + 1)]

        self._link3D_dir = link3d_dir
        self._qtest = qtest
        self._qtest_transforms = qtest_transforms
        self._apply_3dmodel()

    # -----------------------------------------------------------------------------------#
    def _apply_3dmodel(self):
        """
        Collect the corresponding 3D model for each link.\n
        Then compute the relation between the DH transforms for each link and the pose of its corresponding 3D object
        """
        # current_path = os.path.abspath(os.path.dirname(__file__))
        self.links_3d = []
        for i in range(self.n + 1):
            file_name = None
            for ext in ['.stl', '.dae', '.ply']:
                if os.path.exists(os.path.join(self._link3D_dir, self.link3D_names[f'link{i}'] + ext)):
                    file_name = os.path.join(self._link3D_dir, self.link3D_names[f'link{i}'] + ext)
                    break
            if file_name is not None:
                if f'color{i}' in self.link3D_names:
                    self.links_3d.append(geometry.Mesh(file_name, color = self.link3D_names[f'color{i}']))
                else:
                    self.links_3d.append(geometry.Mesh(file_name))
            else:
                raise ImportError(f'Cannot get 3D file at link {i}!')

        link_transforms = self._get_transforms(self._qtest)

        # Get relation matrix between the pose of the DH Link and the pose of the corresponding 3d object
        self._relation_matrices = [np.linalg.inv(link_transforms[i]) @ self._qtest_transforms[i]
                                   for i in range(len(link_transforms))]

    # -----------------------------------------------------------------------------------#
    def _update_3dmodel(self)->None:
        """
        Update the robot's 3D model based on the relation matrices
        """
        link_transforms = self._get_transforms(self.q)
        for i, link in enumerate(self.links_3d):
            link.T = link_transforms[i] @ self._relation_matrices[i]

    # -----------------------------------------------------------------------------------#
    def _get_transforms(self,q)->List[np.ndarray]:
        """
        Get the transform list represent each link
        """
        transforms = [self.base.A]
        L = self.links
        for i in range(self.n):
            transforms.append(transforms[i] @ L[i].A(q[i]).A)
        return transforms

    # -----------------------------------------------------------------------------------#
    def add_to_env(self, env:swift.Swift)->None:
        """
        Add the robot into a input Swift environment
        """
        if not isinstance(env, swift.Swift):
            raise TypeError('Environment must be Swift!')
        self._update_3dmodel()
        for link in self.links_3d:
            env.add(link)

    # -----------------------------------------------------------------------------------#
    def __setattr__(self, name, value):
        """
        Overload `=` operator so the object can update its 3D model whenever a new joint state is assigned
        """
        if name == 'q' and hasattr(self, 'q') or name == 'base' and hasattr(self, 'base'):
            self._update_3dmodel()  # Update the 3D model before setting the attribute
        super().__setattr__(name, value)  # Call the base class method to set the attribute

