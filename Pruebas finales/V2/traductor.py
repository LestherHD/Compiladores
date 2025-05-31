import os
import re

def leer_archivo(nombre_archivo):
    """Lee el contenido del archivo de texto."""
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def detectar_lenguaje(codigo):
    """Detecta si el código es C o Java."""
    if "#include" in codigo:
        return "C"
    elif "public class" in codigo:
        return "Java"
    return "Desconocido"

def traducir_a_java(codigo_c):
    """Convierte código en C a Java con formato de clase."""
    traducciones = {
        "printf": "System.out.println",
        "int main()": "public static void main(String[] args)"
    }

    # Eliminar '#include' y 'return 0;'
    codigo_c = re.sub(r"#include.*", "", codigo_c)
    codigo_c = re.sub(r"return\s+0;", "", codigo_c)

    # Aplicar traducciones
    for c_element, j_element in traducciones.items():
        codigo_c = codigo_c.replace(c_element, j_element)

    # Limpiar líneas en blanco
    lineas = [linea.strip() for linea in codigo_c.split("\n") if linea.strip()]

    # Envolver en una clase Java con formato correcto
    codigo_java = "public class Traducido {\n    " + "\n    ".join(lineas) + "\n}"

    return codigo_java.strip()

# Archivo fuente
archivo_fuente = "codigo.txt"
codigo_c = leer_archivo(archivo_fuente)

if codigo_c:
    lenguaje = detectar_lenguaje(codigo_c)
    print(f"Lenguaje detectado: {lenguaje}")

    if lenguaje == "C":
        codigo_java = traducir_a_java(codigo_c)
        print("\nCódigo traducido a Java:")
        print(codigo_java)
    else:
        print("El archivo no contiene código en C.")
else:
    print("No se encontró el archivo fuente.")