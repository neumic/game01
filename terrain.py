import noise
import pyrr
from OpenGL.arrays import vbo
from numpy import array, float32, int32, zeros, ones, transpose, concatenate

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

   norm_dict = {}
   #for face in index_array:
      #for vert_index in face:
         #if vert_index not in norm_dict:'kernel' has bad input: nil
            #norm_dict[vert_index] = []
         #norm_dict[vert_index].append(pyrr.vector.generate_normals(*vert_array[face]))

   norm_array = ones(vert_array.shape, dtype=float32)
   #for norm_index in range(len( norm_array ) ):
      #norm_array[norm_index] = pyrr.vector.normalise( sum(norm_dict[norm_index]) )

   return vert_array, norm_array, index_array
