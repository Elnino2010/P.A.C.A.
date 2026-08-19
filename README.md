# P.A.C.A.

Este es P.A.C.A (Programa de Asistencia Computacional Avanzado), antiguamente llamado Jarvis.
Este es un sistema modular centrado en plugins.

**Requisitos**:
Python 3.14 *(Obligatorio)*
.venv *(recomendado)*
pip *(Obligatorio)*
Ollama *(Obligatorio)*

---

**Pasos de instalación**:
1. Descarga el código del repo
2. Abre en tu editor de código favorito la carpeta del proyecto.
3. Crea el .venv *(opcional)*
4. Instala el requirements.txt con pip install -r requirements.txt
5. Ejecuta el main.py

Importante, se debe crear el .env en la carpeta donde esté el main.py y el base.py donde se debe exportar la variable OLLAMA_MODEL. En caso de no hacerse se usará el modelo de código abierto de gemma:2b.
Para consultar más modelos via ollama busca [aquí](https://ollama.com/search).

---

**Plugins incluidos**:
    - Calendario **(calendario.plugin)**
        - Añade una ventana con un calendario con eventos que añade el usuario
        - Permite usar comandos directos para añadir eventos a días futuros
    - Documentos **(documentos.plugin)**:
        - Abre un gestor de archivos donde podrás ver y abrir tus archivos en aplicaciones ya instaladas
        - Permite introducir una ruta absoluta en la barra de comandos
    - Barra de estado **(estatus_bar.plugin)**:
        - Añade un visor de porcentaje de uso de CPU y RAM.
    - Chat de ollama **(ollama.plugin)**:
        - Permite interactuar con una IA desde el chat.
        - Tiene memoria por chat
        - Tiene memoria persistente en formato .md para integrar manualmente en una bóveda de obsidian
    - Gestor inteligente **(orquestador.plugin)**:
        - Permite mandar un mensaje directamente en la barra y que este sea mandado al plugin correspondiente
    - Gestor de medios **(reproductor.plugin)**:
        - Permite gestionar la música del dispositivo ya sea por botones o comandos directos.
        - Puede reproducir música de fuentes como youtube.
        - Almacena una biblioteca con la lista de canciones escuchadas para que sea más fácil volver a ponerlas.
    - TTS **(voz.plugin)**:
        - Los mensajes del sistema pasan a ser tanto escritos como hablados por el programa.
    - Interfaz **(simpleui.plugin)**:
        - Interfaz sencilla que da un contraste más alto a la interfaz, existe como plantilla para mostrar los cambios que se pueden realizar en customtkinter, la librería que usa.