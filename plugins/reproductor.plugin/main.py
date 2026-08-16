import os
import json
import shutil
import threading
import customtkinter as ctk
from base import PluginBase
import static_ffmpeg
static_ffmpeg.add_paths()
import keyboard
# Importaciones seguras de librerías multimedia y de IA
try:
    import pygame
    PYGAME_DISPONIBLE = True
except ImportError:
    PYGAME_DISPONIBLE = False

try:
    import yt_dlp
    YTDLP_DISPONIBLE = True
except ImportError:
    YTDLP_DISPONIBLE = False

try:
    import ollama
    OLLAMA_DISPONIBLE = True
except ImportError:
    OLLAMA_DISPONIBLE = False


class PluginControladorMedios(PluginBase):
    def __init__(self):
        super().__init__()
        self.reproduciendo = False
        self.cancion_actual = "Ninguna"
        
        # Carpeta temporal para guardar la canción que esté sonando
        self.dir_temp = os.path.join(os.path.dirname(__file__), "temp_audio")
        os.makedirs(self.dir_temp, exist_ok=True)

        if PYGAME_DISPONIBLE:
            pygame.mixer.init()

    @property
    def nombre(self) -> str:
        return "Controlador de Medios"

    @property
    def descripcion(self) -> str:
        return "Permite controlar la reproducción de medios, como música o videos, desde la interfaz de Jarvis. Usa comandos desde el chat como 'reproduce', 'pausa' o 'detener' para controlar la reproducción."

    @property
    def acepta_comandos_directos(self) -> bool:
        return True

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        self.app = app

        # Frame de Controles Multimedia en el área inferior
        self.contenedor_medios = ctk.CTkFrame(self.frame_espacio, fg_color="transparent")

        self.btn_play_pause = ctk.CTkButton(
            self.contenedor_medios,
            text="Pausa" if self.reproduciendo else " ▶ Play",
            width=80,
            font=("Consolas", 11, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_color="#00F0FF",
            border_width=1,
            command=self.toggle_play_pause
        )
        self.btn_play_pause.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(
            self.contenedor_medios,
            text="⏹ Stop",
            width=70,
            font=("Consolas", 11, "bold"),
            fg_color="#1E293B",
            hover_color="#EF4444",
            border_color="#EF4444",
            border_width=1,
            command=self.detener_reproduccion
        )
        self.btn_stop.pack(side="left", padx=5)

        self.lbl_cancion = ctk.CTkLabel(
            self.contenedor_medios,
            text=" " + self.cancion_actual,
            font=("Consolas", 11),
            text_color="#00FF9D"
        )
        self.lbl_cancion.pack(side="left", padx=10)

    def al_activar(self):
        self.contenedor_medios.pack(fill="x", pady=5)

    def al_desactivar(self):
        self.detener_reproduccion()
        self.limpiar_temporales()
        self.contenedor_medios.pack_forget()

    def toggle_play_pause(self):
        # Si tenemos audio propio de yt-dlp sonando vía pygame, lo pausamos/reanudamos
        if PYGAME_DISPONIBLE and pygame.mixer.music.get_busy():
            if self.reproduciendo:
                pygame.mixer.music.pause()
                self.reproduciendo = False
                self.btn_play_pause.configure(text="▶ Play")
                self.funcion_chat(self.nombre, "Música de JARVIS pausada.")
            else:
                pygame.mixer.music.unpause()
                self.reproduciendo = True
                self.btn_play_pause.configure(text="⏸ Pausa")
                self.funcion_chat(self.nombre, "Reanudando música de JARVIS.")
        else:
            # Si no hay audio propio, enviamos la tecla multimedia global de Windows
            keyboard.send("play/pause media")
            self.funcion_chat(self.nombre, " ⏯ Comando Play/Pausa enviado al sistema.")

    def detener_reproduccion(self):
        if PYGAME_DISPONIBLE and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.reproduciendo = False
        self.cancion_actual = "Ninguna"
        if hasattr(self, 'lbl_cancion'):
            self.lbl_cancion.configure(text="Ninguna")
            self.btn_play_pause.configure(text="▶ Play")
        self.limpiar_temporales()

    def limpiar_temporales(self):
        """Borra la carpeta de descarga temporal para no dejar basura en el disco"""
        try:
            if os.path.exists(self.dir_temp):
                for archivo in os.listdir(self.dir_temp):
                    ruta_file = os.path.join(self.dir_temp, archivo)
                    if os.path.isfile(ruta_file):
                        os.remove(ruta_file)
        except Exception:
            pass  # Si el archivo está ocupado aún por el reproductor, se borrará en la siguiente limpieza

    def buscar_y_reproducir(self, busqueda: str):
        """Descarga el audio en segundo plano y lo reproduce"""
        if not YTDLP_DISPONIBLE or not PYGAME_DISPONIBLE:
            self.funcion_chat(self.nombre, "Faltan las librerías 'yt-dlp' o 'pygame'.")
            return

        self.funcion_chat(self.nombre, f"Buscando y descargando audio para: '{busqueda}'...")
        self.detener_reproduccion()

        # Opciones para yt-dlp: Extraer solo audio en MP3 comprimido ligero
        opciones_ytdlp = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.dir_temp, 'cancion_actual.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch1:',
            # Evitar errores de bloqueo por parte de YouTube con un User-Agent válido
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        try:
            with yt_dlp.YoutubeDL(opciones_ytdlp) as ydl:
                info = ydl.extract_info(busqueda, download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    titulo = info['entries'][0]['title']
                else:
                    titulo = info.get('title', busqueda)

            # Buscamos el archivo mp3 descargado en la carpeta temp
            archivo_mp3 = None
            for f in os.listdir(self.dir_temp):
                if f.endswith(".mp3"):
                    archivo_mp3 = os.path.join(self.dir_temp, f)
                    break

            if archivo_mp3 and os.path.exists(archivo_mp3):
                pygame.mixer.music.load(archivo_mp3)
                pygame.mixer.music.play()
                self.reproduciendo = True
                self.cancion_actual = titulo[:30] + "..." if len(titulo) > 30 else titulo
                
                # Actualizar UI
                self.lbl_cancion.configure(text=f"{self.cancion_actual}")
                self.btn_play_pause.configure(text="⏸ Pausa")
                self.funcion_chat(self.nombre, f"▶ Reproduciendo: {titulo}")
            else:
                self.funcion_chat(self.nombre, "No se pudo procesar el archivo de audio.")

        except Exception as e:
            self.funcion_chat(self.nombre, f"Error al buscar canción: {str(e)}")

    # Integración con ollama
    def procesar_comando_directo(self, texto: str):
        if OLLAMA_DISPONIBLE:
            threading.Thread(target=self._procesar_con_ia, args=(texto,), daemon=True).start()

    def procesar_comando(self, texto: str):
        palabras_clave = ["reproduce", "pon ", "musica", "cancion", "pausa", "para la musica", "continua"]
        if any(p in texto.lower() for p in palabras_clave):
            if OLLAMA_DISPONIBLE:
                threading.Thread(target=self._procesar_con_ia, args=(texto,), daemon=True).start()

    def _procesar_con_ia(self, prompt: str):
        system_prompt = """
Eres la IA de control multimedia de JARVIS. Analiza la petición del usuario y responde ÚNICAMENTE en código JSON.

ESTRUCTURA DEL JSON:
1. Para reproducir o buscar una canción/artista:
{"accion": "REPRODUCIR", "busqueda": "Nombre de la cancion o artista"}

2. Para pausar o reanudar:
{"accion": "TOGGLE"}

3. Para detener la música por completo:
{"accion": "STOP"}

4. Si no es un comando de audio:
{"accion": "IGNORAR"}

Devuelve SOLO el JSON, sin bloques de markdown ni texto adicional.
"""
        try:
            respuesta = ollama.chat(
                model="gemma4:e4b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            contenido = respuesta['message']['content'].strip()
            if contenido.startswith("```"): contenido = contenido.split("\n", 1)[1].rsplit("\n", 1)[0]
            if contenido.startswith("json"): contenido = contenido[4:].strip()

            datos = json.loads(contenido)
            accion = datos.get("accion")

            if accion == "REPRODUCIR":
                busqueda = datos.get("busqueda")
                if busqueda:
                    self.buscar_y_reproducir(busqueda)
            elif accion == "TOGGLE":
                self.toggle_play_pause()
            elif accion == "STOP":
                self.detener_reproduccion()
                self.funcion_chat(self.nombre, "⏹ Reproducción detenida.")

        except Exception:
            pass