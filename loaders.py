import pygame
from OpenGL.GL import *
from numpy import array, float32

def loadOBJ(filename):
#Loads an obj file and spits out numpy arrays with the vertices, UV coords, and normals
   numVerts = 0
   verts = []
   uvs   = []
   norms = []
   vertsOut = []
   uvsOut   = []
   normsOut = []
   for line in open(filename, "r"):
      vals = line.split()
      if vals[0] == "v":
         v = list(map(float, vals[1:4]))
         verts.append(v)
      elif vals[0] == "vt":
         n = list(map(float, vals[1:3]))
         uvs.append(n)
      elif vals[0] == "vn":
         n = list(map(float, vals[1:4]))
         norms.append(n)
      elif vals[0] == "f":
         for f in vals[1:]:
            w = f.split("/")
            # OBJ Files are 1-indexed so we must subtract 1 below
            vertsOut.append(list(verts[int(w[0])-1]))
            uvsOut.append(list(uvs[int(w[1])-1]))
            normsOut.append(list(norms[int(w[2])-1]))
            numVerts += 1
   return array(vertsOut, dtype=float32), array(uvsOut, dtype=float32), array(normsOut)

def loadShaders(vertFile, fragFile):
#loads and compiles the given shaders and returns the ID of the comiled program
   vertexShaderId = glCreateShader(GL_VERTEX_SHADER)
   fragmentShaderId = glCreateShader(GL_FRAGMENT_SHADER)

   with open( vertFile ) as f:
      vertexShaderSource = f.read()
      
   with open( fragFile ) as f:
      fragmentShaderSource = f.read()

   glShaderSource(vertexShaderId, vertexShaderSource )
   glCompileShader(vertexShaderId)
   log = glGetShaderInfoLog(vertexShaderId)
   if log: print('Vertex Shader: ', log)

   glShaderSource(fragmentShaderId, fragmentShaderSource )
   glCompileShader(fragmentShaderId)
   log = glGetShaderInfoLog(fragmentShaderId)
   if log: print('Fragment Shader: ', log)

   programId = glCreateProgram()
   glAttachShader(programId, vertexShaderId)
   glAttachShader(programId, fragmentShaderId)
   glLinkProgram(programId)

   log = glGetProgramInfoLog(programId)
   if log: print('Linked Program: ', log)

   glDeleteShader( vertexShaderId )
   glDeleteShader( fragmentShaderId )
   
   return programId


def loadBMP( filename ):
#loads a BMP and stores it in a texture buffer
   texture = pygame.surfarray.array3d(pygame.image.load(filename) )
   textureId = glGenTextures(1)
   glBindTexture( GL_TEXTURE_2D, textureId )
   glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, texture.shape[0], texture.shape[1], 0, GL_RGB, GL_UNSIGNED_BYTE, texture)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
   glGenerateMipmap(GL_TEXTURE_2D)
   return textureId
