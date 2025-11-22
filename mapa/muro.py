import pygame
from mapa.constantes import TILE_SIZE, GRIS_PIEDRA,NEGRO


class Muro:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = GRIS_PIEDRA

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        pygame.draw.rect(superficie, NEGRO, self.rect, 1)