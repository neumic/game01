import noise
import pyrr
from OpenGL.arrays import vbo

import numpy as np
from numpy import array, float32
from scipy.spatial import Delaunay
from numpy.random import multivariate_normal, triangular
import random

class Grass:
   def __init__(self):
      t = array( multivariate_normal([0,0], [[1024,0], [0,1024]], 2048),
                    dtype=float32 ).transpose()
      points_ground = np.vstack(( t[0], np.zeros_like(t[0]), t[1])).transpose()
      points_side = points_ground + [0.,2.,-0.3]
      points_top = points_ground + [0.,0.,-0.3]
      vert_array = np.empty( (points_ground.shape[0] * 3, 3 ), dtype=float32 )
      vert_array[::3,:] = points_ground
      vert_array[1::3,:] = points_side
      vert_array[2::3,:] = points_top
      index_array = np.asarray(np.arange(len(vert_array))[::-1], dtype=np.int32)
      self.index_array = index_array
      self.vert_array = vert_array

   def get_arrays( self ):
      return self.vert_array, self.index_array

class Grass_sphere:
   def __init__(self, radius, number):
      #generate 'number' of random vectors and normalize, then scale by 'radius'
      radius_scale_mat = pyrr.matrix44.create_from_scale( array([radius, 
                                                                 radius,
                                                                 radius]) )
      tiny_rot_x = pyrr.matrix44.create_from_x_rotation( 0.1 )
      tiny_rot_y = pyrr.matrix44.create_from_y_rotation( 0.1 )

      sphere_pts = array( [pyrr.matrix44.apply_to_vector( radius_scale_mat,
                              pyrr.vector.normalise(vec))
                           for vec in 2 * np.random.random((number, 3)) - 1],
                          dtype=float32 )
      
      side_pts = array( [pyrr.matrix44.apply_to_vector(tiny_rot_x, vec)
                         for vec in sphere_pts],
                        dtype=float32 )

      top_pts = array( [pyrr.matrix44.apply_to_vector(tiny_rot_y, vec)
                         for vec in sphere_pts],
                        dtype=float32 )

      vert_array = np.empty( (sphere_pts.shape[0] * 3, 3 ), dtype=float32 )
      vert_array[::3,:] = sphere_pts
      vert_array[1::3,:] = side_pts
      vert_array[2::3,:] = top_pts
      index_array = np.asarray(np.arange(len(vert_array))[::-1], dtype=np.int32)
      self.index_array = index_array
      self.vert_array = vert_array

   def get_arrays( self ):
      return self.vert_array, self.index_array



class Terrain:
   def __init__( self, length, breadth ):
      self.length = length
      self.breadth = breadth
      self.index_array = np.empty((0,3),dtype=np.int32)
      self.vert_array = np.empty((0,3))
      self.gen_random_delaunay()

   def gen_random_delaunay( self ):
      points = array( multivariate_normal([0,0], 
                                          [[128**2,0], [0,128**2]],
                                          256**2), dtype=float32)
      delaunay = Delaunay( points )
      t = points.transpose()
      points = np.vstack(( t[0], np.zeros_like(t[0]), t[1])).transpose()

      self.vert_array = array(points, dtype=float32)
      self.index_array = delaunay.simplices
   
   def get_arrays( self ):
      return self.vert_array, self.index_array

