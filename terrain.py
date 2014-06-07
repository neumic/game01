import noise
import pyrr
from OpenGL.arrays import vbo
from numpy import array, float32, int32, zeros, ones, transpose, concatenate, vstack
from math import floor
import random

def terrainNoise( x, z, length, breadth):
   return 128 * noise.pnoise2(x/length,z/breadth, octaves=3)
   #return 0.0

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

      
   trees = genTrees( length, breadth, 2400)
   
   offset = len(verts)
   verts += trees[0]
   vert_array = array(verts, dtype=float32)
   for face in trees[2]:
      indices.append(list( map( lambda x: x + offset, face ) ) )
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
      trees = genTree( array([ x, terrainNoise( x, z, length, breadth) - 1, z]))
      for face in trees[2]:
         tree_indices.append(list( map( lambda x: x + len(tree_verts), face ) ))
      tree_verts += trees[0]
      tree_norms += trees[1]

   return tree_verts, tree_norms, tree_indices
   
def genTree( position ):
   height = random.random() * 40 + 10
   tree_verts = [
      [position[0], position[1], position[2]],
      [position[0], position[1] + height, position[2]],
      [position[0]+0.3, position[1], position[2]],
      [position[0], position[1], position[2]+0.3],

      [position[0], position[1], position[2]],
      [position[0], position[1] + height, position[2]],
      [position[0]-random.random(), position[1] + height, position[2]],
      [position[0], position[1] + height, position[2]-random.random()]]

   tree_indices = [
      [0,1,2],
      [0,1,3],
      [4,5,6],
      [4,5,7]]

   tree_norms = [[1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.],
                 [1.,1.,1.]]

   return tree_verts, tree_norms, tree_indices

class Terrain:
   def __init__( self, length, breadth, center ):
      self.length = length
      self.breadth = breadth
      self.center = center
      self.regen_arrays()
      

   def upshift_row( self ):
      new_row = array( [self.gen_row_verts( self.max_x )], dtype=float32 )
      self.max_x += 1
      self.vert_array = vstack( (self.vert_array[1:], new_row) )

   def downshift_row( self, row ):
      pass

   def shift_col( self, col ):
      pass
    
   def recenter( self, center ):
      rows = []
      zDifference = floor( center[2] - self.center[2] )
      for row in range( zDifference ):
         pass
         
   def gen_row_verts( self, row_x ):
      row_vertices = []
      row_indices = []
      _current_index = 0
      zOffset = floor( -self.center[2] - self.breadth / 2 )
      for z in range(zOffset, self.breadth + zOffset):
         row_vertices.append( [row_x, terrainNoise( row_x,z, self.length, self.breadth ), z ] )
      
      return row_vertices 

   def regen_arrays( self ):
      verts = []
      indices = []
      _current_index = 0
      xOffset = floor( -self.center[0] - self.length / 2 )
      zOffset = floor( -self.center[2] - self.breadth / 2 )
      self.max_x = self.length + xOffset

      for x in range(xOffset, self.length + xOffset):
         row_vertices = self.gen_row_verts( x )
         verts.append( row_vertices )
         for z in range(zOffset, self.breadth + zOffset):
            if z > zOffset and x > xOffset:
               indices.append( [ _current_index,
                                 _current_index - 1,
                                 _current_index - self.breadth ])
               indices.append( [ _current_index - self.breadth - 1,
                                 _current_index - 1,
                                 _current_index - self.breadth ])
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

   def get_vert_array( self ):
      return self.vert_array

