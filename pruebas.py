texto = "inicio/este es el texto oculto/final"

# Rompemos el string usando la barra invertida como separador
partes = texto.split("/")

# Verás que partes[1] contiene lo que estaba en medio
print(partes[1])  # Resultado: este es el texto oculto
print(texto)
for parte in range(0, len(partes)+1, 2):
    print(partes[parte])