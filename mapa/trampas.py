import pygame
import time
from mapa.constantes import TILE_SIZE, NEGRO, BLANCO


class Trampa:
    def __init__(self, x, y):
        """
        Inicializa una trampa en la posición (x, y) del mapa.

        Args:
            x: Posición en columnas (coordenada horizontal)
            y: Posición en filas (coordenada vertical)
        """
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = BLANCO  # Color base de la trampa
        self.color_borde = NEGRO  # Color del borde
        self.activa = True  # Estado de la trampa (activa/desactivada)
        self.tiempo_creacion = time.time()  # Momento en que se creó la trampa
        self.pasa_jugador = True  # El jugador puede pasar por encima sin efecto
        self.pasa_enemigo = True  # El enemigo puede pasar por encima (pero será eliminado)

    def dibujar(self, superficie):
        """
        Dibuja la trampa en la superficie indicada.

        Args:
            superficie: La superficie de pygame donde se dibujará la trampa
        """
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
        """Desactiva la trampa (después de atrapar a un cazador)"""
        self.activa = False