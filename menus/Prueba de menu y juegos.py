import random
import pygame
import sys
import math
import time
from configuracion import *
from salon_fama import SalonFamaManager, pantalla_ver_puntajes
from jugadores import PlayerManager
from lista_jugadores import pantalla_ver_jugadores

# ============================================================================
# AQUÍ PEGAR TODOS LOS IMPORTS DEL JUEGO (mapa.muro, mapa.suelo, etc.)
# ============================================================================
from mapa.muro import Muro
from mapa.suelo import Suelo
from mapa.constantes import FILAS, COLUMNAS, ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE, AZUL_META, ROJO_INICIO, NEGRO, BLANCO
from mapa.liana import Liana
from mapa.tunel import Tunel


# ============================================================================
# AQUÍ PEGAR LAS CLASES: Inicio, Meta, GeneradorMapa
# ============================================================================
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

            if not moves:
                break

            dx, dy = random.choice(moves)
            x += dx
            y += dy

            if (x, y) != (mx, my):
                objeto_actual = self.mapa_objetos[y][x]
                if not getattr(objeto_actual, 'pasa_jugador', False):
                    self.mapa_objetos[y][x] = Suelo(x, y)


# ============================================================================
# AQUÍ PEGAR LAS FUNCIONES AUXILIARES DEL JUEGO:
# - tile_coords_from_rect
# - tile_at
# - is_passable_for_player
# - is_passable_for_enemy
# - world_pos_center_of_tile
# - can_move_rect
# - push_back_entities
# ============================================================================
def tile_coords_from_rect(rect, generador):
    """Devuelve lista de (tx,ty) tiles ocupados por rect (enteros)."""
    left = rect.left // TILE_SIZE
    right = rect.right // TILE_SIZE
    top = rect.top // TILE_SIZE
    bottom = rect.bottom // TILE_SIZE

    coords = []
    for ty in range(top, bottom + 1):
        for tx in range(left, right + 1):
            coords.append((tx, ty))
    return coords


def tile_at(tx, ty, generador):
    if 0 <= ty < generador.filas and 0 <= tx < generador.columnas:
        return generador.mapa_objetos[ty][tx]
    return None


def is_passable_for_player(tx, ty, generador):
    t = tile_at(tx, ty, generador)
    return t is not None and getattr(t, 'pasa_jugador', False)


def is_passable_for_enemy(tx, ty, generador):
    t = tile_at(tx, ty, generador)
    return t is not None and getattr(t, 'pasa_enemigo', False)


def world_pos_center_of_tile(tx, ty):
    return (tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2)


def can_move_rect(rect, dx, dy, generador, for_enemy=False):
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
                if not is_passable_for_enemy(tx, ty, generador):
                    return False
            else:
                if not is_passable_for_player(tx, ty, generador):
                    return False
    return True


def push_back_entities(rect_a, rect_b):
    if not rect_a.colliderect(rect_b):
        return
    dx = rect_b.centerx - rect_a.centerx
    dy = rect_b.centery - rect_a.centery
    if dx == 0 and dy == 0:
        dx = 1
    dist = math.hypot(dx, dy)
    overlap = (rect_a.width/2 + rect_b.width/2) - dist
    if dist != 0 and overlap > 0:
        dx /= dist
        dy /= dist
        rect_b.x += int(dx * (overlap / 2))
        rect_b.y += int(dy * (overlap / 2))
        rect_a.x -= int(dx * (overlap / 2))
        rect_a.y -= int(dy * (overlap / 2))

# ============================================================================
# AQUÍ PEGAR LA FUNCIÓN: ejecutar_modo_escapa(nombre_jugador)
# (Juego donde enemigos PERSIGUEN al jugador)
# ============================================================================
def ejecutar_modo_escapa(nombre_jugador):
    """Modo donde los enemigos persiguen al jugador"""
    
    # Configuración del juego
    generador = GeneradorMapa(FILAS, COLUMNAS)
    
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
    
    enemy_speed = 1.5
    
    # Inicializar jugador en tile Inicio
    player_spawn_x = 0.0
    player_spawn_y = 0.0
    found_inicio = False
    for y in range(generador.filas):
        for x in range(generador.columnas):
            obj = generador.mapa_objetos[y][x]
            if obj.__class__.__name__ == 'Inicio':
                cx, cy = world_pos_center_of_tile(x, y)
                player_spawn_x, player_spawn_y = cx - PLAYER_SIZE / 2, cy - PLAYER_SIZE / 2
                found_inicio = True
                break
        if found_inicio:
            break
    
    if not found_inicio:
        player_spawn_x = ANCHO_VENTANA // 2 - PLAYER_SIZE / 2
        player_spawn_y = ALTO_VENTANA // 2 - PLAYER_SIZE / 2
    
    player_x = player_spawn_x
    player_y = player_spawn_y
    
    # Inicializar enemigos
    enemies = []
    spawns = []
    for y in range(generador.filas):
        for x in range(generador.columnas):
            t = generador.mapa_objetos[y][x]
            if getattr(t, 'pasa_enemigo', False) and t.__class__.__name__ not in ('Inicio', 'Meta'):
                spawns.append((x, y))
    
    random.shuffle(spawns)
    num_enemies = 3
    for i in range(min(num_enemies, len(spawns))):
        tx, ty = spawns[i]
        cx, cy = world_pos_center_of_tile(tx, ty)
        ex = cx - ENEMY_SIZE / 2
        ey = cy - ENEMY_SIZE / 2
        enemies.append({
            'x': float(ex),
            'y': float(ey),
            'spawn_x': float(ex),
            'spawn_y': float(ey),
            'spawn_tx': tx,
            'spawn_ty': ty,
            'visible': True,
            'respawn_time': 0.0
        })
    
    def reset_positions():
        nonlocal player_x, player_y, energy
        player_x = player_spawn_x
        player_y = player_spawn_y
        energy = max_energy
        for e in enemies:
            e['x'] = e['spawn_x']
            e['y'] = e['spawn_y']
            e['visible'] = True
    
    # Bucle principal
    reloj = pygame.time.Clock()
    running = True
    
    while running:
        dt = reloj.tick(60) / 1000.0
        now = time.time()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "menu"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"
                if evento.key == pygame.K_SPACE:
                    generador.generar()
                    found = False
                    for y in range(generador.filas):
                        for x in range(generador.columnas):
                            obj = generador.mapa_objetos[y][x]
                            if obj.__class__.__name__ == 'Inicio':
                                cx, cy = world_pos_center_of_tile(x, y)
                                player_spawn_x, player_spawn_y = cx - PLAYER_SIZE / 2, cy - PLAYER_SIZE / 2
                                player_x, player_y = player_spawn_x, player_spawn_y
                                found = True
                                break
                        if found: break
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
                        enemies.append({
                            'x': float(ex), 
                            'y': float(ey), 
                            'spawn_x': float(ex),
                            'spawn_y': float(ey),
                            'spawn_tx': tx, 
                            'spawn_ty': ty, 
                            'visible': True, 
                            'respawn_time': 0.0
                        })
        
        # Entradas del jugador
        keys = pygame.key.get_pressed()
        speed = player_speed_walk
        
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and energy > 0:
            speed = player_speed_run
            energy -= energy_consumption
            if energy < 0:
                energy = 0.0
        else:
            energy += energy_recovery
            if energy > max_energy: energy = max_energy
        
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed
        
        if dx != 0 and dy != 0:
            inv = 1 / math.sqrt(2)
            dx *= inv
            dy *= inv
        
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
        
        if dx != 0:
            if can_move_rect(player_rect, dx, 0, generador, for_enemy=False):
                player_rect.x += int(round(dx))
            else:
                step = int(math.copysign(1, dx))
                for i in range(abs(int(round(dx)))):
                    if can_move_rect(player_rect, step, 0, generador, for_enemy=False):
                        player_rect.x += step
                    else:
                        break
        
        if dy != 0:
            if can_move_rect(player_rect, 0, dy, generador, for_enemy=False):
                player_rect.y += int(round(dy))
            else:
                step = int(math.copysign(1, dy))
                for i in range(abs(int(round(dy)))):
                    if can_move_rect(player_rect, 0, step, generador, for_enemy=False):
                        player_rect.y += step
                    else:
                        break
        
        player_x, player_y = float(player_rect.x), float(player_rect.y)
        
        # Movimiento enemigos (PERSIGUEN)
        for e in enemies:
            if not e['visible']:
                continue
            
            ex = e['x']
            ey = e['y']
            
            vdx = player_x - ex
            vdy = player_y - ey
            dist = math.hypot(vdx, vdy)
            
            if dist == 0:
                continue
            
            vdx /= dist
            vdy /= dist
            
            desired_dx = vdx * enemy_speed
            desired_dy = vdy * enemy_speed
            
            enemy_rect = pygame.Rect(int(ex), int(ey), ENEMY_SIZE, ENEMY_SIZE)
            
            if can_move_rect(enemy_rect, desired_dx, desired_dy, generador, for_enemy=True):
                enemy_rect.x += int(round(desired_dx))
                enemy_rect.y += int(round(desired_dy))
            else:
                moved = False
                if can_move_rect(enemy_rect, desired_dx, 0, generador, for_enemy=True):
                    enemy_rect.x += int(round(desired_dx))
                    moved = True
                elif can_move_rect(enemy_rect, 0, desired_dy, generador, for_enemy=True):
                    enemy_rect.y += int(round(desired_dy))
                    moved = True
                else:
                    attempts = [
                        (desired_dy, desired_dx),
                        (-desired_dx, -desired_dy),
                        (desired_dx, -desired_dy),
                        (-desired_dx, desired_dy),
                        (enemy_speed, 0),
                        (-enemy_speed, 0),
                        (0, enemy_speed),
                        (0, -enemy_speed)
                    ]
                    for ax, ay in attempts:
                        if can_move_rect(enemy_rect, ax, ay, generador, for_enemy=True):
                            enemy_rect.x += int(round(ax))
                            enemy_rect.y += int(round(ay))
                            moved = True
                            break
            
            e['x'] = float(enemy_rect.x)
            e['y'] = float(enemy_rect.y)
        
        # Colisión
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
        enemy_rects = []
        for e in enemies:
            enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))
        
        for i in range(len(enemy_rects)):
            for j in range(i + 1, len(enemy_rects)):
                push_back_entities(enemy_rects[i], enemy_rects[j])
        
        collision_detected = False
        for idx, er in enumerate(enemy_rects):
            if player_rect.colliderect(er) and enemies[idx]['visible']:
                collision_detected = True
                break
        
        if collision_detected:
            reset_positions()
            player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
            enemy_rects = []
            for e in enemies:
                enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))
        
        # Dibujar
        pantalla.fill(NEGRO)
        
        for fila in generador.mapa_objetos:
            for objeto in fila:
                objeto.dibujar(pantalla)
        
        pygame.draw.rect(pantalla, player_color, (int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE))
        
        for e in enemies:
            if e['visible']:
                pygame.draw.rect(pantalla, (255, 50, 50), (int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))
        
        pygame.draw.rect(pantalla, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))
        current_height = int((energy / max_energy) * energy_bar_height)
        pygame.draw.rect(pantalla, (0, 200, 0), (10, 20 + (energy_bar_height - current_height), energy_bar_width, current_height))
        
        # Mostrar nombre del jugador
        texto_nombre = fuente_texto.render(f"Jugador: {nombre_jugador}", True, BLANCO)
        pantalla.blit(texto_nombre, (ANCHO_VENTANA - texto_nombre.get_width() - 10, 10))
        
        pygame.display.flip()
    
    return "menu"

# ============================================================================
# AQUÍ PEGAR LA FUNCIÓN: ejecutar_modo_cazador(nombre_jugador)
# (Juego donde enemigos HUYEN del jugador)
# ============================================================================
def ejecutar_modo_cazador(nombre_jugador):
    """Modo donde el jugador persigue a los enemigos y estos huyen"""
    
    # Configuración del juego
    generador = GeneradorMapa(FILAS, COLUMNAS)
    
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
    
    enemy_speed = 1.8
    
    # Inicializar jugador en tile Inicio
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
        if found_inicio:
            break
    
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
    num_enemies = 3
    for i in range(min(num_enemies, len(spawns))):
        tx, ty = spawns[i]
        cx, cy = world_pos_center_of_tile(tx, ty)
        ex = cx - ENEMY_SIZE / 2
        ey = cy - ENEMY_SIZE / 2
        enemies.append({
            'x': float(ex),
            'y': float(ey),
            'spawn_tx': tx,
            'spawn_ty': ty,
            'visible': True,
            'respawn_time': 0.0
        })
    
    # Bucle principal
    reloj = pygame.time.Clock()
    running = True
    
    while running:
        dt = reloj.tick(60) / 1000.0
        now = time.time()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "menu"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"
                if evento.key == pygame.K_SPACE:
                    generador.generar()
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
                        enemies.append({'x': float(ex), 'y': float(ey), 'spawn_tx': tx, 'spawn_ty': ty, 'visible': True, 'respawn_time': 0.0})
        
        # Entradas del jugador
        keys = pygame.key.get_pressed()
        speed = player_speed_walk
        
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and energy > 0:
            speed = player_speed_run
            energy -= energy_consumption
            if energy < 0:
                energy = 0.0
        else:
            energy += energy_recovery
            if energy > max_energy: energy = max_energy
        
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed
        
        if dx != 0 and dy != 0:
            inv = 1 / math.sqrt(2)
            dx *= inv
            dy *= inv
        
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
        
        if dx != 0:
            if can_move_rect(player_rect, dx, 0, generador, for_enemy=False):
                player_rect.x += int(round(dx))
            else:
                step = int(math.copysign(1, dx))
                for i in range(abs(int(round(dx)))):
                    if can_move_rect(player_rect, step, 0, generador, for_enemy=False):
                        player_rect.x += step
                    else:
                        break
        
        if dy != 0:
            if can_move_rect(player_rect, 0, dy, generador, for_enemy=False):
                player_rect.y += int(round(dy))
            else:
                step = int(math.copysign(1, dy))
                for i in range(abs(int(round(dy)))):
                    if can_move_rect(player_rect, 0, step, generador, for_enemy=False):
                        player_rect.y += step
                    else:
                        break
        
        player_x, player_y = float(player_rect.x), float(player_rect.y)
        
        # Movimiento enemigos (HUYEN)
        for e in enemies:
            if not e['visible']:
                if now >= e['respawn_time']:
                    stx, sty = e['spawn_tx'], e['spawn_ty']
                    cx, cy = world_pos_center_of_tile(stx, sty)
                    e['x'] = cx - ENEMY_SIZE / 2
                    e['y'] = cy - ENEMY_SIZE / 2
                    e['visible'] = True
                continue
            
            ex = e['x']
            ey = e['y']
            
            # Vector desde jugador hacia enemigo (HUIR)
            vdx = ex - player_x
            vdy = ey - player_y
            dist = math.hypot(vdx, vdy)
            if dist == 0:
                vdx, vdy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                dist = 1.0
            
            vdx /= dist
            vdy /= dist
            
            desired_dx = vdx * enemy_speed
            desired_dy = vdy * enemy_speed
            
            enemy_rect = pygame.Rect(int(ex), int(ey), ENEMY_SIZE, ENEMY_SIZE)
            
            if can_move_rect(enemy_rect, desired_dx, desired_dy, generador, for_enemy=True):
                enemy_rect.x += int(round(desired_dx))
                enemy_rect.y += int(round(desired_dy))
            else:
                moved = False
                if can_move_rect(enemy_rect, desired_dx, 0, generador, for_enemy=True):
                    enemy_rect.x += int(round(desired_dx))
                    moved = True
                elif can_move_rect(enemy_rect, 0, desired_dy, generador, for_enemy=True):
                    enemy_rect.y += int(round(desired_dy))
                    moved = True
                else:
                    attempts = [
                        (desired_dy, desired_dx),
                        (-desired_dx, -desired_dy),
                        (desired_dx, -desired_dy),
                        (-desired_dx, desired_dy),
                        (enemy_speed, 0),
                        (-enemy_speed, 0),
                        (0, enemy_speed),
                        (0, -enemy_speed)
                    ]
                    for ax, ay in attempts:
                        if can_move_rect(enemy_rect, ax, ay, generador, for_enemy=True):
                            enemy_rect.x += int(round(ax))
                            enemy_rect.y += int(round(ay))
                            moved = True
                            break
            
            e['x'] = float(enemy_rect.x)
            e['y'] = float(enemy_rect.y)
        
        # Colisión
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
        enemy_rects = []
        for e in enemies:
            enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))
        
        for i in range(len(enemy_rects)):
            for j in range(i + 1, len(enemy_rects)):
                push_back_entities(enemy_rects[i], enemy_rects[j])
        
        for idx, er in enumerate(enemy_rects):
            push_back_entities(player_rect, er)
            
            if player_rect.colliderect(er) and enemies[idx]['visible']:
                enemies[idx]['visible'] = False
                enemies[idx]['respawn_time'] = now + 3.0
                enemies[idx]['x'] = -1000.0
                enemies[idx]['y'] = -1000.0
        
        player_x, player_y = float(player_rect.x), float(player_rect.y)
        for i, r in enumerate(enemy_rects):
            enemies[i]['x'], enemies[i]['y'] = float(r.x), float(r.y)
        
        # Dibujar
        pantalla.fill(NEGRO)
        
        for fila in generador.mapa_objetos:
            for objeto in fila:
                objeto.dibujar(pantalla)
        
        pygame.draw.rect(pantalla, player_color, (int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE))
        
        for e in enemies:
            if e['visible']:
                pygame.draw.rect(pantalla, (255, 50, 50), (int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))
        
        pygame.draw.rect(pantalla, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))
        current_height = int((energy / max_energy) * energy_bar_height)
        pygame.draw.rect(pantalla, (0, 200, 0), (10, 20 + (energy_bar_height - current_height), energy_bar_width, current_height))
        
        # Mostrar nombre del jugador
        texto_nombre = fuente_texto.render(f"Jugador: {nombre_jugador}", True, BLANCO)
        pantalla.blit(texto_nombre, (ANCHO_VENTANA - texto_nombre.get_width() - 10, 10))
        
        pygame.display.flip()
    
    return "menu"

def pantalla_menu(manager):
    botones = [
        Boton(250, 180, 300, 55, "Jugar", VERDE, (39, 174, 96)),
        Boton(250, 250, 300, 55, "Salon de la Fama", AZUL, (41, 128, 185)),
        Boton(250, 320, 300, 55, "Ver Jugadores", AMARILLO, (243, 156, 18)),
        Boton(250, 450, 300, 55, "Salir", ROJO, (192, 57, 43))
    ]

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botones[0].verificar_click(pos_mouse):
                    return "jugar"
                elif botones[1].verificar_click(pos_mouse):
                    return "salon_fama"
                elif botones[2].verificar_click(pos_mouse):
                    return "ver_jugadores"
                elif botones[3].verificar_click(pos_mouse):
                    return "salir"

        dibujar_fondo_degradado(pantalla)

        titulo = fuente_titulo.render("Escape Laberinto", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))

        for boton in botones:
            boton.verificar_hover(pos_mouse)
            boton.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(60)

    return "salir"


def pantalla_simular_juego(leaderboard_manager, player_manager):
    estado_fase = "configuracion"

    botones_modo = [
        Boton(50, 150, 300, 50, "Modo Escapa", AZUL, (41, 128, 185)),
        Boton(450, 150, 300, 50, "Modo Cazador", VERDE, (39, 174, 96))
    ]
    input_nombre = InputBox(250, 300, 300, 50)
    boton_iniciar = Boton(300, 400, 200, 50, "Comenzar", VERDE, (39, 174, 96))
    boton_volver = Boton(20, 20, 100, 40, "Atrás", GRIS, GRIS_OSCURO)

    # Variables de juego
    modo_seleccionado = "modo_escapa"
    nombre_jugador = ""
    mensaje_estado = ""
    color_mensaje = ROJO

    tiempo_inicio_mensaje = 0

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()
        tiempo_actual = pygame.time.get_ticks()

        # --- LOGICA ---
        if estado_fase == "mensaje_bienvenida":
            if tiempo_actual - tiempo_inicio_mensaje > 2000:
                # Ejecutar el juego según el modo seleccionado
                if modo_seleccionado == "modo_escapa":
                    resultado = ejecutar_modo_escapa(nombre_jugador)
                else:
                    resultado = ejecutar_modo_cazador(nombre_jugador)
                
                # Volver al menú después del juego
                return "menu"

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado_fase == "configuracion":
                    if botones_modo[0].verificar_click(pos_mouse):
                        modo_seleccionado = "modo_escapa"
                    elif botones_modo[1].verificar_click(pos_mouse):
                        modo_seleccionado = "modo_cazador"
                    elif boton_iniciar.verificar_click(pos_mouse):
                        nombre_raw = input_nombre.texto.strip()
                        if nombre_raw:
                            texto_msg, es_nuevo = player_manager.verificar_y_registrar(nombre_raw)
                            nombre_jugador = nombre_raw
                            mensaje_estado = texto_msg
                            color_mensaje = VERDE if es_nuevo else AZUL
                            estado_fase = "mensaje_bienvenida"
                            tiempo_inicio_mensaje = tiempo_actual
                        else:
                            mensaje_estado = "¡Por favor escribe tu nombre!"
                            color_mensaje = ROJO
                    elif boton_volver.verificar_click(pos_mouse):
                        return "menu"

            if estado_fase == "configuracion":
                input_nombre.manejar_evento(evento)

        dibujar_fondo_degradado(pantalla)

        if estado_fase == "configuracion":
            titulo = fuente_titulo.render("CONFIGURACIÓN", True, BLANCO)
            pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

            for boton in botones_modo:
                boton.verificar_hover(pos_mouse)
                boton.dibujar(pantalla)
                if (boton.texto == "Modo Escapa" and modo_seleccionado == "modo_escapa") or \
                        (boton.texto == "Modo Cazador" and modo_seleccionado == "modo_cazador"):
                    pygame.draw.rect(pantalla, AMARILLO, boton.rect, 3, border_radius=10)

            texto_nom = fuente_texto.render("Ingresa tu nombre:", True, BLANCO)
            pantalla.blit(texto_nom, (250, 270))
            input_nombre.dibujar(pantalla)

            boton_iniciar.verificar_hover(pos_mouse)
            boton_iniciar.dibujar(pantalla)
            boton_volver.verificar_hover(pos_mouse)
            boton_volver.dibujar(pantalla)

            if mensaje_estado and estado_fase == "configuracion":
                err_surf = fuente_pequena.render(mensaje_estado, True, color_mensaje)
                pantalla.blit(err_surf, (ANCHO // 2 - err_surf.get_width() // 2, 360))

        elif estado_fase == "mensaje_bienvenida":
            msg_surf = fuente_subtitulo.render(mensaje_estado, True, color_mensaje)
            pantalla.blit(msg_surf, (ANCHO // 2 - msg_surf.get_width() // 2, ALTO // 2))
            sub_msg = fuente_pequena.render("Iniciando partida...", True, BLANCO)
            pantalla.blit(sub_msg, (ANCHO // 2 - sub_msg.get_width() // 2, ALTO // 2 + 40))

        pygame.display.flip()
        reloj.tick(60)

    return "salir"


def main():
    manager = SalonFamaManager()
    player_manager = PlayerManager()
    estado = "menu"

    while estado != "salir":
        if estado == "menu":
            estado = pantalla_menu(manager)
        elif estado == "salon_fama":
            estado = pantalla_ver_puntajes(manager)
        elif estado == "ver_jugadores":
            estado = pantalla_ver_jugadores(player_manager)
        elif estado == "jugar":
            estado = pantalla_simular_juego(manager, player_manager)

    pygame.quit()


if __name__ == "__main__":
    main()