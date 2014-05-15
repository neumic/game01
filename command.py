import pygame
from pygame.locals import *

class InputHandler:
   def __init__( self ):
      pygame.init() #Safe to call more than once
      self.bindings = {}

   def handleInput( self ):
      for event in pygame.event.get():
         print(event)
         if event.type == KEYDOWN:
            print( event.key )
            if event.key in self.bindings:
               self.bindings[event.key]()
         elif event.type == QUIT:
            exit()

   def keyBind( self, key, function ):
      #TODO: add sanity checks on the inputs
      self.bindings[key] = function

