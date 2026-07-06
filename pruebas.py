import os

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
                f_indice.write(f"-- Título: {nombre_archivo} -- Etiqueta: [{etiqueta_encontrada}]\n")

print("¡Índice generado con éxito!")