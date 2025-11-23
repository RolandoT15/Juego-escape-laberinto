from configuracion import *


def pantalla_ver_jugadores(manager):
    boton_volver = Boton(300, 520, 200, 50, "Volver", GRIS, GRIS_OSCURO)
    lista_nombres = manager.obtener_nombres()
    lista_mostrar = lista_nombres[:10]

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.verificar_click(pos_mouse):
                    return "menu"


        dibujar_fondo_degradado(pantalla)

        # Título
        titulo = fuente_titulo.render("JUGADORES", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))


        pygame.draw.line(pantalla, AMARILLO, (300, 90), (500, 90), 3)

        # Listar Nombres
        y_pos = 120
        if lista_mostrar:
            for i, nombre in enumerate(lista_mostrar):
                texto = f"{i + 1}. {nombre}"
                texto_surface = fuente_subtitulo.render(texto, True, BLANCO)
                pantalla.blit(texto_surface, (ANCHO // 2 - texto_surface.get_width() // 2, y_pos))

                y_pos += 35
        else:
            txt_vacio = fuente_texto.render("No hay jugadores registrados.", True, GRIS)
            pantalla.blit(txt_vacio, (ANCHO // 2 - txt_vacio.get_width() // 2, 250))

        # Boton volver
        boton_volver.verificar_hover(pos_mouse)
        boton_volver.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(60)

    return "salir"