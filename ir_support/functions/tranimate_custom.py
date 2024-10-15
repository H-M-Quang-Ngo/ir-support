import numpy as np
import matplotlib.pyplot as plt
from spatialmath.base import trinterp, tranimate
from typing import Generator, Optional, Union, List, Tuple

def tranimate_custom(T1: np.ndarray, T2: np.ndarray, 
                     speed: int = 1, dim: Optional[Union[List[float], Tuple[float, ...]]] = None, 
                     hold: bool = False) -> None:
    """
    Supported function to animate motion from transform T1 to T2 (SE3)

    :param T1: initial SE3 matrix
    :type T1: SE3 ndarray
    :param T2: final SE3 matrix
    :type T2: SE3 ndarray
    :param speed: Speed of the animation from 1 to 100. Default is 1
    :type speed: int
    :param dim: plot volume
    :type dim: list or tuple, [a] or [a1,a2] or [a,a2,b1,b2,c1,c2], default is [-2,2],
                or the absolute maximum translation value between two transforms [0, max]
    :param hold: keep the current frame or not, False by default
    :type hold: bool
    """
    valid_speed = int(max(1, min(speed, 100))) # check the speed input
    step_num = -valid_speed + 101
    step = 1/step_num
    def generator_transforms():
        """
        Supported function which is a generator to interpolate from transform T1 to T2
        """
        for i in np.arange(0, 1 + step, step):
            interp_step = i
            if i > 1: interp_step = 1
            yield trinterp(start= T1, end= T2, s= interp_step)

    t1_max = np.max([np.fabs(x) for x in T1[0:3, 3]])
    t2_max = np.max([np.fabs(x) for x in T2[0:3, 3]])
    max_value = np.max([t1_max, t2_max])
    if dim is None:
        if max_value > 2:
            dim = [0, max_value]
        else:
            dim = [-2, 2]
    tranimate(generator_transforms(), dim= dim, wait= True)
    if not hold:
        plt.cla()