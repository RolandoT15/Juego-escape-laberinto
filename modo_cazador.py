import pygame
import random
import sys
import math
import time

from mapa.muro import Muro
from mapa.suelo import Suelo
from mapa.constantes import FILAS, COLUMNAS, ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE, AZUL_META, ROJO_INICIO, NEGRO, \
    BLANCO
from mapa.liana import Liana
from mapa.tunel import Tunel
from menus.configuracion import VERDE, ROJO, AMARILLO


# ---------------------------
# CLASES (Se mantienen igual)
# ---------------------------
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
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.mapa_objetos = []
        self.inicio = (1, 1)
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
        ix, iy = self.inicio
        mx, my = self.meta
        self.mapa_objetos[iy][ix] = Inicio(ix, iy)
        self.mapa_objetos[my][mx] = Meta(mx, my)
        self.crear_camino_garantizado()

    def crear_camino_garantizado(self):
        x, y = self.inicio
        mx, my = self.meta
        while (x, y) != (mx, my):
            moves = []
            if x < mx: moves.append((1, 0))
            if x > mx: moves.append((-1, 0))
            if y < my: moves.append((0, 1))
            if y > my: moves.append((0, -1))
            if not moves: break
            dx, dy = random.choice(moves)
            x += dx
            y += dy
            if (x, y) != (mx, my):
                objeto_actual = self.mapa_objetos[y][x]
                if not getattr(objeto_actual, 'pasa_jugador', False):
                    self.mapa_objetos[y][x] = Suelo(x, y)


# Variable global para que las funciones auxiliares la vean
generador = None


# ---------------------------
# UTILIDADES
# ---------------------------
def tile_coords_from_rect(rect):
    left = rect.left // TILE_SIZE
    right = rect.right // TILE_SIZE
    top = rect.top // TILE_SIZE
    bottom = rect.bottom // TILE_SIZE
    coords = []
    for ty in range(top, bottom + 1):
        for tx in range(left, right + 1):
            coords.append((tx, ty))
    return coords


def tile_at(tx, ty):
    if generador and 0 <= ty < generador.filas and 0 <= tx < generador.columnas:
        return generador.mapa_objetos[ty][tx]
    return None


def is_passable_for_player(tx, ty):
    t = tile_at(tx, ty)
    return t is not None and getattr(t, 'pasa_jugador', False)


def is_passable_for_enemy(tx, ty):
    t = tile_at(tx, ty)
    return t is not None and getattr(t, 'pasa_enemigo', False)


def world_pos_center_of_tile(tx, ty):
    return (tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2)


def can_move_rect(rect, dx, dy, for_enemy=False):
    new_rect = rect.copy()
    new_rect.x += int(round(dx))
    new_rect.y += int(round(dy))
    left = max(0, new_rect.left // TILE_SIZE)
    right = min(generador.columnas - 1, (new_rect.right - 1) // TILE_SIZE)
    top = max(0, new_rect.top // TILE_SIZE)
    bottom = min(generador.filas - 1, (new_rect.bottom - 1) // TILE_SIZE)
    for ty in range(top, bottom + 1):
        for tx in range(left, right + 1):
            if for_enemy:
                if not is_passable_for_enemy(tx, ty): return False
            else:
                if not is_passable_for_player(tx, ty): return False
    return True


def push_back_entities(rect_a, rect_b):
    if not rect_a.colliderect(rect_b): return
    dx = rect_b.centerx - rect_a.centerx
    dy = rect_b.centery - rect_a.centery
    if dx == 0 and dy == 0: dx = 1
    dist = math.hypot(dx, dy)
    overlap = (rect_a.width / 2 + rect_b.width / 2) - dist
    if dist != 0 and overlap > 0:
        dx /= dist
        dy /= dist
        rect_b.x += int(dx * (overlap / 2))
        rect_b.y += int(dy * (overlap / 2))
        rect_a.x -= int(dx * (overlap / 2))
        rect_a.y -= int(dy * (overlap / 2))


# ---------------------------
# FUNCIÓN PRINCIPAL DEL JUEGO
# ---------------------------
def ejecutar_juego(pantalla, nombre_jugador):
    global generador  # Usamos la global para que las funciones auxiliares funcionen

    reloj = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)  # Fuente para el HUD

    # Reiniciar generador para nueva partida
    generador = GeneradorMapa(FILAS, COLUMNAS)

    # Configuración de Entidades
    PLAYER_SIZE = max(4, TILE_SIZE - 6)
    ENEMY_SIZE = max(4, TILE_SIZE - 10)
    player_speed_walk = 2.8
    player_speed_run = 5.0
    player_color = (50, 150, 255)

    energy = 100.0
    max_energy = 100.0
    energy_bar_width = 20
    energy_bar_height = min(ALTO_VENTANA - 40, 300)
    energy_recovery = 0.25
    energy_consumption = 0.9
    enemy_speed = 1.8  # Ajustar velocidad de enemigos

    # Inicializar jugador
    player_x = 0.0
    player_y = 0.0
    found_inicio = False
    for y in range(generador.filas):
        for x in range(generador.columnas):
            obj = generador.mapa_objetos[y][x]
            if obj.__class__.__name__ == 'Inicio':
                cx, cy = world_pos_center_of_tile(x, y)
                player_x, player_y = cx - PLAYER_SIZE / 2, cy - PLAYER_SIZE / 2
                found_inicio = True
                break
        if found_inicio: break

    if not found_inicio:
        player_x = ANCHO_VENTANA // 2 - PLAYER_SIZE / 2
        player_y = ALTO_VENTANA // 2 - PLAYER_SIZE / 2

    # Inicializar enemigos
    enemies = []
    spawns = []
    for y in range(generador.filas):
        for x in range(generador.columnas):
            t = generador.mapa_objetos[y][x]
            if getattr(t, 'pasa_enemigo', False) and t.__class__.__name__ not in ('Inicio', 'Meta'):
                spawns.append((x, y))

    random.shuffle(spawns)
    num_enemies = 4
    for i in range(min(num_enemies, len(spawns))):
        tx, ty = spawns[i]
        cx, cy = world_pos_center_of_tile(tx, ty)
        ex = cx - ENEMY_SIZE / 2
        ey = cy - ENEMY_SIZE / 2
        enemies.append({
            'x': float(ex), 'y': float(ey),
            'spawn_tx': tx, 'spawn_ty': ty,
            'visible': True,
            'respawn_time': 0.0
        })

    running = True
    puntos = 0
    ultimo_mensaje_puntos = ""
    color_mensaje_puntos = BLANCO
    tiempo_mensaje = 0

    while running:
        dt = reloj.tick(60) / 1000.0
        now = time.time()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
                return puntos

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    # Lógica de reinicio dentro del juego
                    generador.generar()
                    # Reposicionar jugador
                    found = False
                    for y in range(generador.filas):
                        for x in range(generador.columnas):
                            obj = generador.mapa_objetos[y][x]
                            if obj.__class__.__name__ == 'Inicio':
                                cx, cy = world_pos_center_of_tile(x, y)
                                player_x, player_y = cx - PLAYER_SIZE / 2, cy - PLAYER_SIZE / 2
                                found = True
                                break
                        if found: break
                    # Reposicionar enemigos
                    spawns = []
                    for y in range(generador.filas):
                        for x in range(generador.columnas):
                            t = generador.mapa_objetos[y][x]
                            if getattr(t, 'pasa_enemigo', False) and t.__class__.__name__ not in ('Inicio', 'Meta'):
                                spawns.append((x, y))
                    random.shuffle(spawns)
                    enemies = []
                    for i in range(min(num_enemies, len(spawns))):
                        tx, ty = spawns[i]
                        cx, cy = world_pos_center_of_tile(tx, ty)
                        ex = cx - ENEMY_SIZE / 2
                        ey = cy - ENEMY_SIZE / 2
                        enemies.append({'x': float(ex), 'y': float(ey), 'spawn_tx': tx, 'spawn_ty': ty, 'visible': True,
                                        'respawn_time': 0.0})

        # --- Lógica de movimiento ---
        keys = pygame.key.get_pressed()
        speed = player_speed_walk
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and energy > 0:
            speed = player_speed_run
            energy -= energy_consumption
            if energy < 0: energy = 0.0
        else:
            energy += energy_recovery
            if energy > max_energy: energy = max_energy

        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += speed

        if dx != 0 and dy != 0:
            inv = 1 / math.sqrt(2)
            dx *= inv
            dy *= inv

        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)

        # Movimiento Jugador
        if dx != 0:
            if can_move_rect(player_rect, dx, 0, for_enemy=False):
                player_rect.x += int(round(dx))
            else:
                step = int(math.copysign(1, dx))
                for i in range(abs(int(round(dx)))):
                    if can_move_rect(player_rect, step, 0, for_enemy=False):
                        player_rect.x += step
                    else:
                        break
        if dy != 0:
            if can_move_rect(player_rect, 0, dy, for_enemy=False):
                player_rect.y += int(round(dy))
            else:
                step = int(math.copysign(1, dy))
                for i in range(abs(int(round(dy)))):
                    if can_move_rect(player_rect, 0, step, for_enemy=False):
                        player_rect.y += step
                    else:
                        break

        player_x, player_y = float(player_rect.x), float(player_rect.y)

        # -----------------------------------------------------------------
        # MODIFICACIÓN: MOVIMIENTO DE ENEMIGOS HACIA LA META
        # -----------------------------------------------------------------

        # 1. Obtener coordenadas del centro de la meta en pixeles
        meta_col, meta_row = generador.meta
        meta_x, meta_y = world_pos_center_of_tile(meta_col, meta_row)

        for e in enemies:
            if not e['visible']:
                if now >= e['respawn_time']:
                    # Reaparecer en su spawn original
                    stx, sty = e['spawn_tx'], e['spawn_ty']
                    cx, cy = world_pos_center_of_tile(stx, sty)
                    e['x'] = cx - ENEMY_SIZE / 2
                    e['y'] = cy - ENEMY_SIZE / 2
                    e['visible'] = True
                continue

            ex = e['x']
            ey = e['y']

            # 2. Calcular vector hacia la META (meta_x/y - enemigo_x/y)
            vdx = meta_x - ex
            vdy = meta_y - ey

            dist = math.hypot(vdx, vdy)

            # 3. Detectar si el enemigo llegó a la meta
            # Si la distancia al centro es menor a medio tile, consideramos que llegó
            if dist < TILE_SIZE / 2:
                # Enemigo llegó a la meta -> Restar puntos
                puntos -= 150

                if puntos < 0:
                    puntos = 0
                    running = False
                    break

                ultimo_mensaje_puntos = "-100 (Escape)"
                color_mensaje_puntos = ROJO
                tiempo_mensaje = now

                # Desaparecer y programar respawn
                e['visible'] = False
                e['respawn_time'] = now + 2.0  # Reaparece rápido
                e['x'] = -1000.0
                e['y'] = -1000.0
                continue

            if dist == 0:
                dist = 1.0

            vdx /= dist
            vdy /= dist

            desired_dx = vdx * enemy_speed
            desired_dy = vdy * enemy_speed

            enemy_rect = pygame.Rect(int(ex), int(ey), ENEMY_SIZE, ENEMY_SIZE)

            # Lógica de movimiento con "deslizamiento" en paredes
            if can_move_rect(enemy_rect, desired_dx, desired_dy, for_enemy=True):
                enemy_rect.x += int(round(desired_dx))
                enemy_rect.y += int(round(desired_dy))
            else:
                if can_move_rect(enemy_rect, desired_dx, 0, for_enemy=True):
                    enemy_rect.x += int(round(desired_dx))
                elif can_move_rect(enemy_rect, 0, desired_dy, for_enemy=True):
                    enemy_rect.y += int(round(desired_dy))
                else:
                    # Intentos aleatorios para desatascarse
                    attempts = [(desired_dy, desired_dx), (-desired_dx, -desired_dy),
                                (desired_dx, -desired_dy), (-desired_dx, desired_dy),
                                (enemy_speed, 0), (-enemy_speed, 0), (0, enemy_speed), (0, -enemy_speed)]
                    for ax, ay in attempts:
                        if can_move_rect(enemy_rect, ax, ay, for_enemy=True):
                            enemy_rect.x += int(round(ax))
                            enemy_rect.y += int(round(ay))
                            break
            e['x'] = float(enemy_rect.x)
            e['y'] = float(enemy_rect.y)

        # Colisiones entre enemigos (empuje)
        enemy_rects = []
        for e in enemies:
            enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))

        for i in range(len(enemy_rects)):
            for j in range(i + 1, len(enemy_rects)):
                push_back_entities(enemy_rects[i], enemy_rects[j])

        # -----------------------------------------------------------------
        # MODIFICACIÓN: COLISIÓN JUGADOR VS ENEMIGO (CAZA)
        # -----------------------------------------------------------------
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)

        for idx, er in enumerate(enemy_rects):
            push_back_entities(player_rect, er)

            # Si el jugador toca un enemigo visible
            if player_rect.colliderect(er) and enemies[idx]['visible']:
                # Puntos para el jugador
                puntos += 50
                ultimo_mensaje_puntos = "+50 (Atrapado)"
                color_mensaje_puntos = VERDE
                tiempo_mensaje = now

                # Enemigo capturado -> Respawn
                enemies[idx]['visible'] = False
                enemies[idx]['respawn_time'] = now + 4.0  # Tarda un poco más en volver
                enemies[idx]['x'] = -1000.0
                enemies[idx]['y'] = -1000.0

        # Actualizar posiciones post-física
        player_x, player_y = float(player_rect.x), float(player_rect.y)
        for i, r in enumerate(enemy_rects):
            enemies[i]['x'], enemies[i]['y'] = float(r.x), float(r.y)

        # --- DIBUJADO ---
        pantalla.fill(NEGRO)
        for fila in generador.mapa_objetos:
            for objeto in fila:
                objeto.dibujar(pantalla)

        # Dibujar jugador
        pygame.draw.rect(pantalla, player_color, (int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE))

        # Dibujar enemigos
        for e in enemies:
            if e['visible']:
                pygame.draw.rect(pantalla, (255, 50, 50), (int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))

        # HUD: Barra de energía
        pygame.draw.rect(pantalla, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))
        current_height = int((energy / max_energy) * energy_bar_height)
        pygame.draw.rect(pantalla, (0, 200, 0),
                         (10, 20 + (energy_bar_height - current_height), energy_bar_width, current_height))

        # HUD: Puntuación
        texto_puntos = font.render(f"Puntos: {puntos}", True, BLANCO)
        pantalla.blit(texto_puntos, (ANCHO_VENTANA - 150, 20))

        texto_info = font.render("¡Caza a los enemigos!", True, AMARILLO)
        pantalla.blit(texto_info, (ANCHO_VENTANA - 220, 50))

        # Mensaje flotante de puntos (+500 / -100)
        if now - tiempo_mensaje < 1.0:  # Mostrar por 1 segundo
            msg_surf = font.render(ultimo_mensaje_puntos, True, color_mensaje_puntos)
            pantalla.blit(msg_surf, (ANCHO_VENTANA - 180, 80))

        pygame.display.flip()

    return puntos