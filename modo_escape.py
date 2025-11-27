import pygame
import random
import sys
import math
import time

# Importo los módulos del mapa tal y como vienen en tu primer código
from mapa.muro import Muro
from mapa.suelo import Suelo
from mapa.constantes import FILAS, COLUMNAS, ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE, AZUL_META, ROJO_INICIO, NEGRO, \
    BLANCO
from mapa.liana import Liana
from mapa.tunel import Tunel
from mapa.trampas import Trampa


# ---------------------------
# CLASES DEL GENERADOR (copiadas / adaptadas)
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

        # Puntos de inicio y final
        ix, iy = self.inicio
        mx, my = self.meta
        self.mapa_objetos[iy][ix] = Inicio(ix, iy)
        self.mapa_objetos[my][mx] = Meta(mx, my)

        self.crear_camino_garantizado()

    def crear_camino_garantizado(self):
        x, y = self.inicio
        mx, my = self.meta

        # Busca del inicio al objetivo
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


# ---------------------------
# CONFIGURACIÓN DEL JUEGO
# ---------------------------
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Juego integrado - Mapa + Entidades")
reloj = pygame.time.Clock()

# Trampas
trampas = []  # Lista para almacenar las trampas activas
max_trampas = 3  # Número máximo de trampas simultáneas
ultimo_tiempo_trampa = 0  # Para controlar el cooldown de colocación
cooldown_trampa = 5  # En segundos
puntos = 0  # Puntuación del jugador

# Generador y mapa
generador = GeneradorMapa(FILAS, COLUMNAS)

# Tamaños de entidades (encajan dentro de un tile)
PLAYER_SIZE = max(4, TILE_SIZE - 6)
ENEMY_SIZE = max(4, TILE_SIZE - 10)

# Variables del jugador
player_speed_walk = 2.8  # velocidad en pixels/frame (más bajo porque tiles más pequeños)
player_speed_run = 5.0
player_color = (50, 150, 255)

# Energía
energy = 100.0
max_energy = 100.0
energy_bar_width = 20
energy_bar_height = min(ALTO_VENTANA - 40, 300)
energy_recovery = 0.25
energy_consumption = 0.9

# Enemigos (lista de dicts): x,y,spawn_x,spawn_y,visible,respawn_time
enemy_speed = 1.5  # Velocidad de persecución (ajustable)


# ---------------------------
# UTILIDADES: buscar tiles/posiciones
# ---------------------------
def tile_coords_from_rect(rect):
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


def tile_at(tx, ty):
    if 0 <= ty < generador.filas and 0 <= tx < generador.columnas:
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


# ---------------------------
# Inicializar jugador en tile Inicio
# ---------------------------
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
    # fallback al centro
    player_spawn_x = ANCHO_VENTANA // 2 - PLAYER_SIZE / 2
    player_spawn_y = ALTO_VENTANA // 2 - PLAYER_SIZE / 2

# Posición actual del jugador
player_x = player_spawn_x
player_y = player_spawn_y

# ---------------------------
# Inicializar enemigos en tiles válidos (pasa_enemigo True, no Inicio/Meta)
# ---------------------------
enemies = []
spawns = []
for y in range(generador.filas):
    for x in range(generador.columnas):
        t = generador.mapa_objetos[y][x]
        if getattr(t, 'pasa_enemigo', False) and t.__class__.__name__ not in ('Inicio', 'Meta'):
            spawns.append((x, y))

# Seleccionar hasta 6 spawn posibles y crear 3 enemigos aleatorios
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
        'spawn_x': float(ex),  # Guardar posición inicial
        'spawn_y': float(ey),
        'spawn_tx': tx,
        'spawn_ty': ty,
        'visible': True,
        'respawn_time': 0.0
    })


# ---------------------------
# FUNCIÓN PARA REINICIAR POSICIONES
# ---------------------------
def reset_positions():
    """Reinicia jugador y enemigos a sus posiciones iniciales"""
    global player_x, player_y, energy

    # Reiniciar jugador
    player_x = player_spawn_x
    player_y = player_spawn_y
    energy = max_energy  # Restaurar energía completa

    # Reiniciar enemigos
    for e in enemies:
        e['x'] = e['spawn_x']
        e['y'] = e['spawn_y']
        e['visible'] = True


# ---------------------------
# COLISIÓN TILE-BASED: comprobar si rect puede moverse dx,dy
# ---------------------------
def can_move_rect(rect, dx, dy, for_enemy=False):
    new_rect = rect.copy()
    new_rect.x += int(round(dx))
    new_rect.y += int(round(dy))

    # Obtener tiles que ocuparía
    left = max(0, new_rect.left // TILE_SIZE)
    right = min(generador.columnas - 1, (new_rect.right - 1) // TILE_SIZE)
    top = max(0, new_rect.top // TILE_SIZE)
    bottom = min(generador.filas - 1, (new_rect.bottom - 1) // TILE_SIZE)

    for ty in range(top, bottom + 1):
        for tx in range(left, right + 1):
            if for_enemy:
                if not is_passable_for_enemy(tx, ty):
                    return False
            else:
                if not is_passable_for_player(tx, ty):
                    return False
    return True


# ---------------------------
# EMPUJE SIMPLE ENTRE ENTIDADES (cuando se superponen)
# ---------------------------
def push_back_entities(rect_a, rect_b):
    if not rect_a.colliderect(rect_b):
        return
    dx = rect_b.centerx - rect_a.centerx
    dy = rect_b.centery - rect_a.centery
    if dx == 0 and dy == 0:
        dx = 1
    dist = math.hypot(dx, dy)
    overlap = (rect_a.width / 2 + rect_b.width / 2) - dist
    if dist != 0 and overlap > 0:
        dx /= dist
        dy /= dist
        # mover la mitad cada uno (si posible)
        rect_b.x += int(dx * (overlap / 2))
        rect_b.y += int(dy * (overlap / 2))
        rect_a.x -= int(dx * (overlap / 2))
        rect_a.y -= int(dy * (overlap / 2))


# ---------------------------
# BUCLE PRINCIPAL
# ---------------------------
running = True
while running:
    dt = reloj.tick(60) / 1000.0  # segundos por frame (no usado intensamente pero útil)
    now = time.time()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                # regenerar mapa, reposicionar jugador y enemigos y limpar trampas
                generador.generar()

                trampas = []
                ultimo_tiempo_trampa = 0

                # reposicionar jugador en el nuevo Inicio
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
                # recalcular spawns y reposicionar enemigos a sus nuevos spawns
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
            elif evento.key == pygame.K_t:
                tiempo_actual = time.time()
                # Verificar cooldown y número máximo de trampas
                if tiempo_actual - ultimo_tiempo_trampa >= cooldown_trampa and len(trampas) < max_trampas:
                    # Obtener la posición actual del jugador en tiles
                    tile_x = int(player_x // TILE_SIZE)
                    tile_y = int(player_y // TILE_SIZE)

                    # Crear nueva trampa en la posición del jugador
                    nueva_trampa = Trampa(tile_x, tile_y)
                    trampas.append(nueva_trampa)
                    ultimo_tiempo_trampa = tiempo_actual
    # ----- ENTRADAS -----
    keys = pygame.key.get_pressed()
    speed = player_speed_walk

    # correr si Shift y hay energía
    if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and energy > 0:
        speed = player_speed_run
        energy -= energy_consumption
        if energy < 0:
            energy = 0.0
    else:
        energy += energy_recovery
        if energy > max_energy: energy = max_energy

    # movimiento deseado (vector)
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

    # Normalizar diagonal (para que la velocidad no sea mayor al mover diagonal)
    if dx != 0 and dy != 0:
        inv = 1 / math.sqrt(2)
        dx *= inv
        dy *= inv

    player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)

    # Intentar mover en x, luego en y (colisión por tiles)
    if dx != 0:
        if can_move_rect(player_rect, dx, 0, for_enemy=False):
            player_rect.x += int(round(dx))
        else:
            # si no puede moverse en esa dirección, intentar moverse 1 pixel a la vez (suaviza)
            step = int(math.copysign(1, dx))
            moved = False
            for i in range(abs(int(round(dx)))):
                if can_move_rect(player_rect, step, 0, for_enemy=False):
                    player_rect.x += step
                    moved = True
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

    # Actualizar coordenadas del jugador
    player_x, player_y = float(player_rect.x), float(player_rect.y)

    # ----- MOVIMIENTO ENEMIGOS (PERSIGUEN al jugador, evitando paredes) -----
    for e in enemies:
        if not e['visible']:
            continue

        ex = e['x']
        ey = e['y']

        # vector DESDE enemigo HACIA jugador (perseguir)
        vdx = player_x - ex
        vdy = player_y - ey
        dist = math.hypot(vdx, vdy)

        if dist == 0:
            # Si están en la misma posición, no moverse
            continue

        # Normalizar el vector
        vdx /= dist
        vdy /= dist

        desired_dx = vdx * enemy_speed
        desired_dy = vdy * enemy_speed

        enemy_rect = pygame.Rect(int(ex), int(ey), ENEMY_SIZE, ENEMY_SIZE)

        # Si la dirección deseada es transitable para enemigos, moverse
        if can_move_rect(enemy_rect, desired_dx, desired_dy, for_enemy=True):
            enemy_rect.x += int(round(desired_dx))
            enemy_rect.y += int(round(desired_dy))
        else:
            # Intentar alternativas (intentar mover por componente X o Y o giros)
            moved = False
            # probar solo X
            if can_move_rect(enemy_rect, desired_dx, 0, for_enemy=True):
                enemy_rect.x += int(round(desired_dx))
                moved = True
            # probar solo Y
            elif can_move_rect(enemy_rect, 0, desired_dy, for_enemy=True):
                enemy_rect.y += int(round(desired_dy))
                moved = True
            else:
                # probar perpendiculares y giros simples
                attempts = [
                    (desired_dy, desired_dx),  # swap
                    (-desired_dx, -desired_dy),  # invert
                    (desired_dx, -desired_dy),
                    (-desired_dx, desired_dy),
                    (enemy_speed, 0),
                    (-enemy_speed, 0),
                    (0, enemy_speed),
                    (0, -enemy_speed)
                ]
                for ax, ay in attempts:
                    if can_move_rect(enemy_rect, ax, ay, for_enemy=True):
                        enemy_rect.x += int(round(ax))
                        enemy_rect.y += int(round(ay))
                        moved = True
                        break

        # actualizar pos
        e['x'] = float(enemy_rect.x)
        e['y'] = float(enemy_rect.y)

    # Verificar colisión de enemigos con trampas y actualizar estado
    trampas_a_eliminar = []
    for i, trampa in enumerate(trampas):
        if not trampa.activa:
            trampas_a_eliminar.append(i)
            continue

        for idx, e in enumerate(enemies):
            if not e['visible']:
                continue

            enemy_rect = pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE)
            if trampa.rect.colliderect(enemy_rect):
                # Enemigo eliminado por trampa
                e['visible'] = False
                e['respawn_time'] = time.time() + 10  # Reaparece después de 10 segundos
                trampa.desactivar()
                trampas_a_eliminar.append(i)

                # Incrementar puntuación
                puntos += 50  # O el valor que prefieras
                break

    # Eliminar trampas desactivadas (en orden inverso para no afectar los índices)
    for i in sorted(trampas_a_eliminar, reverse=True):
        if i < len(trampas):
            trampas.pop(i)

    # Actualizar estado de respawn de los enemigos
    for e in enemies:
        if not e['visible'] and time.time() >= e['respawn_time']:
            e['visible'] = True
            e['x'] = e['spawn_x']
            e['y'] = e['spawn_y']
    # ----- COLISIÓN ENTRE ENTIDADES (evitar superposición) -----
    player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
    enemy_rects = []
    for e in enemies:
        enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))

    # Empuje entre enemigos
    for i in range(len(enemy_rects)):
        for j in range(i + 1, len(enemy_rects)):
            push_back_entities(enemy_rects[i], enemy_rects[j])

    # Detectar colisión jugador-enemigos
    collision_detected = False
    for idx, er in enumerate(enemy_rects):
        if player_rect.colliderect(er) and enemies[idx]['visible']:
            collision_detected = True
            break

    # Si hay colisión, reiniciar todas las posiciones
    if collision_detected:
        reset_positions()
        # Recrear los rects después del reinicio
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE)
        enemy_rects = []
        for e in enemies:
            enemy_rects.append(pygame.Rect(int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))

    # ---------------------------
    # DIBUJADO
    # ---------------------------
    pantalla.fill(NEGRO)

    # Dibujar mapa (tiles)
    for fila in generador.mapa_objetos:
        for objeto in fila:
            objeto.dibujar(pantalla)

    # En la sección de dibujado, después de dibujar el mapa
    # Dibujar trampas activas
    for trampa in trampas:
        trampa.dibujar(pantalla)

    # Para mostrar información sobre trampas y puntuación, añade:
    font = pygame.font.SysFont(None, 24)
    texto_trampas = font.render(f"Trampas: {len(trampas)}/{max_trampas}", True, BLANCO)
    texto_puntos = font.render(f"Puntos: {puntos}", True, BLANCO)
    pantalla.blit(texto_trampas, (ANCHO_VENTANA - 150, 20))
    pantalla.blit(texto_puntos, (ANCHO_VENTANA - 150, 50))

    # Si quieres mostrar el cooldown de las trampas:
    if time.time() - ultimo_tiempo_trampa < cooldown_trampa:
        cooldown_restante = int(cooldown_trampa - (time.time() - ultimo_tiempo_trampa))
        texto_cooldown = font.render(f"Cooldown: {cooldown_restante}s", True, BLANCO)
        pantalla.blit(texto_cooldown, (ANCHO_VENTANA - 150, 80))

    # Dibujar jugador (centrado en su rect)
    pygame.draw.rect(pantalla, player_color, (int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE))

    # Dibujar enemigos visibles
    for e in enemies:
        if e['visible']:
            pygame.draw.rect(pantalla, (255, 50, 50), (int(e['x']), int(e['y']), ENEMY_SIZE, ENEMY_SIZE))

    # Dibujar barra vertical de energía a la izquierda
    pygame.draw.rect(pantalla, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))  # marco
    current_height = int((energy / max_energy) * energy_bar_height)
    pygame.draw.rect(pantalla, (0, 200, 0),
                     (10, 20 + (energy_bar_height - current_height), energy_bar_width, current_height))

    pygame.display.flip()

pygame.quit()
sys.exit()