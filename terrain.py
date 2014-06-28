import noise
import pyrr
from OpenGL.arrays import vbo

import numpy as np
from numpy import array, float32
from scipy.spatial import Delaunay
from numpy.random import multivariate_normal, triangular
import random

class Terrain:
   def __init__( self, length, breadth ):
      self.length = length
      self.breadth = breadth
      self.index_array = np.empty((0,3),dtype=np.int32)
      self.vert_array = np.empty((0,3))
      self.gen_random_delaunay()
      self.gen_grass()

   def gen_grass(self):
      t = array( multivariate_normal([0,0], [[256,0], [0,256]], 2048), dtype=float32).transpose()
      points_ground = np.vstack(( t[0], np.zeros_like(t[0]), t[1])).transpose()
      points_side = points_ground + [0.,2.,-0.01]
      points_top = points_ground + [0.,0.,-0.01]
      vert_array = np.empty( (points_ground.shape[0] * 3, 3 ), dtype=float32 )
      vert_array[::3,:] = points_ground
      vert_array[1::3,:] = points_side
      vert_array[2::3,:] = points_top
      index_array = np.asarray(np.arange(len(self.vert_array), len(self.vert_array) + len(vert_array))[::-1], dtype=np.int32)
      index_array = index_array.reshape( ( len(index_array) / 3, 3 ) )
      

      self.index_array = np.vstack( (self.index_array, index_array ) )
      self.vert_array = np.vstack( ( self.vert_array, vert_array ) )

   def gen_random_delaunay( self ):
      points = array( multivariate_normal([0,0], [[128**2,0], [0,128**2]], 256**2), dtype=float32)
      #points = array( column_stack( [triangular( -3000., 0., 3000, 90000 ), triangular( -3000., 0., 3000., 90000)] ) )
      delaunay = Delaunay( points )
      t = points.transpose()
      points = np.vstack(( t[0], np.zeros_like(t[0]), t[1])).transpose()

      self.vert_array = array(points, dtype=float32)
      self.index_array = delaunay.simplices
   
   def get_arrays( self ):
      return self.vert_array, self.index_array

