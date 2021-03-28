#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mola.core_mesh import Mesh
from mola import utils_math
import math
import colorsys
__author__ = ['Benjamin Dillenburger', 'Demetris Shammas', 'Mathias Bernhard']
__copyright__ = 'Copyright 2019 / Digital Building Technologies DBT / ETH Zurich'
__license__ = 'MIT License'
__email__ = ['<dbt@arch.ethz.ch>']

try:
    import numpy as np
except ImportError:
    pass


def color_hue_to_rgb(hue):
    """
    Converts a color defined as Hue (HSV, saturation and value assumed to be 100%) into red, green and blue
    and returns (r,g,b,1)
    """
    col = colorsys.hsv_to_rgb(hue, 1, 1)
    return (col[0], col[1], col[2], 1)  # alpha = 100 %


def color_numpyarray_from_value_numpyarray(value_array, min_value, max_value, min_hue, max_hue):
    ndim = value_array.ndim
    new_shape = []
    for i in range(ndim):
        new_shape.append(value_array.shape[i])
    new_shape.append(4)
    new_shape = tuple(new_shape)
    color_array = np.empty((new_shape))
    with np.nditer(value_array, flags=['multi_index']) as it:
        for x in it:
            hue = utils_math.math_map(
                x, min_value, max_value, min_hue, max_hue)
            color_array[it.multi_index] = color_hue_to_rgb(hue)
    return color_array


def grid_set_values_at_borders(grid, value):
    for i in range(grid.nx):
        for j in range(grid.ny):
            for k in range(grid.nz):
                if (i == 0 or i == grid.nx-1):
                    grid.set_value_at_xyz(value, i, j, k)
                elif (j == 0 or j == grid.ny-1):
                    grid.set_value_at_xyz(value, i, j, k)
                elif (k == 0 or k == grid.nz-1):
                    grid.set_value_at_xyz(value, i, j, k)


def grid_set_values_sinusoids(grid, freq_x=6*math.pi, freq_y=6*math.pi, freq_z=6*math.pi):
    for i in range(grid.nx):
        for j in range(grid.ny):
            for k in range(grid.nz):
                vx = math.sin(i/grid.nx * freq_x)
                vy = math.sin(j/grid.ny * freq_y)
                vz = math.sin(k/grid.nz * freq_z)
                v = utils_math.math_map((vx+vy+vz), -3.0, 3.0, -1.0, 1.0)
                grid.set_value_at_xyz(v, i, j, k)


def numpy_to_grid_values(voxel_states):
    """Returns a list of values of a voxel geometry that is described by a Numpy Array. The output list can be used as input in mola.Grid.

    Arguments
    ----------
    voxel_states : numpy.ndarray
        Numpy Array of shape (nX,nY,nZ) and dtype=int where values represent different voxel states.
    """
    shape = voxel_states.shape
    nx, ny, nz = shape[0], shape[1], shape[2]
    val1d = voxel_states.reshape((nx*ny*nz, -1))
    return [v[0] for v in list(val1d.astype('int'))]


def numpy_to_voxel_mesh(voxel_bools, voxel_colors):
    """Returns the Mesh of a voxel geometry that is described by Numpy Arrays.

    Arguments
    ----------
    voxel_bools : numpy.ndarray
        Numpy Array of shape (nX,nY,nZ) and dtype=bool where True corresponds to a Solid voxel and False corresponds to a Void voxel.
    voxel_colors : numpy.ndarray
        Numpy Array of shape (nX,nY,nZ,3) containing r,g,b values for each voxel.
    """
    shape = voxel_bools.shape
    nx, ny, nz = shape[0], shape[1], shape[2]
    mesh = Mesh()
    for index in np.ndindex(shape):
        x = index[0]
        y = index[1]
        z = index[2]
        if voxel_bools[x, y, z]:
            # (x,y) (x1,y) (x1,y1) (x,y1)
            r = voxel_colors[x, y, z, 0]
            g = voxel_colors[x, y, z, 1]
            b = voxel_colors[x, y, z, 2]
            # rgb=voxel_colors[x,y,z]
            rgb = (r, g, b, 1)
            if x == nx - 1 or not voxel_bools[x+1, y, z]:
                v1 = mesh.add_vertex(x + 1, y, z)
                v2 = mesh.add_vertex(x + 1, y + 1, z)
                v3 = mesh.add_vertex(x + 1, y + 1, z + 1)
                v4 = mesh.add_vertex(x + 1, y, z + 1)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
            if x == 0 or not voxel_bools[x-1, y, z]:
                v1 = mesh.add_vertex(x, y + 1, z)
                v2 = mesh.add_vertex(x, y, z)
                v3 = mesh.add_vertex(x, y, z + 1)
                v4 = mesh.add_vertex(x, y + 1, z + 1)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
            if y == ny - 1 or not voxel_bools[x, y+1, z]:
                v1 = mesh.add_vertex(x + 1, y + 1, z)
                v2 = mesh.add_vertex(x, y + 1, z)
                v3 = mesh.add_vertex(x, y + 1, z + 1)
                v4 = mesh.add_vertex(x + 1, y + 1, z + 1)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
            if y == 0 or not voxel_bools[x, y-1, z]:
                v1 = mesh.add_vertex(x, y, z)
                v2 = mesh.add_vertex(x + 1, y, z)
                v3 = mesh.add_vertex(x + 1, y, z + 1)
                v4 = mesh.add_vertex(x, y, z + 1)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
            if z == nz-1 or not voxel_bools[x, y, z+1]:
                v1 = mesh.add_vertex(x, y, z + 1)
                v2 = mesh.add_vertex(x + 1, y, z + 1)
                v3 = mesh.add_vertex(x + 1, y + 1, z + 1)
                v4 = mesh.add_vertex(x, y + 1, z + 1)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
            if z == 0 or not voxel_bools[x, y, z-1]:
                v1 = mesh.add_vertex(x, y + 1, z)
                v2 = mesh.add_vertex(x + 1, y + 1, z)
                v3 = mesh.add_vertex(x + 1, y, z)
                v4 = mesh.add_vertex(x, y, z)
                new_face = mesh.add_face([v1, v2, v3, v4])
                new_face.color = rgb
    mesh.update_topology()
    return mesh
