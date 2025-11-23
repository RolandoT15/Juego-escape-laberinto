import json
import os

ARCHIVO_JUGADORES = "datos_jugador.json"


class PlayerManager:
    def __init__(self):
        self.jugadores = self.cargar_jugadores()

    def cargar_jugadores(self):
        if os.path.exists(ARCHIVO_JUGADORES):
            try:
                with open(ARCHIVO_JUGADORES, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    if isinstance(datos, list):
                        return datos
                    return []
            except:
                return []
        return []

    def guardar_jugadores(self):
        with open(ARCHIVO_JUGADORES, 'w', encoding='utf-8') as f:
            json.dump(self.jugadores, f, indent=4, ensure_ascii=False)

    def verificar_y_registrar(self, nombre):
        nombre = nombre.strip()
        encontrado = False

        for jugador in self.jugadores:
            if jugador[0] == nombre:
                encontrado = True
                break

        if encontrado:
            return (f"¡Bienvenido de nuevo, {nombre}!", False)
        else:
            nuevo_jugador = [nombre, 0]
            self.jugadores.append(nuevo_jugador)
            self.guardar_jugadores()
            return (f"¡Jugador registrado: {nombre}!", True)

    def registrar_partida(self, nombre):
        for jugador in self.jugadores:
            if jugador[0] == nombre:
                jugador[1] += 1
                self.guardar_jugadores()
                return

    def obtener_nombres(self):
        nombres = []

        for jugador in self.jugadores:
            nombres.append(jugador[0])

        nombres.sort()
        return nombres