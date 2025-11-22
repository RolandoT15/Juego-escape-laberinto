import pygame
from mapa.constantes import  TILE_SIZE, VERDE_OSCURO

class Suelo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = VERDE_OSCURO

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)

