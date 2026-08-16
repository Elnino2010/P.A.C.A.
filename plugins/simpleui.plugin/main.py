import customtkinter as ctk
from base import PluginBase

class PluginRedisenoJarvis(PluginBase):
    def __init__(self):
        super().__init__()
        # El plugin se activa automáticamente
        self.activo = True

    @property
    def nombre(self) -> str:
        return "Interfaz JARVIS HUD"

    @property
    def descripcion(self) -> str:
        return "Aplica un rediseño visual de tipo HUD (Heads-Up Display) a la interfaz de JARVIS, mejorando la estética y la usabilidad."

    @property
    def acepta_comandos_directos(self) -> bool:
        return False

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.app = app
        self.funcion_chat = funcion_chat
        
        # Al cargarse la interfaz, se aplica el rediseño
        if self.app:
            self.aplicar_rediseno_completo()

    def al_activar(self):
        # Si se reactiva desde el menú lateral
        if self.app:
            self.aplicar_rediseno_completo()

    def al_desactivar(self):
        # Restaurar apariencia básica por defecto si el usuario decide apagarlo
        if self.app:
            self.restaurar_apariencia_original()

    def aplicar_rediseno_completo(self):
        """Aplica la paleta Cyber-HUD de P.A.C.A. a toda la ventana principal"""
        app = self.app

        # Paleta de colores
        AZUL_NEON = "#00F0FF"
        AZUL_OSCURO_FONDO = "#0A0E17"
        AZUL_PANEL = "#111827"
        AZUL_BORDE = "#1F293D"
        TEXTO_VERDE_TERMINAL = "#00FF9D"

        # Ventana Principal
        app.configure(fg_color=AZUL_OSCURO_FONDO)
        app.title("J.A.R.V.I.S.")

        # Panel Lateral (Módulos)
        app.panel_lateral.configure(
            fg_color=AZUL_PANEL,
            border_width=1,
            border_color=AZUL_BORDE
        )

        # Pantalla de Chat
        app.chat_log.configure(
            fg_color="#050811",
            text_color=TEXTO_VERDE_TERMINAL,
            border_width=2,
            border_color=AZUL_NEON,
            corner_radius=8,
            font=("Consolas", 13, "bold")
        )

        # Marco de Espacio para Plugins inferiores
        app.espacio_plugins.configure(
            fg_color=AZUL_PANEL,
            border_width=1,
            border_color=AZUL_BORDE,
            corner_radius=8
        )

        #  Menú Desplegable
        app.opcion_destino.configure(
            fg_color=AZUL_PANEL,
            button_color=AZUL_BORDE,
            button_hover_color="#1E293B",
            text_color=AZUL_NEON,
            dropdown_fg_color=AZUL_PANEL,
            dropdown_text_color=AZUL_NEON,
            dropdown_hover_color=AZUL_BORDE,
            corner_radius=8,
            font=("Consolas", 12, "bold")
        )

        # Campo de Entrada de Texto
        app.entrada_texto.configure(
            fg_color="#0D131F",
            text_color="#E2E8F0",
            placeholder_text_color="#475569",
            border_color=AZUL_NEON,
            border_width=1,
            corner_radius=8,
            font=("Consolas", 13)
        )

        # Botón de Enviar
        app.btn_enviar.configure(
            fg_color=AZUL_NEON,
            text_color="#0D131F",
            hover_color="#00C4D6",
            corner_radius=8,
            font=("Consolas", 13, "bold")
        )

        # Mensaje de confirmación visual en consola
        self.funcion_chat("SISTEMA VISUAL", "Interfaz HUD JARVIS aplicada automáticamente.")

    def restaurar_apariencia_original(self):
        """Devuelve los componentes a la estética neutra predeterminada"""
        app = self.app
        app.configure(fg_color="#1A1A1A")
        app.title("Sistema Central")
        
        app.panel_lateral.configure(fg_color="#2B2B2B", border_width=0)
        app.chat_log.configure(
            fg_color="#1D1E1E", 
            text_color="#00FF00", 
            border_width=0, 
            corner_radius=0
        )
        app.espacio_plugins.configure(fg_color="#2B2B2B", border_width=0)
        app.entrada_texto.configure(border_color="#565B5E", fg_color="#343638")
        app.btn_enviar.configure(fg_color="#1F6AA5", text_color="#FFFFFF")

    def procesar_comando(self, texto: str):
        pass