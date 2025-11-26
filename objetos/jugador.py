import pygame
from mapa.constantes import TILE_SIZE

#hola

class Jugador:
    def __init__(self, x, y):
        # Posición en la grilla (columnas, filas)
        self.x = x
        self.y = y
        # Rectángulo para dibujar y color (Verde)
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = (0, 255, 0)

    def mover(self, dx, dy, mapa_objetos):
        """
        Intenta mover al jugador.
        dx: cambio en x (-1, 0, 1)
        dy: cambio en y (-1, 0, 1)
        mapa_objetos: la matriz de objetos para chequear colisiones
        """
        nueva_x = self.x + dx
        nueva_y = self.y + dy

        # Verificamos que no se salga de los límites de la matriz (seguridad)
        if 0 <= nueva_y < len(mapa_objetos) and 0 <= nueva_x < len(mapa_objetos[0]):

            # Obtenemos el objeto que está en la posición a la que queremos ir
            # Nota: mapa_objetos se accede como [fila][columna] -> [y][x]
            objeto_destino = mapa_objetos[nueva_y][nueva_x]

            # Verificamos la propiedad 'pasa_jugador' del objeto (Muro, Suelo, etc.)
            if objeto_destino.pasa_jugador:
                self.x = nueva_x
                self.y = nueva_y

                # Actualizamos la posición visual (pixeles)
                self.rect.x = self.x * TILE_SIZE
                self.rect.y = self.y * TILE_SIZE

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        # Dibujamos un borde negro pequeño para resaltar
        pygame.draw.rect(superficie, (0, 0, 0), self.rect, 1)