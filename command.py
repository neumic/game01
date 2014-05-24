import pygame
from pygame.locals import *

class InputHandler:
   def __init__( self ):
      pygame.init() #Safe to call more than once
      self.keyBindings = {}
      self.mouseMoveBinding = None
      pygame.key.set_repeat(True)

   def handleInput( self ):
      for event in pygame.event.get():
         #print(event)
         if event.type == KEYDOWN:
            if event.key in self.keyBindings:
               self.keyBindings[event.key]()
         elif event.type == MOUSEMOTION:
            #TODO: sum relative mouse movement per call 
            if self.mouseMoveBinding is not None:
               self.mouseMoveBinding( *event.rel )
         elif event.type == QUIT:
            exit()

   def keyBind( self, key, function ):
      #TODO: add sanity checks on the inputs
      self.keyBindings[key] = function

   def mouseMoveBind(self, function ):
      #TODO: add sanity checks on the inputs
      self.mouseMoveBinding = function

