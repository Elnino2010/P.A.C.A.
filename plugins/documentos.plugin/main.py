import os
import sys
import subprocess
import platform
import customtkinter as ctk
from base import PluginBase

class PluginGestorArchivos(PluginBase):
    def __init__(self):
        super().__init__()
        self.ventana_gestor = None

    @property
    def nombre(self) -> str:
        return "Gestor de Archivos"

    @property
    def descripcion(self) -> str:
        return "Permite explorar y abrir archivos y carpetas desde la interfaz de Jarvis. Usa comandos desde el chat como 'abrir' o 'buscar' para navegar directamente a rutas específicas. También funciona si se le pone unicamente la ruta de un archivo o carpeta en el chat General."

    @property
    def acepta_comandos_directos(self) -> bool:
        return True  # Activado para poder pasarle rutas por chat si quieres

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        self.app = app

    def al_activar(self):
        # Botón en el panel inferior para desplegar la ventana
        self.btn_abrir = ctk.CTkButton(
            self.frame_espacio,
            text="Abrir Explorador",
            font=("Consolas", 12, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_color="#00F0FF",
            border_width=1,
            command=self.abrir_ventana_explorador
        )
        self.btn_abrir.pack(side="left", padx=10, pady=5)

    def al_desactivar(self):
        if hasattr(self, 'btn_abrir') and self.btn_abrir:
            self.btn_abrir.destroy()
            
        # Si la ventana emergente está abierta al desactivar el plugin, la cerramos
        if self.ventana_gestor and self.ventana_gestor.winfo_exists():
            self.ventana_gestor.destroy()

    def abrir_ventana_explorador(self, ruta_inicial=None):
        """Crea o enfoca la ventana secundaria del explorador"""
        if self.ventana_gestor and self.ventana_gestor.winfo_exists():
            self.ventana_gestor.focus()
            if ruta_inicial and os.path.exists(ruta_inicial):
                self.cargar_directorio(ruta_inicial)
            return

        self.ventana_gestor = ctk.CTkToplevel(self.app)
        self.ventana_gestor.title("P.A.C.A. - Explorador de Archivos")
        self.ventana_gestor.geometry("650x450")
        self.ventana_gestor.attributes("-topmost", True)

        # --- NAVEGACIÓN Y RUTA ---
        frame_top = ctk.CTkFrame(self.ventana_gestor, fg_color="transparent")
        frame_top.pack(fill="x", padx=10, pady=10)

        self.entry_ruta = ctk.CTkEntry(frame_top, font=("Consolas", 12))
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_ruta.bind("<Return>", lambda e: self.cargar_directorio(self.entry_ruta.get()))

        btn_ir = ctk.CTkButton(
            frame_top, 
            text="Ir", 
            width=50, 
            font=("Consolas", 12, "bold"),
            command=lambda: self.cargar_directorio(self.entry_ruta.get())
        )
        btn_ir.pack(side="right")

        # --- LISTA DE ARCHIVOS Y CARPETAS ---
        self.scroll_lista = ctk.CTkScrollableFrame(self.ventana_gestor, label_text="Contenido del Directorio")
        self.scroll_lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Cargar ruta inicial o Home por defecto
        inicio = ruta_inicial if (ruta_inicial and os.path.exists(ruta_inicial)) else os.path.expanduser("~")
        self.cargar_directorio(inicio)

    def cargar_directorio(self, ruta: str):
        """Lee el contenido de un directorio y renderiza los elementos"""
        ruta_abs = os.path.abspath(ruta)
        
        if not os.path.exists(ruta_abs) or not os.path.isdir(ruta_abs):
            self.funcion_chat(self.nombre, f"La ruta no existe o no es una carpeta: {ruta_abs}")
            return

        self.entry_ruta.delete(0, "end")
        self.entry_ruta.insert(0, ruta_abs)

        # Limpiar lista anterior
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        # Botón para subir de nivel (..)
        padre = os.path.dirname(ruta_abs)
        if padre != ruta_abs:
            btn_atras = ctk.CTkButton(
                self.scroll_lista,
                text=" .. (Subir de nivel)",
                anchor="w",
                fg_color="transparent",
                text_color="#00F0FF",
                hover_color="#1F293D",
                command=lambda p=padre: self.cargar_directorio(p)
            )
            btn_atras.pack(fill="x", pady=2)

        try:
            elementos = os.listdir(ruta_abs)
            elementos.sort(key=lambda s: (not os.path.isdir(os.path.join(ruta_abs, s)), s.lower()))

            for item in elementos:
                path_completo = os.path.join(ruta_abs, item)
                es_carpeta = os.path.isdir(path_completo)
                icono = "📁" if es_carpeta else "📄"

                btn_item = ctk.CTkButton(
                    self.scroll_lista,
                    text=f"{icono} {item}",
                    anchor="w",
                    fg_color="transparent",
                    text_color="#E2E8F0" if not es_carpeta else "#00FF9D",
                    hover_color="#1E293B",
                    command=lambda p=path_completo, d=es_carpeta: self._al_hacer_clic(p, d)
                )
                btn_item.pack(fill="x", pady=1)

            self.scroll_lista._parent_canvas.yview_moveto(0.0)

        except Exception as err:
            self.funcion_chat(self.nombre, f"Error al leer carpeta: {err}")

    def _al_hacer_clic(self, ruta: str, es_carpeta: bool):
        if es_carpeta:
            self.cargar_directorio(ruta)
        else:
            self.abrir_en_sistema(ruta)

    def abrir_en_sistema(self, ruta: str):
        """Abre un archivo o carpeta en el explorador/programa nativo del S.O."""
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", ruta])
            else:  # Linux y otros UNIX
                subprocess.Popen(["xdg-open", ruta])
            
            self.funcion_chat(self.nombre, f"Abierto en el sistema: {os.path.basename(ruta)}")
        except Exception as e:
            self.funcion_chat(self.nombre, f"Error al abrir archivo: {e}")

    def procesar_comando(self, texto: str):
        # Si se escribe una ruta directamente en el chat General o se pide abrir
        if texto.startswith("/") or texto.startswith("C:\\") or texto.startswith("~"):
            if os.path.exists(texto):
                self.abrir_ventana_explorador(texto)

    def procesar_comando_directo(self, texto: str):
        # Si seleccionan el plugin en el desplegable y le pasan la ruta
        ruta = texto.strip().strip('"\'')
        if os.path.exists(ruta):
            if os.path.isfile(ruta):
                self.abrir_en_sistema(ruta)
            else:
                self.abrir_ventana_explorador(ruta)
        else:
            self.funcion_chat(self.nombre, f"Ruta no encontrada: {ruta}")