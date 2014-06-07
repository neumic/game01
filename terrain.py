import noise
import pyrr
from OpenGL.arrays import vbo
from numpy import array, float32, int32, zeros, ones, transpose, concatenate
import random

def terrainNoise( x, z, length, breadth):
   return 0.0

def genTerrain( length, breadth):
   verts = []
   indices = []
   _current_index = 0

   for x in range(length):
      for z in range(breadth):
         verts.append( [x, terrainNoise( x,z, length, breadth ), z ] )
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

def genTrees( length, breadth, number ):
   tree_verts = []
   tree_norms = []
   tree_indices = []
   for num in range( number ):
      x = random.random() * length
      z = random.random() * breadth
      trees = genTree( 20, array([ x, terrainNoise( x, z, length, breadth) - 1, z]))
      for face in trees[2]:
         tree_indices.append(list( map( lambda x: x + len(tree_verts), face ) ))
      tree_verts += trees[0]
      tree_norms += trees[1]

   return tree_verts, tree_norms, tree_indices
   
def genTree( height, position ):
   tree_verts = [
      [position[0], position[1], position[2]],
      [position[0], position[1] + height, position[2]],
      [position[0]+0.3, position[1], position[2]],
      [position[0], position[1], position[2]+0.3]]

   tree_indices = [
      [0,1,2],
      [0,1,3]]

   tree_norms = [[1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.]]

   return tree_verts, tree_norms, tree_indices

class Terrain:
   def __init__( self, length, breadth ):
      self.length = length
      self.breadth = breadth
      self.regen_arrays()
      
      pass

   def gen_row( self, row ):
      pass

   def gen_col( self, col ):
      pass
   
   def regen_arrays( self ):
      verts = []
      indices = []
      _current_index = 0

      for x in range(self.length):
         for z in range(self.breadth):
            verts.append( [x, terrainNoise( x,z, self.length, self.breadth ), z ] )
            if x >= 1 and z >= 1:
               indices.append( [ _current_index,
                                 _current_index - 1,
                                 _current_index - self.breadth ])
              #indices.append( [ _current_index - self.breadth - 1,
              #                  _current_index - 1,
              #                  _current_index - self.breadth ])
            _current_index += 1

         
      self.vert_array = array(verts, dtype=float32)
      self.index_array = array(indices, dtype=int32)

      norm_dict = {}
      #for face in index_array:
         #for vert_index in face:
            #if vert_index not in norm_dict:'kernel' has bad input: nil
               #norm_dict[vert_index] = []
            #norm_dict[vert_index].append(pyrr.vector.generate_normals(*vert_array[face]))

      self.norm_array = ones(self.vert_array.shape, dtype=float32)
      #for norm_index in range(len( norm_array ) ):
         #norm_array[norm_index] = pyrr.vector.normalise( sum(norm_dict[norm_index]) )

   def get_arrays( self ):
      return self.vert_array, self.norm_array, self.index_array

