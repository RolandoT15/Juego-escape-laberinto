import pygame
import sys
import math
import random

pygame.init()

# ----- CONFIGURACIÓN DE VENTANA -----
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jugador con Energía y Barra Vertical")

clock = pygame.time.Clock()

# ----- JUGADOR -----
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
walk_speed = 4
run_speed = 7      # velocidad al correr
player_color = (50, 150, 255)

# ----- ENERGÍA -----
energy = 100
max_energy = 100
energy_bar_width = 20
energy_bar_height = 300
energy_recovery = 0.25     # Velocidad de recuperación
energy_consumption = 0.6    # Velocidad de consumo

# ----- ENEMIGOS -----
enemy_size = 40
enemy_speed = 2.0
enemy_color = (255, 50, 50)

enemies = []
for _ in range(3):
    ex = random.randint(0, WIDTH - enemy_size)
    ey = random.randint(0, HEIGHT - enemy_size)
    enemies.append([float(ex), float(ey)])

WHITE = (255, 255, 255)

# ---------------------------------------------
# FUNCIÓN PARA EMPUJAR ENTIDADES (COLISIONES)
# ---------------------------------------------
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


# ---------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # ----- MOVIMIENTO DEL JUGADOR -----
    speed = walk_speed

    # Si corre (Shift) y tiene energía
    if keys[pygame.K_LSHIFT] and energy > 0:
        speed = run_speed
        energy -= energy_consumption
        if energy < 0:
            energy = 0
    else:
        # Recuperar energía cuando no corre
        energy += energy_recovery
        if energy > max_energy:
            energy = max_energy

    # Movimiento con WASD y flechas
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += speed

    # Mantener jugador dentro de pantalla
    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    # ----- MOVIMIENTO DE ENEMIGOS -----
    for enemy in enemies:
        ex, ey = enemy
        dx = player_x - ex
        dy = player_y - ey
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        ex += dx * enemy_speed
        ey += dy * enemy_speed

        enemy[0], enemy[1] = ex, ey

    # ----- COLISIONES -----
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    enemy_rects = [pygame.Rect(e[0], e[1], enemy_size, enemy_size) for e in enemies]

    # Entre enemigos
    for i in range(len(enemy_rects)):
        for j in range(i + 1, len(enemy_rects)):
            push_back(enemy_rects[i], enemy_rects[j])

    # Jugador con enemigos
    for er in enemy_rects:
        push_back(player_rect, er)

    # Actualizar posiciones
    player_x, player_y = player_rect.x, player_rect.y
    for i, r in enumerate(enemy_rects):
        enemies[i][0], enemies[i][1] = r.x, r.y


    # ---------------------------------------------
    # DIBUJADO
    # ---------------------------------------------
    window.fill(WHITE)

    # ----- BARRA DE ENERGÍA VERTICAL -----
    pygame.draw.rect(window, (100, 100, 100), (10, 20, energy_bar_width, energy_bar_height))  # marco
    current_height = int((energy / max_energy) * energy_bar_height)
    pygame.draw.rect(window, (0, 200, 0), (10, 20 + (energy_bar_height - current_height), energy_bar_width, current_height))

    # Dibujar jugador
    pygame.draw.rect(window, player_color, player_rect)

    # Dibujar enemigos
    for r in enemy_rects:
        pygame.draw.rect(window, enemy_color, r)

    pygame.display.update()
