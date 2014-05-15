from numpy import array, float32
from pyrr import matrix44 as mat4
from pyrr import vector
import math

def lookAtMatrix( camera, target, up ):
   forward = vector.normalise(target - camera)
   side = vector.normalise( vector.cross( forward, up ) )
   #shifts 'up' to the camera's up
   up = vector.cross( side, forward )

   matrix2 = array(
      [[ side[0], up[0], -forward[0], 0.0 ],
       [ side[1], up[1], -forward[1], 0.0 ], 
       [ side[2], up[2], -forward[2], 0.0 ], 
       [     0.0,   0.0,         0.0, 1.0 ]],
      dtype = float32)

   return array(mat4.multiply( mat4.create_from_translation( -camera ), matrix2 ), dtype=float32)
   #return array(matrix2 , dtype=float32)

class Camera:
   def __init__(self, fov = 45.0, aspect = 1.0):
      self.position = array([0,0,5])
      self.horizontalAngle = 0.0
      self.verticalAngle = 0.0
      self.fov = fov
      self.aspect = aspect

   def getProjectionMatrix(self):
      return array(mat4.create_perspective_projection_matrix( self.fov, self.aspect, 0.1, 100.0 ), dtype=float32)

   def getViewMatrix(self):
      #return lookAtMatrix( array([4.0,6.0,-7.0]), array([0.,0.,0.]), array([0.,1.,0.]) )
      forward = array([ math.cos( self.verticalAngle ) * math.sin( self.horizontalAngle ),
                        math.sin( self.verticalAngle ),
                        math.cos( self.verticalAngle ) * math.cos( self.horizontalAngle ) ])
      up = array([0.,-1.,0.,])
      side = -vector.normalise( vector.cross( forward, up ) )
      #shifts 'up' to the camera's up
      up = vector.cross( side, forward )

      matrix2 = array(
         [[ side[0], up[0], forward[0], 0.0 ],
          [ side[1], up[1], forward[1], 0.0 ], 
          [ side[2], up[2], forward[2], 0.0 ], 
          [     0.0,   0.0,         0.0, 1.0 ]],
         dtype = float32)

      return array(mat4.multiply( mat4.create_from_translation( [0.,0.,-9.,] ), matrix2 ), dtype=float32)

   def addRotations( self, x, y ):
      mouseSpeed = 0.0005
      self.horizontalAngle += mouseSpeed * x
      self.verticalAngle   += mouseSpeed * y
