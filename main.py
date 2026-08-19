import os
import json
import importlib.util
import inspect
import customtkinter as ctk
from base import PluginBase

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InterfazJarvis(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("P.A.C.A.")
        self.geometry("950x600")
        
        self.panel_lateral = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.panel_lateral.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.panel_lateral, text="MÓDULOS", font=("Courier", 18, "bold")).pack(pady=20)

        self.area_derecha = ctk.CTkFrame(self, fg_color="transparent")
        self.area_derecha.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.chat_log = ctk.CTkTextbox(self.area_derecha, font=("Courier", 14), text_color="#00FF00")
        self.chat_log.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_log.insert("end", "SISTEMA INICIADO CON ÉXITO. ESPERANDO ÓRDENES...\n" + "-"*40 + "\n")
        self.chat_log.configure(state="disabled")

        self.espacio_plugins = ctk.CTkFrame(self.area_derecha, height=150)
        self.espacio_plugins.pack(fill="x", pady=(0, 10))
        
        self.barra_inferior = ctk.CTkFrame(self.area_derecha, fg_color="transparent")
        self.barra_inferior.pack(fill="x")
        
        # Menú desplegable para seleccionar el destino del mensaje
        self.opcion_destino = ctk.CTkOptionMenu(
            self.barra_inferior, 
            values=["General (Todos)"], 
            font=("Courier", 12),
            width=150
        )
        self.opcion_destino.pack(side="left", padx=(0, 10))

        self.entrada_texto = ctk.CTkEntry(self.barra_inferior, placeholder_text="Introducir comando...", font=("Courier", 14))
        self.entrada_texto.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada_texto.bind("<Return>", self.enviar_comando)
        
        self.btn_enviar = ctk.CTkButton(self.barra_inferior, text="ENVIAR", font=("Courier", 14, "bold"), command=self.enviar_comando)
        self.btn_enviar.pack(side="right")

        self.plugins_cargados = []
        self.cargar_plugins()

    def enviar_mensaje_chat(self, emisor: str, mensaje: str):
        """Inserta líneas visualmente estructuradas para distinguir la procedencia de los mensajes"""
        self.chat_log.configure(state="normal")
        
        tag = emisor.upper()

        # Estructuración por bloques
        if tag == "USUARIO":
            encabezado = f"\n┌─── [USUARIO] " + "─" * 35 + "\n"
            cuerpo = f"│  {mensaje}\n"
            pie = "└──" + "─" * 48 + "\n"
        elif "JARVIS" in tag or "OLLAMA" in tag:
            encabezado = f"\n┌─── [P.A.C.A.] " + "─" * 32 + "\n"
            cuerpo = f"│  {mensaje}\n"
            pie = "└──" + "─" * 48 + "\n"
        elif tag == "SISTEMA":
            encabezado = f"\n[SISTEMA]: {mensaje}\n"
            cuerpo = ""
            pie = ""
        else:
            encabezado = f"\n┌─── [{tag}] " + "─" * (42 - len(tag)) + "\n"
            cuerpo = f"│  {mensaje}\n"
            pie = "└──" + "─" * 48 + "\n"

        self.chat_log.insert("end", encabezado + cuerpo + pie)
        self.chat_log.yview("end")  # Scroll automático
        self.chat_log.configure(state="disabled")

    def actualizar_desplegable(self):
        """Actualiza la lista de plugins disponibles en el menú desplegable"""
        opciones_validas = ["General (Todos)"]
        
        for plugin in self.plugins_cargados:
            # Solo añadimos los que están encendidos y aceptan comandos directos
            if plugin.activo and plugin.acepta_comandos_directos:
                opciones_validas.append(plugin.nombre)
                
        self.opcion_destino.configure(values=opciones_validas)
        
        # Si el plugin seleccionado actualmente se ha apagado, volvemos a 'General'
        if self.opcion_destino.get() not in opciones_validas:
            self.opcion_destino.set("General (Todos)")

    def enviar_comando(self, event=None):
        texto = self.entrada_texto.get().strip()
        if not texto: return
        
        destino = self.opcion_destino.get()
        self.enviar_mensaje_chat("Usuario", f"({destino}) -> {texto}")
        self.entrada_texto.delete(0, "end")

        if destino == "General (Todos)":
            orquestador = next(
                (p for p in self.plugins_cargados if p.nombre == "Orquestador IA" and p.activo), 
                None
            )
            
            if orquestador:
                orquestador.procesar_comando(texto)
            else:
                for plugin in self.plugins_cargados:
                    if plugin.activo:
                        plugin.procesar_comando(texto)
        else:
            for plugin in self.plugins_cargados:
                if plugin.nombre == destino and plugin.activo:
                    plugin.procesar_comando_directo(texto)
                    break

    def toggle_plugin(self, plugin, switch_var):
        plugin.activo = switch_var.get()
        
        if plugin.activo:
            plugin.al_activar()
            estado = "ACTIVADO"
        else:
            plugin.al_desactivar()
            estado = "DESACTIVADO"
            
        self.enviar_mensaje_chat("Sistema", f"Módulo '{plugin.nombre}' {estado}.")
        self.actualizar_desplegable()

    def guardar_catalogo_json(self):
        """Genera/actualiza un archivo JSON con los plugins cargados y sus descripciones."""
        catalogo = []
        for plugin in self.plugins_cargados:
            catalogo.append({
                "nombre": plugin.nombre,
                "descripcion": plugin.descripcion
            })
        
        try:
            with open("plugins.json", "w", encoding="utf-8") as f:
                json.dump(catalogo, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Error al guardar plugins.json]: {e}")
            
    def cargar_plugins(self):
        ruta_plugins = "plugins"
        
        # Si la carpeta 'plugins' no existe, la creamos para evitar errores
        if not os.path.exists(ruta_plugins):
            os.makedirs(ruta_plugins)
            self.enviar_mensaje_chat("Sistema", "Carpeta de plugins creada.")
            return

        # Escaneamos la carpeta
        for elemento in os.listdir(ruta_plugins):
            try:
                path_elemento = os.path.join(ruta_plugins, elemento)

                # Buscamos carpetas que terminen en .plugin
                if os.path.isdir(path_elemento) and elemento.endswith(".plugin"):
                    archivo_main = os.path.join(path_elemento, "main.py")
                
                    if not os.path.exists(archivo_main):
                        self.enviar_mensaje_chat("Sistema", f"Error: {elemento} no tiene main.py")
                        continue

                    # Carga dinámica del módulo
                    nombre_modulo = elemento.replace(".", "_")
                    spec = importlib.util.spec_from_file_location(nombre_modulo, archivo_main)
                    modulo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(modulo)

                    # Buscamos la clase del plugin
                    for nombre, objeto in inspect.getmembers(modulo, inspect.isclass):
                        if issubclass(objeto, PluginBase) and objeto is not PluginBase:
                            plugin_instancia = objeto()
                            self.plugins_cargados.append(plugin_instancia)
                            
                            # Añadimos el plugin a la interfaz lateral con un switch
                            var_estado = ctk.BooleanVar(value=False)
                            switch = ctk.CTkSwitch(
                                self.panel_lateral, 
                                text=plugin_instancia.nombre, 
                                font=("Courier", 12),
                                variable=var_estado,
                                command=lambda p=plugin_instancia, v=var_estado: self.toggle_plugin(p, v)
                            )
                            switch.pack(pady=10, padx=20, anchor="w")
                            
                            # Inyectamos el UI del plugin
                            plugin_instancia.cargar_ui(self.espacio_plugins, self.enviar_mensaje_chat, app=self)
            except Exception as e:
                self.enviar_mensaje_chat("Sistema", f"Error al cargar plugin '{elemento}': {str(e)}")
        self.guardar_catalogo_json()


if __name__ == "__main__":
    app = InterfazJarvis()
    app.mainloop()