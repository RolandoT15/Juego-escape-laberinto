import random
from configuracion import *
from salon_fama import SalonFamaManager, pantalla_ver_puntajes
from jugadores import PlayerManager
from lista_jugadores import pantalla_ver_jugadores
import modo_escape
import modo_cazador


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
    boton_salir_fin = Boton(300, 450, 200, 50, "Volver al Menú", GRIS, GRIS_OSCURO)

    # Variables
    modo_seleccionado = "modo_escapa"  # Valor por defecto
    nombre_jugador = ""
    mensaje_estado = ""
    color_mensaje = ROJO

    puntuacion = 0
    guardado_automatico = False

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()


        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado_fase == "configuracion":
                    # Selección de modo
                    if botones_modo[0].verificar_click(pos_mouse):
                        modo_seleccionado = "modo_escapa"
                    elif botones_modo[1].verificar_click(pos_mouse):
                        modo_seleccionado = "modo_cazador"

                    # Volver atrás
                    elif boton_volver.verificar_click(pos_mouse):
                        return "menu"

                    # INICIAR JUEGO REAL
                    elif boton_iniciar.verificar_click(pos_mouse):
                        nombre_raw = input_nombre.texto.strip()
                        if nombre_raw:
                            # 1. Registrar jugador
                            texto_msg, es_nuevo = player_manager.verificar_y_registrar(nombre_raw)
                            nombre_jugador = nombre_raw

                            # 2. EJECUTAR EL JUEGO EXTERNO
                            # Pasamos la pantalla actual y el nombre
                            if modo_seleccionado == "modo_escapa":
                                # Llama a la funcion de  archivo modo_escapa.py
                                puntuacion = modo_escape.ejecutar_juego(pantalla, nombre_jugador)
                            elif modo_seleccionado == "modo_cazador":
                                # Llama a la funcion de archivo modo_cazador.py
                                puntuacion = modo_cazador.ejecutar_juego(pantalla, nombre_jugador)

                            # 3. Al terminar el juego (return), cambiamos a fase terminado
                            estado_fase = "terminado"

                            # Reiniciamos eventos para evitar clics fantasma al volver
                            pygame.event.clear()
                        else:
                            mensaje_estado = "¡Por favor escribe tu nombre!"
                            color_mensaje = ROJO

                elif estado_fase == "terminado":
                    if boton_salir_fin.verificar_click(pos_mouse):
                        return "menu"

            if estado_fase == "configuracion":
                input_nombre.manejar_evento(evento)

        dibujar_fondo_degradado(pantalla)

        if estado_fase == "configuracion":
            # --- DIBUJO DE MENÚ DE CONFIGURACIÓN ---
            titulo = fuente_titulo.render("CONFIGURACIÓN", True, BLANCO)
            pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

            for boton in botones_modo:
                boton.verificar_hover(pos_mouse)
                boton.dibujar(pantalla)
                # Resaltar botón seleccionado
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

            if mensaje_estado:
                err_surf = fuente_pequena.render(mensaje_estado, True, color_mensaje)
                pantalla.blit(err_surf, (ANCHO // 2 - err_surf.get_width() // 2, 360))

        elif estado_fase == "terminado":
            # --- GUARDADO Y PANTALLA FINAL ---
            if not guardado_automatico:
                leaderboard_manager.agregar_puntuacion(modo_seleccionado, nombre_jugador, puntuacion)
                player_manager.registrar_partida(nombre_jugador)
                guardado_automatico = True

            titulo = fuente_titulo.render("¡PARTIDA FINALIZADA!", True, BLANCO)
            pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 100))

            res_nom = fuente_subtitulo.render(f"Jugador: {nombre_jugador}", True, BLANCO)
            pantalla.blit(res_nom, (ANCHO // 2 - res_nom.get_width() // 2, 200))

            res_mode = fuente_pequena.render(f"Modo: {modo_seleccionado}", True, GRIS)
            pantalla.blit(res_mode, (ANCHO // 2 - res_mode.get_width() // 2, 240))

            res_pts = fuente_titulo.render(f"Puntuación: {puntuacion}", True, AMARILLO)
            pantalla.blit(res_pts, (ANCHO // 2 - res_pts.get_width() // 2, 300))


            boton_salir_fin.verificar_hover(pos_mouse)
            boton_salir_fin.dibujar(pantalla)

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