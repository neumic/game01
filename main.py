from numpy import array
from numpy import float32
from numpy import random
import numpy

from OpenGL.GL import *
from OpenGL.arrays import vbo
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
from loaders import *
from terrain import Terrain

HEIGHT = 800
WIDTH = 1280

null = c_void_p(0) #handy trick from https://bitbucket.org/tartley/gltutpy/


pygame.init()
screen = pygame.display.set_mode( (WIDTH,HEIGHT),
   HWSURFACE|OPENGL|DOUBLEBUF|OPENGLBLIT )
pygame.mouse.set_visible( False )
pygame.event.set_grab( True ) 
pygame.display.toggle_fullscreen()
clock = pygame.time.Clock()
pygame.font.init()
fpsFont = pygame.font.Font( pygame.font.get_default_font(), 14 )

#glEnable( GL_CULL_FACE )
glEnable( GL_DEPTH_TEST )
glDepthFunc(GL_LESS)

glClearColor( 0.1, 0.1, 0.5, 0. )

programId = loadShaders( "shaders/simple.vertexshader",
                         "shaders/simple.fragmentshader" )
matrixId = glGetUniformLocation( programId, b'MVP' )
textureSamplerId = glGetUniformLocation( programId, b'textureSampler' )

camera = Camera(position = [9.0, -2.0, 9.0])

terrain = Terrain( 256, 256, numpy.copy(camera.position ) )
vert_array, norm_array, index_array = terrain.get_arrays()
vert_norm_vbo = vbo.VBO( numpy.concatenate( (vert_array, norm_array) ) )
index_vbo = vbo.VBO( index_array, target = GL_ELEMENT_ARRAY_BUFFER )

##Framebuffer rendering code
framebufferName = glGenFramebuffers(1)
glBindFramebuffer( GL_FRAMEBUFFER, framebufferName )

renderedTexture = glGenTextures(1)
glBindTexture( GL_TEXTURE_2D, renderedTexture )
glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB,
              HEIGHT, WIDTH, 0, GL_RGB, GL_UNSIGNED_BYTE, null )

glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )

depthTexture = glGenTextures(1)
glBindTexture( GL_TEXTURE_2D, depthTexture )
glTexImage2D( GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24,
             HEIGHT, WIDTH, 0,GL_DEPTH_COMPONENT, GL_FLOAT, null )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )

glFramebufferTexture2D( GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthTexture, 0)

glFramebufferTexture2D( GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, renderedTexture, 0)

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
subsecondStart = 0 #initialize the first second
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

   glEnableClientState(GL_VERTEX_ARRAY)
   glEnableClientState(GL_NORMAL_ARRAY)
   vert_norm_vbo.bind()
   index_vbo.bind()

   glVertexPointerf( vert_norm_vbo )
   glNormalPointerf( vert_norm_vbo + len(vert_array) )

   glDrawElements( GL_TRIANGLES, len(index_vbo.flat), GL_UNSIGNED_INT, index_vbo )

   vert_norm_vbo.unbind()
   index_vbo.unbind()
   glDisableClientState(GL_VERTEX_ARRAY)
   glDisableClientState(GL_NORMAL_ARRAY)

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
   #Every second stuff
   if time - secondStart > 1000:
      fps = frames * 1000 / (time - secondStart)
      secondStart = time
      frames = 0
      fpsDisplay = fpsFont.render( str(fps), False, (0,255,255) )


   if time - subsecondStart > 100:
      subsecondStart = time
      terrain.upshift_row( )
      vert_array = terrain.get_vert_array()
      vert_norm_vbo = vbo.VBO( numpy.concatenate( (vert_array, norm_array) ) )
      index_vbo = vbo.VBO( index_array, target = GL_ELEMENT_ARRAY_BUFFER )

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
