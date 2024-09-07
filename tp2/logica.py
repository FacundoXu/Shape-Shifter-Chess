from random import *
import csv
import gamelib

# Tamaño del gamelib
ANCHO_TABLERO = 400
ALTO_TABLERO = 500

# Tamaño del juego
FILAS = 8
COLUMNAS = 8

# Diseño del juego
TITULO = 'Shape Shifter Chess'
TITULO_POS_X = 100
TITULO_POS_Y = 430
NIVEL_POS_X = 53
NIVEL_POS_Y = 470
SALIR = 'Salir: Esc'
SALIR_POS_X = 299
SALIR_POS_Y = 430
REINTENTAR = 'Reintentar: Z'
REINTENTAR_POS_X = 310
REINTENTAR_POS_Y = 470

# Colores
GRIS = '#2D2D3F'
NEGRO = '#171717'
ROJO = '#FF0F58'

# Rutas de archivos
RUTA_MOVIMIENTOS = 'movimientos.csv'
RUTA_PARTIDA = 'partida.csv'
GANAR = 'music/ganar.wav'
RESTART = 'music/reintentar.wav'

# Estados de piezas
MOV_POSIBLE = 'mov_posible'
ACTIVA = 'activa'

# Errores
ERROR1 = 'No se encontro partida guardada'
ERROR2 = 'Vamos a generar un nivel'

# Entradas
SI = 's'
NO = 'n'
PREGUNTA = 'Quiere continuar la partida? (s/n)'

# Otros
VACIO = ''
DIVISOR_PIXEL = 10

def cargar_movimientos(ruta):
    '''
    Recibe la ruta de un archivo. Devuelve un diccionario con los posibles movimientos de cada pieza
    '''
    movimientos = {}

    with open(ruta) as f:
        for linea in csv.reader(f):
            pieza, direccion, extensible = linea[0], linea[1].split(';'), linea[2]
            movimientos[pieza] = movimientos.get(pieza, [])

            if extensible == 'true':
                for i in range(1, FILAS + 1):
                    movimientos[pieza].append(tuple(i * int(x) for x in direccion))
            if extensible == 'false':
                movimientos[pieza].append(tuple(int(x) for x in direccion))
    
    return movimientos

def crear_juego():
    '''
    Devuelve un juego representado como matriz
    '''
    juego = [[VACIO for j in range(COLUMNAS)] for i in range(FILAS)]
    return juego

def generar_primera_pieza(movimientos):
    '''
    Devuelve una primera pieza aleatoria
    '''
    return choice(list(movimientos))

def generar_posicion_primera_pieza():
    '''
    Devuelve la posicion de una primera pieza aleatoria
    '''
    return randint(0, FILAS - 1), randint(0, COLUMNAS - 1)

def generar_pieza_aleatoria(movimientos):
    '''
    Devuelve una pieza aleatoria
    '''
    return choice(list(movimientos))

def hay_vacio(juego, x, y):
    '''
    Devuelve True si hay vacio en la posicion, sino, devuelve False
    '''
    return juego[x][y] == VACIO

def coordenadas_a_pixeles(x, y):
    '''
    Recibe las coordenadas de una pieza. Devuelve las coordenadas en pixeles
    '''
    return x // (ALTO_TABLERO // DIVISOR_PIXEL), y // (ALTO_TABLERO // DIVISOR_PIXEL)

def guardar_partida(ruta, juego):
    '''
    Guarda los datos de la partida en un archivo
    '''
    with open(ruta, 'w', newline='') as f:
        partida = csv.writer(f)
        partida.writerows(juego)

def cargar_partida(ruta):
    '''
    Carga los datos de la partida guardada
    '''
    juego = []
    n_nivel = 0

    with open(ruta) as f:
        for linea in csv.reader(f):
            for i, elemento in enumerate(linea):

                if elemento != VACIO:
                    pieza, estado = elemento.split(',')
                    linea[i] = (pieza[2:-1], estado[2:-2])
                    n_nivel += 1

            juego.append(linea)

    return juego, n_nivel - 2

def hay_partida_guardada(ruta):
    '''
    Devuelve True si hay una partida guardada, sino, devuelve False
    '''
    try:
        with open(ruta) as f:
            return True
    except FileNotFoundError as e:
        return False

def juego_nuevo(movimientos, n_nivel):
    '''
    Recibe los movimientos posibles y el n_nivel del juego. Devuelve un nuevo juego
    '''
    primera_pieza = generar_primera_pieza(movimientos)
    prim_x, prim_y = generar_posicion_primera_pieza()

    juego = crear_juego()
    juego[prim_y][prim_x] = (primera_pieza, ACTIVA)
    
    pieza = primera_pieza
    pos_x, pos_y = prim_x, prim_y
    
    for i in range(1, n_nivel + 2):
        while True:
            dir_x, dir_y = choice(movimientos[pieza])
            prox_x, prox_y = (pos_x + dir_x), (pos_y + dir_y)

            if (0 < prox_x < FILAS) and (0 < prox_y < COLUMNAS):

                if hay_vacio(juego, prox_y, prox_x):
                    pieza = generar_pieza_aleatoria(movimientos)
                    pos_x, pos_y = prox_x, prox_y 
                    juego[pos_y][pos_x] = (pieza, VACIO)

                    for direccion in movimientos[primera_pieza]:
                        dir_prim_x, dir_prim_y = direccion

                        if (pos_x == dir_prim_x + prim_x) and (pos_y == dir_prim_y + prim_y):
                            juego[pos_y][pos_x] = (pieza, MOV_POSIBLE)
                break
    
    guardar_partida(RUTA_PARTIDA, juego)
    return juego

def juego_actualizar(movimientos, juego, x, y):
    '''
    Recibe los posibles movimientos, un juego y unas coordenadas. Devuelve un juego actualizado
    '''
    pos_x, pos_y = coordenadas_a_pixeles(x, y)
    
    if pos_x < FILAS and pos_y < COLUMNAS and not hay_vacio(juego, pos_y, pos_x):
        pieza, estado = juego[pos_y][pos_x]

        if estado == MOV_POSIBLE: 
            pos_x_activa, pos_y_activa = None, None

            for i in range(len(juego)):
                for j in range(len(juego[0])):
                    if not hay_vacio(juego, i, j):

                        if juego[i][j][1] == ACTIVA:
                            pos_x_activa, pos_y_activa = j, i
                        else:
                            juego[i][j] = (juego[i][j][0], VACIO)

            juego[pos_y][pos_x] = (pieza, ACTIVA)
            juego[pos_y_activa][pos_x_activa] = VACIO

            for direccion in movimientos[pieza]:
                dir_x, dir_y = direccion

                for fila in range(len(juego)):
                    for columna in range(len(juego[0])):

                        prox_x, prox_y = dir_x + pos_x, dir_y + pos_y
                        
                        if prox_x == columna and prox_y == fila and not hay_vacio(juego, fila, columna):
                            juego[fila][columna] = (juego[fila][columna][0], MOV_POSIBLE)
                                
    return juego

def mostrar_casilleros():
    '''
    Muestra graficamente los casilleros del juego
    '''
    for i in range(0, ANCHO_TABLERO + 1, ALTO_TABLERO // 10):
        gamelib.draw_line(i, 0, i, ANCHO_TABLERO, fill=NEGRO)
        gamelib.draw_line(0, i, ANCHO_TABLERO, i, fill=NEGRO)

    for i in range(FILAS):
        for j in range(COLUMNAS):
            if (i + j) % 2 == 0:
                color = GRIS
            else:
                color = NEGRO
            gamelib.draw_rectangle(i * (ALTO_TABLERO // 10) + 2, j * (ALTO_TABLERO // 10) + 2, (ALTO_TABLERO // 10) * (i + 1) - 2, (ALTO_TABLERO // 10) * (j + 1) - 2, fill=color)

def mostrar_detalles(n_nivel):
    '''
    Muestra graficamente el titulo, el nivel actual y las entradas que puede utilizar el usuario
    '''
    gamelib.draw_text(TITULO, TITULO_POS_X, TITULO_POS_Y, fill=ROJO)
    gamelib.draw_text(f'Nivel: {n_nivel}', NIVEL_POS_X, NIVEL_POS_Y, fill=ROJO)
    gamelib.draw_text(SALIR, SALIR_POS_X, SALIR_POS_Y, fill=ROJO)
    gamelib.draw_text(REINTENTAR, REINTENTAR_POS_X, REINTENTAR_POS_Y, fill=ROJO)

def imagen_ruta(pieza, estado):
    '''
    Recibe la pieza y el estado. Devuelve la ruta de la respectiva pieza
    '''
    if estado == ACTIVA:
        imagen = 'img/' + pieza + '_rojo.gif'
    if estado == MOV_POSIBLE or estado == VACIO:
        imagen = 'img/' + pieza + '_blanco.gif'

    return imagen

def imagen_posicion(pos_x, pos_y):
    '''
    Recibe las coordenadas. Devuelve las coordenadas en las que seran mostradas las imagenes
    '''
    return (pos_x * (ALTO_TABLERO // 10)) + 3, (pos_y * (ALTO_TABLERO // 10)) + 3

def dibujar_imagen(imagen, x, y):
    '''
    Recibe la imagen y sus coordenadas. Dibuja la imagen de la pieza
    '''
    gamelib.draw_image(imagen, x, y)

def dibujar_rectangulo_posible(pos_x, pos_y):
    '''
    Recibe las coordenadas. Dibuja un rectangulo rojo para el estado de movimiento posible
    '''
    gamelib.draw_rectangle(pos_x * (ALTO_TABLERO // 10) + 3, pos_y * (ALTO_TABLERO // 10) + 3, (ALTO_TABLERO // 10) * (pos_x + 1) - 2, (ALTO_TABLERO // 10) * (pos_y + 1) - 2, fill=VACIO, outline=ROJO, width=3)

def asignar_imagen_pieza(pieza, estado, pos_x, pos_y):
    '''
    Recibe la pieza, su estado y sus coordenadas. 
    Asigna la imagen a su respectiva pieza dependiendo del estado de la misma
    '''
    imagen = imagen_ruta(pieza, estado)
    x, y = imagen_posicion(pos_x, pos_y)

    if estado == ACTIVA:
        dibujar_imagen(imagen, x, y)
    if estado == MOV_POSIBLE:
        dibujar_rectangulo_posible(pos_x, pos_y)
        dibujar_imagen(imagen, x, y)
    if estado == VACIO:
        dibujar_imagen(imagen, x, y)

def mostrar_piezas(juego):
    '''
    Muestra graficamente las piezas del juego, la pieza actual y las posibles piezas a visitar
    '''
    for pos_x in range(FILAS):
        for pos_y in range(COLUMNAS):
            if not hay_vacio(juego, pos_y, pos_x):
                pieza, estado = juego[pos_y][pos_x]
                asignar_imagen_pieza(pieza, estado, pos_x, pos_y)

def juego_mostrar(juego, n_nivel):
    '''
    Recibe un juego y el n_nivel actual. Muestra graficamente todo el juego con sus respectivos elementos
    '''
    mostrar_casilleros()
    mostrar_detalles(n_nivel)
    mostrar_piezas(juego)