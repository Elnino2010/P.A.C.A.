import threading
import pyttsx3
from base import PluginBase

class PluginVoz(PluginBase):
    def __init__(self):
        super().__init__()
        self.engine_lock = threading.Lock()

    @property
    def nombre(self) -> str:
        return "Voz (TTS)"

    @property
    def descripcion(self) -> str:
        return "Plugin que permite a JARVIS hablar en voz alta utilizando la síntesis de voz (TTS). No usa comandos directos."

    @property
    def acepta_comandos_directos(self) -> bool:
        return False

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.app = app
        
        # Intercepta la función del chat original
        self.funcion_chat_original = funcion_chat
        
        # Inyecta la versión wrapper que detecta cuándo habla el sistema/JARVIS
        if app is not None:
            app.enviar_mensaje_chat = self.enviar_mensaje_chat_interceptado

    def enviar_mensaje_chat_interceptado(self, emisor: str, mensaje: str):
        #Ejecutamos la función original para que se pinte en pantalla
        self.funcion_chat_original(emisor, mensaje)

        # Si el plugin está activo y el mensaje no es del Usuario, lo leemos en voz alta
        if self.activo and emisor.upper() != "USUARIO":
            threading.Thread(target=self._hablar, args=(mensaje,), daemon=True).start()

    def _hablar(self, texto: str):
        """Inicializa y reproduce la voz en un hilo secundario para evitar congelar la interfaz."""
        if not texto or not texto.strip():
            return

        with self.engine_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 165)  # Velocidad de lectura

                # Configurar voz en español si está disponible
                voices = engine.getProperty("voices")
                for voice in voices:
                    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
                        engine.setProperty("voice", voice.id)
                        break

                engine.say(texto)
                engine.runAndWait()
            except Exception as e:
                print(f"[Voz TTS Error]: {e}")

    def procesar_comando(self, texto: str):
        # Este plugin solo escucha las respuestas, no requiere comandos de texto
        pass

    def al_activar(self):
        threading.Thread(target=self._hablar, args=("Módulo de voz activado.",), daemon=True).start()

    def al_desactivar(self):
        pass