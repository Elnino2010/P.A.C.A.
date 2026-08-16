from abc import ABC, abstractmethod

class PluginBase(ABC):
    def __init__(self):
        self.activo = False

    @property
    @abstractmethod
    def nombre(self) -> str:
        pass

    @property
    def descripcion(self) -> str:
        """Una breve descripción de lo que hace el plugin para que el Orquestador lo entienda."""
        return "Sin descripción disponible."

    @property
    def acepta_comandos_directos(self) -> bool:
        """Define si este plugin aparecerá en el menú desplegable del chat.
        Por defecto es False para que solo lo activen los que lo necesiten."""
        return False

    @abstractmethod
    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        """
        app: La referencia a la ventana principal InterfazJarvis
        """
        pass

    @abstractmethod
    def procesar_comando(self, texto: str):
        """Se ejecuta cuando el usuario envía un mensaje al canal 'General'"""
        pass

    def procesar_comando_directo(self, texto: str):
        """Se ejecuta SOLO cuando el usuario selecciona este plugin en el desplegable"""
        pass

    def al_activar(self):
        """Se llama automáticamente cuando el usuario ACTIVA el plugin"""
        pass

    def al_desactivar(self):
        """Se llama automáticamente cuando el usuario DESACTIVA el plugin"""
        pass