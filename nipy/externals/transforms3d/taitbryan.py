from transforms3d.taitbryan import *
from transforms3d.taitbryan import euler2mat as actual_euler2mat


def euler2mat(z=0, y=0, x=0):
    """ Old behavior of euler2mat replicated with wrapper
    """
    return actual_euler2mat(z, y, x)
