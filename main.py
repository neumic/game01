from numpy import array
from numpy import float32

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from pyrr import matrix44 as mat4
from pyrr import vector

import pygame
from pygame.locals import *

from ctypes import c_void_p

import math

from command import *
from camera  import Camera

HEIGHT = 512
WIDTH = 512

null = c_void_p(0)

def loadOBJ(filename):
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
   texture = pygame.surfarray.array3d(pygame.image.load(filename) )
   textureId = glGenTextures(1)
   glBindTexture( GL_TEXTURE_2D, textureId )
   glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, texture.shape[0], texture.shape[1], 0, GL_RGB, GL_UNSIGNED_BYTE, texture)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
   glGenerateMipmap(GL_TEXTURE_2D)
   return textureId
   

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT), HWSURFACE|OPENGL|DOUBLEBUF|OPENGLBLIT)
pygame.mouse.set_visible( False )
pygame.event.set_grab( True ) 
#pygame.display.toggle_fullscreen()
clock = pygame.time.Clock()
pygame.font.init()
fpsFont = pygame.font.Font( pygame.font.get_default_font(), 14 )

#glEnable( GL_CULL_FACE )
glEnable( GL_DEPTH_TEST )
glDepthFunc(GL_LESS)

glClearColor( 0.1, 0.1, 0.5, 0. )

programId = loadShaders( "shaders/simple.vertexshader", "shaders/simple.fragmentshader" )
matrixId = glGetUniformLocation( programId, b'MVP' )
textureSamplerId = glGetUniformLocation( programId, b'textureSampler' )


verts, uvs, norms = loadOBJ( "objects/suzanne.obj" )

vertBuffer = glGenBuffers(1)
glBindBuffer( GL_ARRAY_BUFFER, vertBuffer )
glBufferData( GL_ARRAY_BUFFER, verts, GL_STATIC_DRAW )

UVBuffer = glGenBuffers(1)
glBindBuffer( GL_ARRAY_BUFFER, UVBuffer )
glBufferData( GL_ARRAY_BUFFER, uvs, GL_STATIC_DRAW )

normBuffer = glGenBuffers(1)
glBindBuffer( GL_ARRAY_BUFFER, normBuffer )
glBufferData( GL_ARRAY_BUFFER, norms, GL_STATIC_DRAW )

##Framebuffer rendering code
framebufferName = glGenFramebuffers(1)
glBindFramebuffer( GL_FRAMEBUFFER, framebufferName )

renderedTexture = glGenTextures(1)
glBindTexture( GL_TEXTURE_2D, renderedTexture )
glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, null)

glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )

depthTexture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, depthTexture)
glTexImage2D(GL_TEXTURE_2D, 0,GL_DEPTH_COMPONENT24, HEIGHT, WIDTH, 0,GL_DEPTH_COMPONENT, GL_FLOAT, null)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthTexture, 0)

glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, renderedTexture, 0)

drawBuffers = [GL_COLOR_ATTACHMENT0]
glDrawBuffers(1, drawBuffers)

if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
   print("framebuffer incomplete")
   sys.exit()

quad_verts = array([
		-1.0, -1.0, 0.0,
		 1.0, -1.0, 0.0,
		-1.0,  1.0, 0.0,
		-1.0,  1.0, 0.0,
		 1.0, -1.0, 0.0,
		 1.0,  1.0, 0.0], dtype=float32)

quadVertBuffer = glGenBuffers(1)
glBindBuffer( GL_ARRAY_BUFFER, quadVertBuffer )
glBufferData(GL_ARRAY_BUFFER, quad_verts, GL_STATIC_DRAW)

quad_programId = loadShaders( "shaders/Passthrough.vertexshader", "shaders/edgeDetect.fragmentshader" )
quad_vertexPosition_modelspace = glGetAttribLocation(quad_programId, b'vertexPosition_modelspace');
texID = glGetUniformLocation(quad_programId, b'renderedTexture');
timeID = glGetUniformLocation(quad_programId, b'time');


vertexPosition_modelspaceID = glGetAttribLocation(programId, b'vertexPosition_modelspace')
vertexUVId = glGetAttribLocation(programId, b'vertexUV')

textureId = loadBMP( "textures/uvtemplate.bmp" )

camera = Camera()

inputHandler = InputHandler()
inputHandler.keyBind( K_ESCAPE, quit )
inputHandler.keyBind( K_w, camera.moveForward )
inputHandler.keyBind( K_s, camera.moveBackward )
inputHandler.keyBind( K_a, camera.moveLeft )
inputHandler.keyBind( K_d, camera.moveRight )
inputHandler.mouseMoveBind( camera.addRotations )

####FPS METER STUFF
frames = 0 # counter for calculating fps
secondStart = 0 #initialize the first second
fpsDisplay = fpsFont.render( str(0), False, (0,255,255) )

while True:
   inputHandler.handleInput()
   
   glBindFramebuffer(GL_FRAMEBUFFER, framebufferName);
   glViewport(0,0,HEIGHT,WIDTH)
   glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

   glUseProgram( programId )

   timePassed = clock.tick()

   camera.regenProjectionMatrix()
   projection = camera.getProjectionMatrix()
   camera.regenViewMatrix()
   view = camera.getViewMatrix()
   model = array(mat4.create_identity(), dtype=float32)
   MVP = array( mat4.multiply(mat4.multiply(model, view), projection ), dtype=float32)

   glUniformMatrix4fv( matrixId, 1, GL_FALSE, MVP )
   glActiveTexture(GL_TEXTURE0)
   glBindTexture(GL_TEXTURE_2D, textureId)
   glUniform1i(textureSamplerId, 0);

   glBindBuffer(GL_ARRAY_BUFFER, vertBuffer)
   glEnableVertexAttribArray(vertexPosition_modelspaceID)
   glVertexAttribPointer( vertexPosition_modelspaceID, 3, GL_FLOAT, GL_FALSE, 0, null )

   glEnableVertexAttribArray(1)
   glBindBuffer(GL_ARRAY_BUFFER, UVBuffer)
   glVertexAttribPointer( vertexUVId, 2, GL_FLOAT, GL_FALSE, 0, null )

   glEnableVertexAttribArray(2)
   glBindBuffer( GL_ARRAY_BUFFER, normBuffer )
   glVertexAttribPointer( 2, 3, GL_FLOAT, GL_FALSE, 0, null )

   glDrawArrays( GL_TRIANGLES, 0, len( verts ) )
   glDisableVertexAttribArray(vertexPosition_modelspaceID)
   glDisableVertexAttribArray( vertexUVId )

###DRAWING THE FULL SCREEN QUAD
   glBindFramebuffer(GL_FRAMEBUFFER, 0)
   glViewport(0,0,HEIGHT,WIDTH)

   glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

   glUseProgram(quad_programId)

   glActiveTexture(GL_TEXTURE0)
   glBindTexture(GL_TEXTURE_2D, depthTexture)
   glUniform1i(texID, 0)

   glEnableVertexAttribArray(0);
   glBindBuffer(GL_ARRAY_BUFFER, quadVertBuffer)
   glVertexAttribPointer( quad_vertexPosition_modelspace, 3, GL_FLOAT, GL_FALSE, 0, null)
####FPS METER STUFF
   frames += 1
   time = pygame.time.get_ticks()
   if time - secondStart > 1000:
      fps = frames * 1000 / (time - secondStart)
      secondStart = time
      frames = 0
      fpsDisplay = fpsFont.render( str(fps), False, (0,255,255) )

   glViewport(0,0, WIDTH, HEIGHT )
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   glOrtho(0.0, WIDTH - 1.0, 0.0, HEIGHT - 1.0, -1.0, 1.0)
   glMatrixMode(GL_MODELVIEW)
   glLoadIdentity()
   glPushMatrix()
   glRasterPos2i(0,0)
   rw, rh = fpsDisplay.get_size()
   glDrawPixels(rw, rh, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring( fpsDisplay, 'RGBA', 1))
   glPopMatrix()

   glDrawArrays(GL_TRIANGLES, 0, 6)

   glDisableVertexAttribArray(0)

   pygame.display.flip()
