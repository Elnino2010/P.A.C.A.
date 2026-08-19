import os
import re
import json
import threading
import customtkinter as ctk
from base import PluginBase
import static_ffmpeg
static_ffmpeg.add_paths()
import keyboard
from dotenv import load_dotenv

load_dotenv()
ollama_model = os.getenv("OLLAMA_MODEL", "gemma:2b")

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

        # Carpeta permanente para biblioteca de música y almacenamiento JSON
        self.dir_musica = os.path.join(os.path.dirname(__file__), "musica")
        self.ruta_json = os.path.join(self.dir_musica, "biblioteca.json")
        os.makedirs(self.dir_musica, exist_ok=True)

        self._inicializar_biblioteca()

        if PYGAME_DISPONIBLE:
            pygame.mixer.init()

    def _inicializar_biblioteca(self):
        """Crea el archivo biblioteca.json si no existe."""
        if not os.path.exists(self.ruta_json):
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def _cargar_biblioteca(self) -> dict:
        """Carga el índice de canciones guardadas."""
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _guardar_en_biblioteca(self, clave_busqueda: str, titulo: str, ruta_archivo: str):
        """Registra una nueva canción descargada en el JSON."""
        biblioteca = self._cargar_biblioteca()
        biblioteca[clave_busqueda.lower()] = {
            "titulo": titulo,
            "archivo": os.path.basename(ruta_archivo)
        }
        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(biblioteca, f, ensure_ascii=False, indent=4)

    def _buscar_en_biblioteca(self, busqueda: str) -> tuple:
        """Comprueba si la búsqueda coincide con alguna entrada del JSON."""
        biblioteca = self._cargar_biblioteca()
        busqueda_clean = busqueda.lower().strip()

        # Búsqueda exacta por clave de solicitud
        if busqueda_clean in biblioteca:
            info = biblioteca[busqueda_clean]
            ruta = os.path.join(self.dir_musica, info["archivo"])
            if os.path.exists(ruta):
                return info["titulo"], ruta

        # Búsqueda por coincidencia parcial en el título
        for clave, info in biblioteca.items():
            if busqueda_clean in info["titulo"].lower() or busqueda_clean in clave:
                ruta = os.path.join(self.dir_musica, info["archivo"])
                if os.path.exists(ruta):
                    return info["titulo"], ruta

        return None, None

    @property
    def nombre(self) -> str:
        return "Controlador de Medios"

    @property
    def descripcion(self) -> str:
        return "Permite controlar la reproducción de música local o buscar de internet sin borrar descargas."

    @property
    def acepta_comandos_directos(self) -> bool:
        return True

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        self.app = app

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
        self.contenedor_medios.pack_forget()

    def toggle_play_pause(self):
        if PYGAME_DISPONIBLE and pygame.mixer.music.get_busy():
            if self.reproduciendo:
                pygame.mixer.music.pause()
                self.reproduciendo = False
                self.btn_play_pause.configure(text="▶ Play")
                self.funcion_chat(self.nombre, "Música pausada.")
            else:
                pygame.mixer.music.unpause()
                self.reproduciendo = True
                self.btn_play_pause.configure(text="⏸ Pausa")
                self.funcion_chat(self.nombre, "Reanudando música.")
        else:
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

    def _reproducir_archivo(self, titulo: str, ruta_mp3: str):
        """Carga y reproduce una pista mediante Pygame."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(ruta_mp3)
        pygame.mixer.music.play()
        self.reproduciendo = True
        self.cancion_actual = titulo[:30] + "..." if len(titulo) > 30 else titulo

        self.lbl_cancion.configure(text=f"{self.cancion_actual}")
        self.btn_play_pause.configure(text="⏸ Pausa")
        self.funcion_chat(self.nombre, f"▶ Reproduciendo: {titulo}")

    def buscar_y_reproducir(self, busqueda: str):
        if not YTDLP_DISPONIBLE or not PYGAME_DISPONIBLE:
            self.funcion_chat(self.nombre, "Faltan las librerías 'yt-dlp' o 'pygame'.")
            return

        # 1. Comprobar si ya existe en la biblioteca local
        titulo_guardado, ruta_guardada = self._buscar_en_biblioteca(busqueda)
        if ruta_guardada:
            self.funcion_chat(self.nombre, f"📁 Canción encontrada en almacenamiento local: '{titulo_guardado}'")
            self._reproducir_archivo(titulo_guardado, ruta_guardada)
            return

        # 2. Descargar con yt-dlp manteniendo las cookies e historial técnico intacto
        self.funcion_chat(self.nombre, f"🔎 Descargando audio para: '{busqueda}'...")

        opciones_ytdlp = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.dir_musica, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch1:',
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
                    datos = info['entries'][0]
                else:
                    datos = info

                titulo = datos.get('title', busqueda)
                nombre_sanitizado = re.sub(r'[\\/*?:"<>|]', "", titulo)
                archivo_esperado = os.path.join(self.dir_musica, f"{nombre_sanitizado}.mp3")

                # Localizar el archivo descargado final
                if not os.path.exists(archivo_esperado):
                    for f in os.listdir(self.dir_musica):
                        if f.endswith(".mp3") and nombre_sanitizado[:15].lower() in f.lower():
                            archivo_esperado = os.path.join(self.dir_musica, f)
                            break

                if os.path.exists(archivo_esperado):
                    self._guardar_en_biblioteca(busqueda, titulo, archivo_esperado)
                    self._reproducir_archivo(titulo, archivo_esperado)
                else:
                    self.funcion_chat(self.nombre, "❌ No se pudo localizar el archivo de audio procesado.")

        except Exception as e:
            self.funcion_chat(self.nombre, f"Error al procesar la solicitud: {str(e)}")

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
                model=ollama_model,
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