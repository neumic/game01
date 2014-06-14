import noise
import pyrr
from OpenGL.arrays import vbo
from numpy import array, float32, int32, zeros, ones, zeros_like, concatenate, vstack, hstack, column_stack
from scipy.spatial import Delaunay
from numpy.random import multivariate_normal, triangular
import random

class Terrain:
   def __init__( self, length, breadth ):
      self.length = length
      self.breadth = breadth
      self.gen_random_delaunay()
      
      pass

   def gen_random_delaunay( self ):
      points = array( multivariate_normal([0,0], [[128**2,0], [0,128**2]], 256**2), dtype=float32)
      #points = array( column_stack( [triangular( -3000., 0., 3000, 90000 ), triangular( -3000., 0., 3000., 90000)] ) )
      delaunay = Delaunay( points )
      t = points.transpose()
      points = vstack(( t[0], zeros_like(t[0]), t[1])).transpose()

      self.vert_array = array(points, dtype=float32)
      self.index_array = delaunay.simplices
   
   def get_arrays( self ):
      return self.vert_array, self.index_array

