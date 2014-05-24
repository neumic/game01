import noise
from OpenGL.arrays import vbo
from numpy import array, float32, int32

def genTerrain( length, breadth):
   verts = []
   indices = []
   _current_index = 0

   for x in range(length):
      for z in range(breadth):
         verts.append( [x,   noise.snoise2(x,z), z ] )
         if x >= 1 and z >= 1:
            indices.append( [ _current_index, _current_index - 1, _current_index - breadth ])
            indices.append( [ _current_index - breadth - 1, _current_index - 1, _current_index - breadth ])
         _current_index += 1

   vert_array = array(verts, dtype=float32)
   index_array = array(indices, dtype=int32)

   return vert_array, index_array
