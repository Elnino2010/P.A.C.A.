import threading
import time
import psutil
import customtkinter as ctk
from base import PluginBase

class PluginStatusHardware(PluginBase):
    def __init__(self):
        super().__init__()
        self.ejecutando = False
        self.hilo_monitor = None

    @property
    def nombre(self) -> str:
        return "Estado Hardware"

    

    @property
    def descripcion(self) -> str:
        return "Muestra el estado del hardware del sistema, incluyendo el uso de CPU y RAM. No tiene interacción directa con el usuario."

    def cargar_ui(self, frame_espacio, funcion_chat, app=None):
        self.frame_espacio = frame_espacio
        self.funcion_chat = funcion_chat
        
        # Frame contenedor de la barra de estado
        self.contenedor_status = ctk.CTkFrame(self.frame_espacio, fg_color="transparent")

        # Labels de lectura (solo CPU y RAM)
        self.lbl_cpu = ctk.CTkLabel(
            self.contenedor_status, 
            text="CPU: 0%", 
            font=("Consolas", 12, "bold"), 
            text_color="#00FF9D"
        )
        self.lbl_cpu.pack(side="left", padx=20)

        self.lbl_ram = ctk.CTkLabel(
            self.contenedor_status, 
            text="RAM: 0%", 
            font=("Consolas", 12, "bold"), 
            text_color="#00F0FF"
        )
        self.lbl_ram.pack(side="left", padx=20)

    def al_activar(self):
        self.contenedor_status.pack(fill="x", pady=5)
        self.ejecutando = True
        
        # Inicia hilo en segundo plano para no congelar la UI
        self.hilo_monitor = threading.Thread(target=self._actualizar_metricas, daemon=True)
        self.hilo_monitor.start()

    def al_desactivar(self):
        self.ejecutando = False
        self.contenedor_status.pack_forget()

    def _actualizar_metricas(self):
        """Bucle que lee CPU y RAM cada 1.5 segundos"""
        while self.ejecutando:
            uso_cpu = psutil.cpu_percent(interval=1)
            uso_ram = psutil.virtual_memory().percent

            # Actualiza la interfaz desde el hilo de forma segura
            if self.ejecutando and hasattr(self, 'lbl_cpu'):
                self.lbl_cpu.configure(text=f"CPU: {uso_cpu}%")
                self.lbl_ram.configure(text=f"RAM: {uso_ram}%")

            time.sleep(0.5)

    def procesar_comando(self, texto: str):
        if "status" in texto.lower() or "hardware" in texto.lower():
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.funcion_chat(self.nombre, f"Diagnóstico: CPU al {cpu}% | RAM al {ram}%")