#Aquí gestionaremos la memoria del modelo
#Será una memoria tipo bóbeda de obsidian, donde se guardarán los datos en distintos archivos .md con etiquetas que la IA buscará antes de responder y cambiará después de cada respuesta para que la IA pueda aprender de sus errores y mejorar su rendimiento.
import os, ollama, time

#Crearemos una función para guardar un índice con los nombres de los archivos y sus etiquetas para que la IA pueda acceder a ellos y buscar información relevante antes de responder.
def guardar_indice():
    etiquetas = [] # Esto será todo lo que esté entre corchetes []

    # 1. Recorremos los archivos de la carpeta
    for nombre_archivo in os.listdir("Memoria"):
        if nombre_archivo.endswith(".md") and nombre_archivo != "indice.md":
            
            # Abrimos el archivo actual
            with open(os.path.join("Memoria", nombre_archivo), "r", encoding="utf-8") as f:
                
                # Creamos la variable por defecto por si acaso el archivo estuviera vacío
                etiqueta_encontrada = "sin_etiqueta"
                
                # 2. Recorremos línea por línea usando una variable distinta
                for linea in f:
                    linea_limpia = linea.strip() # Quitamos espacios y saltos de línea (\n)
                    
                    # Comprobamos si es la línea de la etiqueta
                    if linea_limpia.startswith("[") and linea_limpia.endswith("]"):
                        etiqueta_encontrada = linea_limpia[1:-1] # Le quitamos los corchetes
                        break # Ya encontramos la etiqueta, podemos dejar de leer este archivo
                etiquetas.append(etiqueta_encontrada)
                # 3. Guardamos en el índice usando las variables correctas
                with open(os.path.join("Memoria", "indice.md"), "w", encoding="utf-8") as f_indice:
                    f_indice.write(f"-- Título: [{nombre_archivo}] -- Etiqueta: [{etiqueta_encontrada}]\n")
    

    
#Función para acceder a la memoria inteligente en cada respuesta de la IA
def acceso_memoria_inteligente():
    print()

#Función para guardar la memoria en un varios archivos .md después de cada respuesta de la IA
def guardar_memoria(pregunta_usuario, respuesta_ia):
    #Primero comprueba que la carpeta "Memoria" exista, si no la crea.
    CARPETA_MEMORIA = "Memoria"
    if not os.path.exists(CARPETA_MEMORIA):
        os.makedirs(CARPETA_MEMORIA)
    
    #Ahora le pasamos la pregunta del usuario y la respuesta de la IA para establecer puntos de memoria y un resumen.
    mresumen = f"""Eres un módulo de extracción de memoria temática. Tu único objetivo es analizar la conversación proporcionada (Pregunta del usuario y Respuesta de la IA) y extraer el tema principal y los puntos clave en un formato estructurado y estricto.

Debes responder ÚNICAMENTE siguiendo esta estructura exacta, sin introducciones, sin saludos y sin texto adicional ni nada que no esté en el formato especificado ya que si lo pones, no se guardará correctamente en la memoria. El formato es el siguiente:

/Título del archivo/
[NOMBRE_DEL_TEMA]
* **Punto clave 1**: Explicación breve y concisa.
* **Punto clave 2**: Explicación breve y concisa.
* **Punto clave 3**: Explicación breve y concisa.

Reglas críticas:
1.El Título del archivo debe ser único y descriptivo, reflejando el tema principal de la conversación. Debe estar en minúsculas, sin espacios (usa guiones bajos si es necesario) y sin la extensión .md (ejemplo: "programacion_python" o "gestion_servidores").
2. El NOMBRE_DEL_TEMA debe ir dentro de los corchetes [], en minúsculas, sin espacios (usa guiones bajos si es necesario) y sin la extensión .md (ejemplo: [programacion_python] o [gestion_servidores]). Debe ser el tema más relevante de la conversación y debe ser exactamente el tema global para que en otro momento pueda ser identificado por cualquiera.
3. El contenido debe estar sintetizado en viñetas claras con formato Markdown, directo al grano.
4. Si la conversación no aporta información útil para almacenar a largo plazo, responde únicamente: [ninguno]

CONVERSACIÓN A ANALIZAR:
Usuario: {pregunta_usuario}
IA: {respuesta_ia}"""
    mensaje_memoria = [{"role": "system", "content": mresumen}]
    respuesta_memoria = ollama.chat(model='gemma4:e4b', messages=mensaje_memoria)
    print(f"Resumen de la memoria: {respuesta_memoria.message.content}")

    #Para prueba, vamos a guardar la conversación en un archivo de texto plano para ver si funciona correctamente.
    partes_resumen = respuesta_memoria.message.content.split("/")
    try:
        for parte in range(1, len(partes_resumen), 2):
            nombre_archivo = f"{CARPETA_MEMORIA}/{partes_resumen[parte]}.md"
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(f"{partes_resumen[parte+1]}")
    except Exception as error:
        print(f"No se guardó en la memoria debido a: {error}")
    guardar_indice()  # Actualizamos el índice después de guardar la memoria