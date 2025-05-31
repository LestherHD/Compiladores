import re

def detectar_lenguaje(codigo):
    """
    Determina el lenguaje del código fuente.
    Si encuentra "public class" o "System.out.println" se asume Java;
    si encuentra "#include" o "typedef struct" o "int main(" se asume C.
    """
    if "public class" in codigo or "System.out.println" in codigo:
        return "Java"
    elif "#include" in codigo or "typedef struct" in codigo or "int main(" in codigo:
        return "C"
    return "Desconocido"

# ----------------- Traducción de Java --> C -----------------
def remove_class_block(codigo, class_name):
    """
    Remueve el bloque (definido por llaves) de la inner class con nombre class_name.
    Se asume que aparece como: static class <class_name> { ... }
    """
    pattern = r'static\s+class\s+' + re.escape(class_name) + r'\s*\{'
    match = re.search(pattern, codigo)
    if not match:
        return codigo
    start = match.start()
    index = match.end()
    brace_count = 1  # ya encontró la primera '{'
    while index < len(codigo) and brace_count > 0:
        if codigo[index] == '{':
            brace_count += 1
        elif codigo[index] == '}':
            brace_count -= 1
        index += 1
    return codigo[:start] + codigo[index:]

def traducir_a_c(codigo_java):
    """
    Transforma el código Java en código C, asumiendo el ejemplo de una clase Biblioteca
    con una inner class Libro. Se realizan estas tareas:
      • Se quitan las líneas de importación de Java.
      • Se remueve el bloque completo de la inner class (Libro), ya que definiremos en C su typedef.
      • Se elimina la envoltura de la clase externa (por ejemplo, "public class Biblioteca { … }").
      • Se transforma la firma del main para que sea "int main() {".
      • Se convierte la creación del objeto Libro a asignaciones con strcpy() y se fija el valor de disponibilidad.
      • Se reemplaza la impresión de System.out.println por un printf().
      • Se agregan los includes estándar de C y se inserta de forma fija la definición de la estructura Libro y las funciones prestar() y devolver().
    """
    # 1. Eliminar importación de java.util.*
    codigo_java = re.sub(r"import\s+java\.util\.\*;\s*", "", codigo_java)
    
    # 2. Remover el bloque de la inner class "Libro"
    codigo_java = remove_class_block(codigo_java, "Libro")
    
    # 3. Remover la envoltura de la clase externa (Biblioteca)
    codigo_java = re.sub(r"public\s+class\s+\w+\s*\{", "", codigo_java)
    codigo_java = re.sub(r"}\s*$", "", codigo_java)
    
    # 4. Transformar la firma del main
    codigo_java = re.sub(r"public\s+static\s+void\s+main\s*\(String\[\]\s*args\)\s*\{",
                         "int main() {", codigo_java)
    
    # 5. Convertir la creación del objeto Libro.
    # De:
    #    Libro libro1 = new Libro("1984", "George Orwell");
    # A:
    #    Libro libro1;
    #    strcpy(libro1.titulo, "1984");
    #    strcpy(libro1.autor, "George Orwell");
    #    libro1.disponible = 1;
    codigo_java = re.sub(
        r'Libro\s+(\w+)\s*=\s*new\s+Libro\("([^"]+)",\s*"([^"]+)"\);',
        r'Libro \1;\n    strcpy(\1.titulo, "\2");\n    strcpy(\1.autor, "\3");\n    \1.disponible = 1;',
        codigo_java
    )
    
    # 6. Reemplazar System.out.println(...) por printf con formato
    codigo_java = re.sub(
        r'System\.out\.println\("Libro: "\s*\+\s*(\w+)\.titulo\s*\+\s*", Autor: "\s*\+\s*\1\.autor\);',
        r'printf("Libro: %s, Autor: %s\\n", \1.titulo, \1.autor);',
        codigo_java
    )
    
    # 7. Limpiar espacios sobrantes y quitar la llave de cierre extra del main
    codigo_java = codigo_java.strip()
    codigo_java = re.sub(r"\n?\}$", "", codigo_java)
    
    # 8. Definir los includes y la definición fija de la estructura Libro y sus funciones
    includes = ("#include <stdio.h>\n"
                "#include <stdlib.h>\n"
                "#include <string.h>\n\n")
    struct_libro = (
        "typedef struct {\n"
        "    char titulo[100];\n"
        "    char autor[100];\n"
        "    int disponible; // 1 = disponible, 0 = no disponible\n"
        "} Libro;\n\n"
        "void prestar(Libro *libro) {\n"
        "    libro->disponible = 0;\n"
        "}\n\n"
        "void devolver(Libro *libro) {\n"
        "    libro->disponible = 1;\n"
        "}\n\n"
    )
    
    final_code = includes + struct_libro + codigo_java + "\n    return 0;\n}\n"
    return final_code

# ----------------- Traducción de C --> Java -----------------
def traducir_a_java(codigo_c):
    """
    Convierte código C en código Java (para el ejemplo de Libro).
    Se realizan estos pasos:
      • Se eliminan los #include.
      • Se remueve el bloque typedef struct (que define Libro).
      • Se transforma la firma del main: "int main()" se convierte en "public static void main(String[] args)".
      • Se reemplazan las llamadas a strcpy(...) por comentarios que indiquen que se asigna el valor.
      • Se transforma el printf() en una llamada a System.out.println().
      • Se envuelve el resultado en una clase (por ejemplo, Traducido) y se agrega una definición fija de la clase Libro.
    """
    # 1. Eliminar líneas de #include
    codigo_c = re.sub(r"#include\s*<[^>]+>\n", "", codigo_c)
    
    # 2. Remover el bloque typedef struct para Libro (asumimos que aparece completo)
    codigo_c = re.sub(r"typedef\s+struct\s*\{.*?\}\s*\w+;\n", "", codigo_c, flags=re.DOTALL)
    
    # 3. Transformar la firma de main
    codigo_c = re.sub(r"int main\(\)\s*\{", "public static void main(String[] args) {", codigo_c)
    
    # 4. Convertir llamadas a strcpy() en comentarios (ya que en Java las cadenas se asignan directamente)
    codigo_c = re.sub(r'strcpy\((\w+)\.titulo,\s*"([^"]+)"\);', r'// asignar \1.titulo = "\2"', codigo_c)
    codigo_c = re.sub(r'strcpy\((\w+)\.autor,\s*"([^"]+)"\);', r'// asignar \1.autor = "\2"', codigo_c)
    
    # 5. Transformar printf en System.out.println; se asume un formato específico.
    codigo_c = re.sub(r'printf\("([^"]+)"\s*,\s*(\w+)\.titulo\s*,\s*(\w+)\.autor\);',
                      r'System.out.println("Libro: " + \2.titulo + ", Autor: " + \3.autor);', codigo_c)
    
    # 6. Eliminar "return 0;"
    codigo_c = codigo_c.replace("return 0;", "")
    
    # 7. Definición fija de la clase Libro en Java (para este ejemplo)
    libro_def = (
        "public static class Libro {\n"
        "    String titulo;\n"
        "    String autor;\n"
        "    boolean disponible;\n\n"
        "    public Libro(String titulo, String autor) {\n"
        "        this.titulo = titulo;\n"
        "        this.autor = autor;\n"
        "        this.disponible = true;\n"
        "    }\n"
        "}\n\n"
    )
    
    # 8. Agregar un wrapper para generar la clase Java final
    codigo_java = "import java.util.*;\n\n" + libro_def + "public class Traducido {\n" + codigo_c + "\n}\n"
    return codigo_java

# ----------------- Función principal -----------------
def main():
    # Código fuente de ejemplo en Java
    codigo_java = """

"""
    # Código fuente de ejemplo en C
    codigo_c = """
#include<iostream.h>
#include<conio.h>

void main(){
    char a[100];
    int b, c;

    do{
        clrscr();
        c = 0;
        cout << "Ingrese numero:"; 
        cin >> a;
        b = strlen(a);

        if(a[0] == a[3] && a[1] == a[2]){
            c = 1;
        }
    } while(b != 4 || c != 1);
    cout << endl << "            El numero es capicua!!";
    getch();
}
"""
    # Detectar y traducir según el código fuente
    lang1 = detectar_lenguaje(codigo_java)
    print("Lenguaje detectado (codigo_java):", lang1)
    if lang1 == "Java":
        print("\n--- Traducción (Java --> C) ---")
        codigo_c_resultado = traducir_a_c(codigo_java)
        print(codigo_c_resultado)
    else:
        print("El código fuente Java no es válido.")
    
    print("\n--------------------------------\n")
    
    lang2 = detectar_lenguaje(codigo_c)
    print("Lenguaje detectado (codigo_c):", lang2)
    if lang2 == "C":
        print("\n--- Traducción (C --> Java) ---")
        codigo_java_resultado = traducir_a_java(codigo_c)
        print(codigo_java_resultado)
    else:
        print("El código fuente C no es válido.")

if __name__ == "__main__":
    main()