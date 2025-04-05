# Ejemplo de Anexos para Poderes en Juego de Coincidencias

Este proyecto muestra un ejemplo de como implementar anexos para crear poderes especiales en un juego de coincidencias (match-3).

## Funcionalidades Principales

* **Creación de Poderes Especiales:**
    * Al hacer coincidir 4 cuadros, se crea un poder que elimina todos los cuadros horizontales y verticales adyacentes al cuadro de poder.
    * Al hacer coincidir 5 cuadros, se eliminan todos los cuadros del mismo color en el tablero.
* **Movimiento Restringido:**
    * Solo se permite mover un cuadro si el movimiento resulta en una coincidencia valida.
    * Si el movimiento no genera una coincidencia, el cuadro regresa a su posicion original.
* **Detección de Tablero Sin Movimientos:**
    * El juego detecta automaticamente cuando no hay movimientos posibles disponibles.
    * En caso de que no haya movimientos, el tablero se reinicia para generar nuevas oportunidades de juego.

## Nota Importante sobre el Video de Demostración

Durante la grabacion del video de demostracion, se comento temporalmente la funcionalidad de movimiento restringido. Esto se hizo para facilitar la creacion de coincidencias de 4 y 5 cuadros, lo cual seria bastante dificil de lograr en un video con la restricción de movimiento activada.

Sin embargo, es importante destacar que al descomentar el codigo correspondiente, el juego funciona con todas las funcionalidades completas (ESTO SOLO SE HIZO PARA LAS PRUEBAS DEL VIDEO AQUI ESTA EL CODIGO COMPLETO SIN FUNCIONALIDADES COMENTADAS):

* Solo se permite mover cuadros para crear coincidencias vAlidas.
* El juego detecta y reinicia el tablero cuando no hay movimientos posibles.

Por lo tanto, el juego en su estado final, con el cOdigo descomentado, incluye todas las funcionalidades descritas anteriormente.
