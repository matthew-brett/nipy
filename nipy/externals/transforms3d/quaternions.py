from transforms3d.quaternions import *

from transforms3d.axangles import axangle2mat as axangle2rmat

# Some renamings in transforms3d
conjugate = qconjugate
eye = qeye
mult = qmult
inverse = qinverse
norm = qnorm
isunit = qisunit
