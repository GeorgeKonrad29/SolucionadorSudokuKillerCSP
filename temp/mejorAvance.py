#solucionador de sudoku con forward checking
#para cambiar el board que se quiere leer cambiar al nombre
#deseado en la linea 163, para deshabilitar verbose en la 162.
#Los archivos de tablero se encuentran en la carpeta boards.
#todos de dificultad imposible.
#autores:
#Nicolas López Hernandez- 1088238419
#Jorge Luis López Grajales- 1037580544

#Se importa la biblioteca os para el manejo de archivos.
import os
import copy
from itertools import product

def generar_combinaciones_dominios(suma_objetivo, dominios):
    def valid_combination(comb):
        return sum(comb) == suma_objetivo

    return [comb for comb in product(*dominios) if valid_combination(comb)]


columnas = "ABCDEFGHI"
filas = {i for i in range(1, 10)}

#inicializa los valores donde se iteran letras con numeros dando A1 hasta I9.
def inicializar_valores():
    valores = {}
    for col in columnas:
        for fil in filas:
            valores[f"{col}{fil}"] = filas.copy()
    return valores

#crean las restricciones del tablero por filas columnas y subcuadros de 3x3.
def crear_restricciones():
    restricciones = []
    # Revisión columnas en filas, se itera (A1 A2 A3... B1 B2....)
    for col in columnas:
        valores_set = set()
        for fil in filas:
            valores_set.add(f"{col}{fil}")
        restricciones.append(valores_set)

    # Revisión filas en columnas, se itera (A1 B1 C1... A2 B2 C2)
    for fil in filas:
        valores_set = set()
        for col in columnas:
            valores_set.add(f"{col}{fil}")
        restricciones.append(valores_set)

    # Creación de restricciones para los recuadros 3x3
    for i in range(3):
        for j in range(3):
            valores_set = set()
            # Calcular la posición inicial del recuadro
            for k in range(3):
                for l in range(3):
                    fila = i * 3 + k + 1
                    columna = chr(j * 3 + l + ord('A')) 
                    valores_set.add(f"{columna}{fila}") # Agregar la celda al conjunto
            restricciones.append(valores_set)

    return restricciones


def cargar_restricciones_sumatoria(archivo):
    restriccionesSum = []
    filePath = os.path.join(os.path.dirname(__file__), 'sumatorias', archivo)
    print(f"Cargando restricciones de sumatoria desde: {filePath}")
    if not os.path.isfile(filePath):
        print(f"Archivo no encontrado: {filePath}")
        return False
    
    with open(filePath) as fd:
        for line in fd:
            parts = line.strip().split(', ')
            sumatoria = int(parts[0])
            celdas = parts[1:]
            restriccionesSum.append({sumatoria: celdas})
    
    return restriccionesSum

# Ejemplo de uso
def nuevoset(value):
    nuevoset= {int(value[i]) for i in range(len(value))}
    return nuevoset 
#carga el archivo de los valores del tablero y asigna los valores a cada iteracion
def cargar_tablero(valores, archivo):
    filePath = os.path.join(os.path.dirname(__file__), 'boards', archivo)
    print(f"Loading board from: {filePath}")  # Mensaje de depuración.
    if not os.path.isfile(filePath):
        print(f"File not found: {filePath}")
        return False #Si no carga devuelve false.
    with open(filePath) as fd:
        for fil in filas:
            for col in columnas:
                value = fd.readline().strip()
                valores[f"{col}{fil}"] = nuevoset(value)
    return True #Si carga devueve true.

#carga el archivo de los valores de sumatoria del tablero y asigna los valores a cada iteracion
def cargar_sumatoria(valores, archivo):
    filePath = os.path.join(os.path.dirname(__file__), 'sumatorias', archivo)
    print(f"Cargando sumas objetivo del tablero desde: {filePath}")
    if not os.path.isfile(filePath):
        print(f"Archivo no encontrado: {filePath}")
        return False
    
    with open(filePath) as fd:
        for col in columnas:
            for fil in filas:
                celda = f"{col}{fil}"
                suma_objetivo = int(fd.readline().strip())
                if suma_objetivo > 0:
                    valores[celda] = suma_objetivo
    
    return True 

#aplicacion de restricciones al tablero cargado
def aplicar_restricciones(valores, restricciones, restriccionesSum, verbose=False):
    if verbose:
        print("[INFO] Aplicando restricciones")

    valores_copy = {k: v.copy() for k, v in valores.items()}
    any_change = True
    while any_change:
        any_change = False
        for cons in restricciones:
            for key in cons:
                if len(valores[key]) == 1:
                    value = list(valores[key])[0]
                    if verbose:
                        print(f"[INFO] celda {key} se ha fijado en el valor {value}")
                    for keydeleted in cons:
                        if keydeleted != key and value in valores[keydeleted]:
                            if verbose:
                                print(f"[INFO] Eliminando valor {value} de la celda {keydeleted}")
                            valores[keydeleted].discard(value)
                            if len(valores[keydeleted]) == 0:
                                if verbose:
                                    print(f"[ERROR] Inconsistencia encontrada en la celda {keydeleted}. Restaurando valores...")
                                valores.update(valores_copy)
                                return False
                            any_change = True
        
        # Verificar restricciones de sumatoria
        for restriccion in restriccionesSum:
            for suma_objetivo, celdas in restriccion.items():
                suma_actual = 0
                celdas_no_asignadas = []
                for celda in celdas:
                    if len(valores[celda]) == 1:
                        suma_actual += list(valores[celda])[0]
                    else:
                        celdas_no_asignadas.append(celda)
                if suma_actual > suma_objetivo:
                    if verbose:
                        print(f"[ERROR] Inconsistencia encontrada en la sumatoria {suma_objetivo}. Restaurando valores...")
                    valores.update(valores_copy)
                    return False
                if len(celdas_no_asignadas) == 1:
                    remaining_value = suma_objetivo - suma_actual
                    celda = celdas_no_asignadas[0]
                    if remaining_value in valores[celda]:
                        valores[celda] = {remaining_value}
                        if verbose:
                            print(f"[INFO] Asignando valor {remaining_value} a la celda {celda} basado en la sumatoria {suma_objetivo}")
                        any_change = True
                    else:
                        if verbose:
                            print(f"[ERROR] Inconsistencia encontrada en la celda {celda} para la sumatoria {suma_objetivo}. Restaurando valores...")
                        valores.update(valores_copy)
                        return False
    return True
#imprime el tablero
def imprimir_tablero(valores):
    for fil in filas:
        print(' '.join(str(list(valores[f"{col}{fil}"])[0]) if len(valores[f"{col}{fil}"]) == 1 else '.' for col in columnas))
def seleccionar_sumatoria(restriccionesSum, valores):
    min_len = float('inf')
    min_sum = None
    for restriccion in restriccionesSum:
        for suma_objetivo, celdas in restriccion.items():
            celdas_no_asignadas = [celda for celda in celdas if len(valores[celda]) > 1]
            if 0 < len(celdas_no_asignadas) < min_len:
                min_len = len(celdas_no_asignadas)
                min_sum = (suma_objetivo, celdas)
    return min_sum
#funcion de busqueda(variacion de backtraking).
def forward_checking(valores, restricciones, restriccionesSum, verbose=False):
    mejor_solucion = None

    def es_consistente(valores, restricciones, restriccionesSum):
        for cons in restricciones:
            seen = set()
            for key in cons:
                if len(valores[key]) == 1:
                    value = list(valores[key])[0]
                    if value in seen:
                        return False
                    seen.add(value)
        for restriccion in restriccionesSum:
            for suma_objetivo, celdas in restriccion.items():
                suma_actual = 0
                celdas_no_asignadas = 0
                for celda in celdas:
                    if len(valores[celda]) == 1:
                        suma_actual += list(valores[celda])[0]
                    else:
                        celdas_no_asignadas += 1
                if suma_actual > suma_objetivo or (celdas_no_asignadas == 0 and suma_actual != suma_objetivo):
                    return False
        return True

    def forward_check(valores, restricciones, restriccionesSum):
        nonlocal mejor_solucion
        sumatoria = seleccionar_sumatoria(restriccionesSum, valores)
        if sumatoria is None:
            if verbose:
                print("[INFO] Solucion encontrada")
            mejor_solucion = {k: v.copy() for k, v in valores.items()}
            return True  # Return True to indicate that a solution has been found

        suma_objetivo, celdas = sumatoria
        dominios = [list(valores[celda]) for celda in celdas]
        if dominios.__len__() >= 4:
            print(dominios)
        combinaciones = generar_combinaciones_dominios(suma_objetivo, dominios)
        for combinacion in combinaciones:
            valores_copia = {k: v.copy() for k, v in valores.items()}
            for i, celda in enumerate(celdas):
                valores_copia[celda] = {combinacion[i]}
            if verbose:
                print(f"[INFO] Intentando asignar {combinacion} a las celdas {celdas}")
            if es_consistente(valores_copia, restricciones, restriccionesSum):
                if aplicar_restricciones(valores_copia, restricciones,restriccionesSum, verbose):
                    if forward_check(valores_copia, restricciones, restriccionesSum):
                        return True  # Return True to indicate that a solution has been found

        if mejor_solucion is None or contar_celdas_asignadas(valores) > contar_celdas_asignadas(mejor_solucion):
            mejor_solucion = {k: v.copy() for k, v in valores.items()}

        return False  # Return False to indicate that no solution was found in this branch

    def contar_celdas_asignadas(valores):
        return sum(1 for v in valores.values() if len(v) == 1)

    if verbose:
        print("[INFO] Iniciando forward checking...")

    forward_check(valores, restricciones, restriccionesSum)
    return mejor_solucion

def main():
    valores = inicializar_valores()
    restricciones = crear_restricciones()
    archivo_sumatoria = "KL5BBDBOsum"
    restriccionesSum = cargar_restricciones_sumatoria(archivo_sumatoria)
    verbose = False
    if not cargar_tablero(valores, "KL5BBDBO"):
        print("Error: El archivo del tablero no se encontró.")
        exit(1)

    if verbose:
        print("Tablero encontrado.")

    mejor_solucion = forward_checking(valores, restricciones, restriccionesSum, verbose)
    if mejor_solucion:
        imprimir_tablero(mejor_solucion)  # Imprimir la solución más avanzada
    else:
        print("No solution exists")
        imprimir_tablero(valores)  # Imprimir el estado actual del tablero

if __name__ == "__main__":
    main()