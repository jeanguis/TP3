import curses
import actores
from mapa import Mapa
import sys

class Juego(object):
    def __init__(self, nombre_mapa):
        """Carga el mapa del juego a partir del archivo mapas/<nombre_mapa>.map."""
        with open("mapas/{}.map".format(nombre_mapa)) as f:
            filas = [ linea.strip() for linea in f ]
        mapa, heroe = self.crear_mapa(filas)
        self.mapa = mapa
        self.heroe = heroe
        self.juego_terminado = False
        # El historial de mensajes es simplemente una lista de strings.
        self.mensajes = []

    def crear_mapa(self, filas):
        """Crea el Mapa a partir de la definicion provista por parametro (`filas`),
        y devuelve una tupla con el mapa y el actor que representa al heroe del juego.
        Si hay mas de un heroe en la definicion del mapa, o bien si no hay ningun
        heroe, la funcion lanza una excepcion.
        `filas` es una lista de strings, que corresponde con el contenido completo
        del archivo .map."""

        #There is no hero, create the map.
        posHero = 0
        mapa = Mapa(len(filas[0]), len(filas))

        #Invert the list of str
        reverse = zip(*filas)
        for i in xrange(len(reverse)):
           reverse[i] = ''.join(reverse[i])
        filas = reverse
        del reverse

        #for each line in the list of str
        for i, line in enumerate(filas):
            #for each character in the str
            for j, char in enumerate(line):
                #si el caracter es @
                if(char == '@'):
                    #Si hay hero
                    if posHero == 0: 
                        #Nuevo hero
                        posHero = (i, j)
                    else:
                        #Sino : Error, Hay dos !
                        raise Exception("Hay 2 heroes en la mapa")

                # Agrega los actores a la map
                if(char == '#'):
                    mapa.agregar_actor(actores.Pared(), i,j)
                if(char == 'g'):
                    mapa.agregar_actor(actores.Goblin(), i,j)
                if(char == 'o'):
                    mapa.agregar_actor(actores.Orco(), i,j)
                if(char == '$'):
                    mapa.agregar_actor(actores.Moneda(100), i,j)
                if(char == '<'):
                    mapa.agregar_actor(actores.Salida(), i,j)

        # Si no hay heroe : Exception
        if posHero == 0:
            raise Exception("No hay heroe en la mapa")

        # Cree el horoe
        heroe = actores.Heroe()
        # Lo agrega a la map
        mapa.agregar_actor(heroe, posHero[0], posHero[1])
        return mapa, heroe

    def turno(self, evento):
        """Llama al metodo jugar_turno() del heroe. Si el heroe hizo algo,
        llama al metodo jugar_turno() para el resto de los actores"""
        if self.juego_terminado:
            return

        if not self.heroe.jugar_turno_heroe(evento, self):
            # El heroe no hizo nada
            return

        # El resto de los actores juegan su turno
        for actor in self.mapa.actores:
            if not actor.es_heroe():
                actor.jugar_turno(self)

        self.mapa.eliminar_actores_muertos()

    def terminar(self):
        """Marcar que el juego ha terminado."""
        self.juego_terminado = True

    def msg(self, *args):
        """Agregar un mensaje al historial."""
        self.mensajes.append(" ".join(args))

    def dibujar_mensajes(self, ventana, cantidad):
        """Dibujar los ultimos `cantidad` mensajes del historial en la ventana provista."""
        for y, mensaje in enumerate(self.mensajes[-cantidad:]):
            ventana.addstr(y, 0, mensaje)

    def main(self):
        """Bucle principal del juego."""
        try:
            pantalla = curses.initscr()

            # No imprimir la entrada del teclado:
            curses.noecho()

            # Cursor invisible:
            curses.curs_set(0)

            # Habilitar las flechas para moverse
            pantalla.keypad(1)

            self.msg("Has ingresado en el calabozo! Podras escapar?")
            self.msg("Flechas para moverse, Q para salir")
            while True:
                pantalla.clear()
                self.mapa.dibujar(pantalla.derwin(0, 0))
                self.dibujar_mensajes(pantalla.derwin(0, self.mapa.ancho() + 2), self.mapa.alto())

                evento = pantalla.getch()

                if evento == ord("q"):
                    break
                self.turno(evento)
        finally:
            # devolver el estado de la consola (por ejemplo la visibilidad del cursor)
            curses.endwin()


# Mapa por defecto:
nombre_mapa = 'nivel1'
if len(sys.argv) > 1:
    nombre_mapa = sys.argv[1]

Juego(nombre_mapa).main()
