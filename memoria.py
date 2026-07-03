#Aquí gestionaremos la memoria del modelo
import os



#Primero comprueba que la carpeta "Memoria" exista, si no la crea.
CARPETA_MEMORIA = "Memoria"
if not os.path.exists(CARPETA_MEMORIA):
    os.makedirs(CARPETA_MEMORIA)
