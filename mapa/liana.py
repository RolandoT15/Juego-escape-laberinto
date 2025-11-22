import pygame
from mapa.constantes import VERDE_LIANA,TILE_SIZE

class Liana:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE,TILE_SIZE)
        self.color = VERDE_LIANA
        self.pasa_jugador = False
        self.pasa_enemigo = True

    def dibujar(self,superficie):
        pygame.draw.rect(superficie,VERDE_LIANA,self.rect)
        x,y = self.rect.x, self.rect.y
        w = TILE_SIZE
        pygame.draw.line(superficie,self.color,(x + 10, y), (x + 10, y + w), 3)
        pygame.draw.line(superficie, self.color, (x + 20, y), (x + 20, y + w), 3)
        pygame.draw.line(superficie, self.color, (x + 30, y), (x + 30, y + w), 3)



