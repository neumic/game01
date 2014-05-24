def genTerrain( length, breadth):
   verts = []
   indices = []
   _current_index = 0

   for x in range(length):
      for z in range(breadth):
         verts.append( [x,   0.0, z, ] )
         if x >= 1 and z >= 1:
            indices.append( [ _current_index, _current_index - 1, _current_index - breadth ])
            indices.append( [ _current_index - breadth - 1, _current_index - 1, _current_index - breadth ])
         _current_index += 1


   vert_vbo = vbo.VBO( array(verts, dtype='f') )
   index_vbo = vbo.VBO( array(indices, dtype=numpy.int32), target = GL_ELEMENT_ARRAY_BUFFER )
   return vert_vbo, index_vbo
