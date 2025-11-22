import pygame
import random
import sys
from mapa.muro import Muro
from mapa.suelo import Suelo
from mapa.constantes import FILAS, COLUMNAS,ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE, COLUMNAS, FILAS,AZUL_META, ROJO_INICIO, NEGRO,BLANCO
from mapa.liana import Liana
from mapa.tunel import Tunel

# lOGICA
class Inicio:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = ROJO_INICIO
        self.pasa_jugador = True
        self.pasa_enemigo = True

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)


class Meta:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = AZUL_META
        self.pasa_jugador = True
        self.pasa_enemigo = True

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        pygame.draw.circle(superficie, BLANCO, self.rect.center, 5)


class GeneradorMapa:
    def __init__(self,filas,columnas):
        self.filas = filas
        self.columnas = columnas
        self.mapa_objetos = []
        self.inicio = (1,1)
        self.meta = (self.columnas - 2, self.filas - 2)

        self.generar()

    def generar(self):
        self.mapa_objetos = []

        for f in range(self.filas):
            fila_objs = []
            for c in range(self.columnas):
                if f == 0 or f == self.filas - 1 or c == 0 or c == self.columnas - 1:
                    fila_objs.append(Muro(c, f))
                else:
                    azar = random.random()

                    if azar < 0.35:
                        fila_objs.append(Muro(c, f))
                    elif azar < 0.40:
                        fila_objs.append(Liana(c, f))
                    elif azar < 0.45:
                        fila_objs.append(Tunel(c, f))
                    else:
                        fila_objs.append(Suelo(c, f))

            self.mapa_objetos.append(fila_objs)

        # Puntos de inicio y final
        ix, iy = self.inicio
        mx,my = self.meta
        self.mapa_objetos[iy][ix] = Inicio(ix,iy)
        self.mapa_objetos[my][mx] = Meta(mx,my)

        self.crear_camino_garantizado()

    def crear_camino_garantizado(self):
        x, y = self.inicio
        mx,my = self.meta

        # Busca del inicio al objetivo
        while (x,y) != (mx, my):
            moves = []

            # Direcciones donde se mueve el algoritmo, buscando la menor distancia
            if x < mx: moves.append((1, 0))
            if x > mx: moves.append((-1, 0))
            if y < my: moves.append((0, 1))
            if y > my: moves.append((0, -1))

            if not moves: break

            #Elegir una dirección
            dx, dy = random.choice(moves)
            x += dx
            y += dy

            # Si las coordenadas donde se esta no es la meta, usar el objeto de suelo
            if (x,y) != (mx,my):

                objeto_actual = self.mapa_objetos[y][x]

                if not objeto_actual.pasa_jugador:
                    self.mapa_objetos[y][x] = Suelo(x,y)



pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Mapa Garantizado")
reloj = pygame.time.Clock()

generador = GeneradorMapa(FILAS, COLUMNAS)

ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                generador.generar()

    pantalla.fill(NEGRO)

    for fila in generador.mapa_objetos:
        for objeto in fila:
            objeto.dibujar(pantalla)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()