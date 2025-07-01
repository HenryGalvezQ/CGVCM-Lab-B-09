# CGVCM Lab B-09

Este proyecto contiene un juego de ping pong en Unity controlado por
scripts de Python mediante UDP. Se incluye un modo básico de seguimiento
de colores y un cliente adicional para jugar desde otra computadora.

## Requisitos
- Unity 2022.3.47f1
- Python 3.7+
- Paquetes: `opencv-python` y `numpy`

## Ejecución básica
1. Instala las dependencias en tu entorno de Python:
   ```bash
   pip install opencv-python numpy
   ```
2. Ejecuta `PingPongLab.py` para detectar los marcadores rojo y azul. Por defecto
   se envía a `127.0.0.1:5065`, pero puedes indicar la IP y el puerto:
   ```bash
   python PingPongLab.py --ip 192.168.0.10 --port 5065
   ```
3. Abre la escena **PingPongScene.unity** en Unity y presiona Play.

## Modo multijugador en red
Para que cada jugador use su propia cámara en diferentes equipos,
utiliza el script `RemotePaddle.py` y envía la posición de un solo
paddle indicando el lado:
```bash
python RemotePaddle.py --side L --color blue --ip 192.168.0.10
```
En el equipo que ejecuta Unity, `UDPReceiver` aceptará mensajes con el
formato `L:valor` o `R:valor` para controlar las raquetas izquierda y
derecha respectivamente.

## Modo de un jugador con IA

Agregamos el script `AIPaddle.cs` para que una raqueta pueda seguir
automáticamente la posición de la pelota. Asigna el script al paddle
que quieras automatizar y referencia la bola desde el Inspector.
