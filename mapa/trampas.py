import pygame
import time
from mapa.constantes import TILE_SIZE, NEGRO, BLANCO


class Trampa:
    def __init__(self, x, y):

        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = BLANCO
        self.color_borde = NEGRO
        self.activa = True
        self.tiempo_creacion = time.time()
        self.pasa_jugador = True
        self.pasa_enemigo = True

    def dibujar(self, superficie):

        if self.activa:
            # Dibujar base de la trampa
            pygame.draw.rect(superficie, self.color, self.rect)

            # Dibujar patrón de la trampa (forma de X)
            x, y = self.rect.topleft
            width, height = self.rect.width, self.rect.height

            # Dibujar líneas en X
            pygame.draw.line(superficie, self.color_borde, (x, y), (x + width, y + height), 2)
            pygame.draw.line(superficie, self.color_borde, (x + width, y), (x, y + height), 2)

            # Dibujar borde
            pygame.draw.rect(superficie, self.color_borde, self.rect, 2)

    def desactivar(self):
        self.activa = False