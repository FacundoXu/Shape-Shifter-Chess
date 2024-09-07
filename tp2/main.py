from logica import *

def main():
    gamelib.resize(ANCHO_TABLERO, ALTO_TABLERO)

    movimientos = cargar_movimientos(RUTA_MOVIMIENTOS)
    n_nivel = 0
    juego = []

    if hay_partida_guardada(RUTA_PARTIDA):
        while True:
            continuar = gamelib.input(PREGUNTA)

            if continuar.lower() == SI:
                juego, n_nivel = cargar_partida(RUTA_PARTIDA)
                break
            if continuar.lower() == NO:
                n_nivel = 1
                juego = juego_nuevo(movimientos, n_nivel)
                break
    else:
        gamelib.say(ERROR1)
        gamelib.say(ERROR2)
        
        n_nivel = 1
        juego = juego_nuevo(movimientos, n_nivel)
        guardar_partida(RUTA_PARTIDA, juego)

    while gamelib.is_alive():
        cant_piezas = 0
        
        gamelib.draw_begin()
        juego_mostrar(juego, n_nivel)
        gamelib.draw_end()

        ev = gamelib.wait()
        if not ev:
            break

        if ev.type == gamelib.EventType.ButtonPress and ev.mouse_button == 1:
            x, y = ev.x, ev.y
            juego = juego_actualizar(movimientos, juego, x, y)

            for i in range(len(juego)):
                for j in range(len(juego[0])):
                    if not hay_vacio(juego, i, j):
                        cant_piezas += 1

            if cant_piezas == 1:
                gamelib.play_sound(GANAR)
                n_nivel += 1
                juego = juego_nuevo(movimientos, n_nivel)

        if ev.type == gamelib.EventType.KeyPress and (ev.key == 'z' or ev.key == 'Z'):
            gamelib.play_sound(RESTART)
            juego, n_nivel = cargar_partida(RUTA_PARTIDA)
            
        if ev.type == gamelib.EventType.KeyPress and ev.key == 'Escape':
            break

gamelib.init(main)