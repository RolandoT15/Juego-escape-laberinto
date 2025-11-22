import pygame
from mapa.constantes import TILE_SIZE, MARRON_TUNEL,NEGRO

class Tunel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = MARRON_TUNEL
        self.pasa_jugador = True
        self.pasa_enemigo = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        pygame.draw.circle(superficie, NEGRO, self.rect.center, 12)