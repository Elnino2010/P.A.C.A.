import os
import json
import threading
from base import PluginBase

try:
    import ollama
    OLLAMA_DISPONIBLE = True
except ImportError:
    OLLAMA_DISPONIBLE = False


class PluginOrquestador(PluginBase):
    def __init__(self):
        super().__init__()
        self.ruta_json = "plugins.json"

    @property
    def nombre(self) -> str:
        return "Orquestador IA"

    @property
    def descripcion(self) -> str:
        return "Analiza las órdenes del chat general y las enruta automáticamente al módulo correspondiente usando IA."

    @property
    def acepta_comandos_directos(self) -> bool:
        return False

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        self.app = app

    def procesar_comando(self, texto: str):
        """Se activa al enviar un mensaje al canal 'General (Todos)'"""
        if not OLLAMA_DISPONIBLE:
            return

        # Procesa la decisión de enrutamiento en segundo plano
        threading.Thread(target=self._decidir_y_ejecutar, args=(texto,), daemon=True).start()

    def _cargar_catalogo(self) -> list:
        if os.path.exists(self.ruta_json):
            try:
                with open(self.ruta_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _decidir_y_ejecutar(self, mensaje_usuario: str):
        catalogo = self._cargar_catalogo()
        if not catalogo:
            return

        # Filtra solo los plugins que están activos en la app (excluyendo al propio Orquestador)
        plugins_activos = []
        if self.app:
            for p in self.app.plugins_cargados:
                if p.activo and p.nombre != self.nombre:
                    plugins_activos.append({
                        "nombre": p.nombre,
                        "descripcion": p.descripcion
                    })

        if not plugins_activos:
            return

        system_prompt = f"""
Eres el Orquestador Central del sistema JARVIS.
Tu trabajo es analizar la orden del usuario y decidir qué plugin activo debe ejecutarla.

Lista de plugins activos disponibles actualmente:
{json.dumps(plugins_activos, ensure_ascii=False, indent=2)}

REGLAS DE RESPUESTA:
1. Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
{{
    "destino": "NOMBRE_DEL_PLUGIN" o "JARVIS",
    "comando_limpio": "El texto del comando adaptado si es necesario"
}}
2. Si el mensaje va dirigido a un plugin de la lista, pon exactamente su campo "nombre" en "destino".
3. Si la petición es una conversación general o no encaja con ningún plugin activo, pon "JARVIS" en "destino".
4. Devuelve SOLO el JSON sin bloques de código ni texto explicativo.
"""

        try:
            respuesta = ollama.chat(
                model="gemma4:e4b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensaje_usuario}
                ]
            )

            contenido = respuesta['message']['content'].strip()
            if contenido.startswith("```"): contenido = contenido.split("\n", 1)[1].rsplit("\n", 1)[0]
            if contenido.startswith("json"): contenido = contenido[4:].strip()

            datos = json.loads(contenido)
            destino = datos.get("destino")
            comando = datos.get("comando_limpio", mensaje_usuario)

            # Si el destino es un plugin activo específico, se lo enviamos directamente
            if destino and destino != "JARVIS" and self.app:
                for plugin in self.app.plugins_cargados:
                    if plugin.nombre == destino and plugin.activo:
                        # Si tiene método procesar_comando_directo o procesar_comando
                        plugin.procesar_comando_directo(comando)
                        break

        except Exception as e:
            print(f"[Orquestador Error]: {e}")