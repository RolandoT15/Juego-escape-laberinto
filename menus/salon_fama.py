import json
import os
from configuracion import *


ARCHIVO_DATOS = "datos_salon_fama.json"


class SalonFamaManager:
    def __init__(self):
        self.datos = self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"modo_escapa": [], "modo_cazador": []}
        return {"modo_escapa": [], "modo_cazador": []}

    def guardar_datos(self):
        with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=4, ensure_ascii=False)

    def agregar_puntuacion(self, modo, nombre, puntuacion):
        entrada = {
            "nombre": nombre,
            "puntuacion": puntuacion
        }

        self.datos[modo].append(entrada)
        # Ordenar puntuación
        self.datos[modo].sort(key=lambda x: x["puntuacion"], reverse=True)


        self.datos[modo] = self.datos[modo][:5]

        self.guardar_datos()

    def obtener_top(self, modo, limite=5):
        return self.datos[modo][:limite]


def pantalla_ver_puntajes(manager):
    botones_modo = [
        Boton(50, 120, 300, 50, "Modo Escapa", AZUL, (41, 128, 185)),
        Boton(450, 120, 300, 50, "Modo Cazador", VERDE, (39, 174, 96))
    ]
    boton_volver = Boton(300, 520, 200, 50, "Volver", GRIS, GRIS_OSCURO)

    modo_actual = "modo_escapa"
    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botones_modo[0].verificar_click(pos_mouse):
                    modo_actual = "modo_escapa"
                elif botones_modo[1].verificar_click(pos_mouse):
                    modo_actual = "modo_cazador"
                elif boton_volver.verificar_click(pos_mouse):
                    return "menu"

        # Dibujar
        dibujar_fondo_degradado(pantalla)

        # Título
        titulo = fuente_titulo.render("TOP 5 JUGADORES", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))

        # Botones de modo
        for boton in botones_modo:
            boton.verificar_hover(pos_mouse)
            boton.dibujar(pantalla)

            # Indicar modo activo visualmente
            if (boton.texto == "Modo Escapa" and modo_actual == "modo_escapa") or \
                    (boton.texto == "Modo Cazador" and modo_actual == "modo_cazador"):
                pygame.draw.rect(pantalla, AMARILLO, boton.rect, 3, border_radius=10)

        # Mostrar puntuacion del modo seleccionado
        y_pos = 220
        top_scores = manager.obtener_top(modo_actual)

        if top_scores:
            encabezado = f"{'Lugar':<5}   {'NOMBRE':<20} {'PUNTOS':>10}"
            encabezado_surf = fuente_texto.render(encabezado, True, GRIS)
            pantalla.blit(encabezado_surf, (200, 180))

            for i, entrada in enumerate(top_scores):
                posicion = f"{i + 1}  "

                # Formato de texto alineado
                texto = f"{posicion:<5} {entrada['nombre'][:15]:.<20} {entrada['puntuacion']:>10}"

                color_texto = AMARILLO if i == 0 else BLANCO
                texto_surface = fuente_texto.render(texto, True, color_texto)
                pantalla.blit(texto_surface, (200, y_pos))

                y_pos += 40
        else:
            texto = fuente_texto.render("No hay puntuaciones todavía", True, GRIS)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 300))

        # Botón volver
        boton_volver.verificar_hover(pos_mouse)
        boton_volver.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(60)

    return "salir"