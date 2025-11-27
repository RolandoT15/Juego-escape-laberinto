import pygame
import sys
import math
import random
import time

pygame.init()

# ----- CONFIGURACIÓN DE VENTANA -----
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jugador Persigue - Enemigos Huyen")

clock = pygame.time.Clock()

# ----- JUGADOR -----
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
walk_speed = 4
run_speed = 7
player_color = (50, 150, 255)

# ----- ENERGÍA -----
energy = 100
max_energy = 100
energy_bar_width = 20
energy_bar_height = 300
energy_recovery = 0.25
energy_consumption = 0.6

# ----- ENEMIGOS -----
enemy_size = 40
enemy_speed = 2.5
enemy_color = (255, 50, 50)

# Cada enemigo tendrá:
# [x, y, visible(bool), respawn_time(float)]
enemies = []
for _ in range(3):
    ex = random.randint(0, WIDTH - enemy_size)
    ey = random.randint(0, HEIGHT - enemy_size)
    enemies.append([float(ex), float(ey), True, 0])

WHITE = (255, 255, 255)

# ---- FUNCIÓN PARA EMPUJE / COLISION ----
def push_back(rect_a, rect_b):
    if not rect_a.colliderect(rect_b):
        return

    dx = rect_b.centerx - rect_a.centerx
    dy = rect_b.centery - rect_a.centery

    if dx == 0 and dy == 0:
        dx = 1

    distance = math.hypot(dx, dy)
    overlap = (rect_a.width/2 + rect_b.width/2) - distance

    if distance != 0:
        dx /= distance
        dy /= distance

    rect_b.x += dx * (overlap / 2)
    rect_b.y += dy * (overlap / 2)
    rect_a.x -= dx * (overlap / 2)
    rect_a.y -= dy * (overlap / 2)


# ============================================
# LOOP PRINCIPAL
# ============================================
running = True
while running:
    clock.tick(60)
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # ----- MOVIMIENTO DEL JUGADOR -----
    speed = walk_speed
    if keys[pygame.K_LSHIFT] and energy > 0:
        speed = run_speed
        energy -= energy_consumption
        if energy < 0:
            energy = 0
    else:
        energy += energy_recovery
        if energy > max_energy:
            energy = max_energy

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += speed

    # Límite de pantalla
    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    # ----------------------------------------------
    # MOVIMIENTO DE ENEMIGOS (HUIR DEL JUGADOR)
    # ----------------------------------------------
    enemy_rects = []

    for enemy in enemies:
        ex, ey, visible, respawn_time = enemy

        # Si está invisible, verificar si debe reaparecer
        if not visible:
            if now >= respawn_time:
                enemy[0] = random.randint(0, WIDTH - enemy_size)
                enemy[1] = random.randint(0, HEIGHT - enemy_size)
                enemy[2] = True  # reaparece
            continue

        # Vector del jugador al enemigo (huida)
        dx = ex - player_x
        dy = ey - player_y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        # Huir del jugador
        ex += dx * enemy_speed
        ey += dy * enemy_speed

        # Limitar a la pantalla
        ex = max(0, min(WIDTH - enemy_size, ex))
        ey = max(0, min(HEIGHT - enemy_size, ey))

        enemy[0] = ex
        enemy[1] = ey

        enemy_rects.append((enemy, pygame.Rect(ex, ey, enemy_size, enemy_size)))

    # ----------------------------------------------
    # COLISIONES Y CAZA (Jugador toca enemigo)
    # ----------------------------------------------
    visible_rects = [rect for enemy, rect in enemy_rects]

    # Evitar colisiones entre enemigos visibles
    for i in range(len(visible_rects)):
        for j in range(i + 1, len(visible_rects)):
            push_back(visible_rects[i], visible_rects[j])

    # Jugador con enemigos: si toca → desaparecen 3 s
    for enemy, rect in enemy_rects:
        push_back(player_rect, rect)

        if player_rect.colliderect(rect):  
            enemy[2] = False          # invisible
            enemy[3] = now + 3        # reaparece en 3 s

    # Guardar posiciones corregidas
    player_x, player_y = player_rect.x, player_rect.y

    for enemy, rect in enemy_rects:
        enemy[0], enemy[1] = rect.x, rect.y

    # ==========================
    # DIBUJADO
    # ==========================
    window.fill(WHITE)

    # ----- DIBUJAR BARRA DE ENERGÍA -----
    pygame.draw.rect(window, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))
    bar_height = int((energy / max_energy) * energy_bar_height)
    pygame.draw.rect(window, (0, 200, 0),
                     (10, 20 + (energy_bar_height - bar_height), energy_bar_width, bar_height))

    # Jugador
    pygame.draw.rect(window, player_color, player_rect)

    # Enemigos
    for enemy in enemies:
        if enemy[2]:  # visible
            pygame.draw.rect(window, enemy_color,
                             (enemy[0], enemy[1], enemy_size, enemy_size))

    pygame.display.update()
