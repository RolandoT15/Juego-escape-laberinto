import pygame

pygame.init()

# Configuración de pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Escape del Laberinto")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (52, 152, 219)
VERDE = (46, 204, 113)
ROJO = (231, 76, 60)
GRIS = (149, 165, 166)
GRIS_OSCURO = (52, 73, 94)
AMARILLO = (241, 196, 15)

# Fuentes
fuente_titulo = pygame.font.Font(None, 64)
fuente_subtitulo = pygame.font.Font(None, 36)
fuente_texto = pygame.font.Font(None, 28)
fuente_pequena = pygame.font.Font(None, 22)

# Clases
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.color_actual = color

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_actual, self.rect, border_radius=10)
        pygame.draw.rect(superficie, BLANCO, self.rect, 3, border_radius=10)

        texto_surface = fuente_texto.render(self.texto, True, BLANCO)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        superficie.blit(texto_surface, texto_rect)

    def verificar_hover(self, pos_mouse):
        if self.rect.collidepoint(pos_mouse):
            self.color_actual = self.color_hover
            return True
        else:
            self.color_actual = self.color
            return False

    def verificar_click(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)


class InputBox:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = ""
        self.activo = False
        self.max_caracteres = 12

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(evento.pos)

        if evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.key == pygame.K_RETURN:
                return True
            elif len(self.texto) < self.max_caracteres:
                if evento.unicode.isprintable():
                    self.texto += evento.unicode
        return False

    def dibujar(self, superficie):
        color = AZUL if self.activo else GRIS
        pygame.draw.rect(superficie, color, self.rect, 3, border_radius=5)

        texto_surface = fuente_texto.render(self.texto, True, BLANCO)
        superficie.blit(texto_surface, (self.rect.x + 10, self.rect.y + 10))

def dibujar_fondo_degradado(superficie):
    for y in range(ALTO):
        color = (
            int(44 * (1 - y / ALTO) + 52 * (y / ALTO)),
            int(62 * (1 - y / ALTO) + 73 * (y / ALTO)),
            int(80 * (1 - y / ALTO) + 94 * (y / ALTO))
        )
        pygame.draw.line(superficie, color, (0, y), (ANCHO, y))