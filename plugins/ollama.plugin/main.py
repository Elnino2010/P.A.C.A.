import threading
import ollama
from base import PluginBase
import sys
import os
ruta_plugin = os.path.dirname(__file__)
if ruta_plugin not in sys.path:
    sys.path.append(ruta_plugin)

from memoria import guardar_memoria, acceso_memoria_inteligente, guardar_indice

class JarvisOllamaPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.modelo = 'gemma4:e4b'
        self.historial_mensajes = []
        # Inicializa el índice de memoria al instanciar el plugin
        try:
            guardar_indice()
        except Exception as e:
            print(f"[JarvisOllama] Error inicializando memoria: {e}")

    @property
    def nombre(self) -> str:
        return "JARVIS IA (Ollama)"

    @property
    def descripcion(self) -> str:
        return "Plugin que integra la IA de Ollama para responder preguntas y mantener conversaciones. Cualquier función que no vaya directamente a un plugin irá aquí."

    @property
    def acepta_comandos_directos(self) -> bool:
        # Permite hablarle directamente desde el desplegable
        return True

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.funcion_chat = funcion_chat
        # En este espacio podríamos poner controles si hiciera falta, pero por ahora no requiere botones extra.

    def procesar_comando(self, texto: str):
        # Si llega desde el canal "General", lanzamos el proceso en un hilo
        threading.Thread(target=self._generar_respuesta, args=(texto,), daemon=True).start()

    def procesar_comando_directo(self, texto: str):
        # Si llega desde el desplegable exclusivo, procesamos de la misma forma
        threading.Thread(target=self._generar_respuesta, args=(texto,), daemon=True).start()

    def _generar_respuesta(self, pregunta: str):
        """Método interno que corre en segundo plano (threading) para no congelar la UI"""
        try:
            # 1. Búsqueda o consulta en la memoria temática antes de responder
            contexto_memoria = acceso_memoria_inteligente(pregunta, self.modelo)
            
            # 2. Construimos la consulta para Ollama
            self.historial_mensajes.append({"role": "user", "content": pregunta})

            # 3. Solicitamos la respuesta mediante Stream a Ollama
            respuesta_stream = ollama.chat(model=self.modelo, messages=self.historial_mensajes, stream=True)
            
            texto_completo = ""
            # Mostramos un encabezado inicial en el chat de la GUI
            self.funcion_chat("Jarvis", "Pensando...")

            for chunk in respuesta_stream:
                contenido = chunk.message.content
                texto_completo += contenido

            # Guardamos la respuesta en el historial de la sesión
            self.historial_mensajes.append({"role": "assistant", "content": texto_completo})

            # 4. Publicamos la respuesta final en el chat de CustomTkinter
            self.funcion_chat("Jarvis", texto_completo)

            # 5. Guardamos en el sistema de memoria .md
            guardar_memoria(pregunta, texto_completo)

        except Exception as error:
            self.funcion_chat("Jarvis Error", f"Fallo al conectar con Ollama: {error}")