import random
import string
import json

participantes = [
    {"nombre": "Emilio", "grupo": "A"},
    {"nombre": "Iris Vargas", "grupo": "A"},
    {"nombre": "Karol", "grupo": "B"},
    {"nombre": "Christian (Grande)", "grupo": "B"},
    {"nombre": "Renato", "grupo": "C"},
    {"nombre": "Eduardo", "grupo": "C"},
    {"nombre": "Martin", "grupo": "C"},
    {"nombre": "Joaquin", "grupo": "D"},
    {"nombre": "Yoyo", "grupo": "D"},
    {"nombre": "Antonio", "grupo": "E"},
    {"nombre": "Iris Hinojosa", "grupo": "E"},
]

# Restricciones por grupo: clave = grupo, valor = lista de grupos a los que no pueden regalar
# El grupo C no regala al E.
restricciones = {
    "C": ["E"],
}

# Límite máximo de intentos para buscar una asignación válida
MAX_INTENTOS = 1000

# Conjunto a nivel de módulo para registrar códigos ya generados (evitar repeticiones)
codigos_generados = set()


def generar_codigo_unico(usados=None, length=4):
    """Genera un código alfanumérico único de `length` caracteres (A-Z, 0-9).

    Parámetros:
    - usados: un `set` opcional de códigos ya usados. Si no se proporciona,
      se usará el conjunto de módulo `codigos_generados`.
    - length: longitud del código (por defecto 4).

    La función intentará generar un código aleatorio y garantizará que no esté
    en `usados`. Añade el código al conjunto `usados` antes de retornarlo.
    Lanza `RuntimeError` si se han agotado todas las combinaciones posibles.
    """
    if usados is None:
        usados = codigos_generados

    alphabet = string.ascii_uppercase + string.digits
    max_combinaciones = len(alphabet) ** length
    if len(usados) >= max_combinaciones:
        raise RuntimeError("No quedan códigos únicos disponibles.")

    while True:
        codigo = ''.join(random.choices(alphabet, k=length))
        if codigo not in usados:
            usados.add(codigo)
            return codigo


def guardar_datos_json(resultado, filename='db_amigo_secreto.json'):
    """Guarda la lista de diccionarios `resultado` en un archivo JSON local.

    Usa UTF-8 y formatea con indentación para facilitar su lectura por la web.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Propagar la excepción para que el llamador pueda manejarla
        raise


def generar_asignaciones(participantes):
    """Mezcla una copia de la lista de participantes y crea parejas cíclicas.

    Cada tupla de la lista resultante tiene la forma (regalador, receptor),
    donde ambos son los diccionarios originales de la lista `participantes`.

    Si la lista está vacía o tiene un solo elemento, devuelve lista vacía.
    """
    if not participantes or len(participantes) < 2:
        return []

    lista = participantes.copy()
    random.shuffle(lista)
    asignaciones = []
    n = len(lista)
    for i in range(n):
        regalador = lista[i]
        receptor = lista[(i + 1) % n]
        asignaciones.append((regalador, receptor))

    return asignaciones


def validar_auto_regalo(asignaciones):
    """Valida que en las asignaciones nadie se regale a sí mismo.

    Recibe `asignaciones` como una lista de tuplas (regalador, receptor),
    donde cada elemento es el diccionario de participante. Retorna `False`
    si existe alguna pareja con la misma persona como regalador y receptor;
    retorna `True` en caso contrario.
    """
    for regalador, receptor in asignaciones:
        # comparar por identidad o por nombre para detectar auto-regalos
        if regalador is receptor:
            return False
        nombre_regalador = regalador.get("nombre") if isinstance(regalador, dict) else None
        nombre_receptor = receptor.get("nombre") if isinstance(receptor, dict) else None
        if nombre_regalador and nombre_regalador == nombre_receptor:
            return False
    return True


def validar_restricciones_grupo(asignaciones, restricciones):
    """Verifica que ninguna pareja viole las restricciones de grupo.

    Parámetros:
    - asignaciones: lista de tuplas (regalador, receptor), donde cada uno es un dict.
    - restricciones: dict donde la clave es el grupo del regalador y el valor
      es una lista de grupos a los que no puede regalar.

    Retorna:
    - False en cuanto se encuentre una pareja cuyo grupo receptor esté en la
      lista de prohibiciones del grupo del regalador.
    - True si todas las parejas cumplen las restricciones.
    """
    for regalador, receptor in asignaciones:
        grupo_regalador = None
        grupo_receptor = None
        if isinstance(regalador, dict):
            grupo_regalador = regalador.get("grupo")
        if isinstance(receptor, dict):
            grupo_receptor = receptor.get("grupo")

        if grupo_regalador is None or grupo_receptor is None:
            # Si faltan datos de grupo, consideramos que no hay una violación
            # aquí y continuamos (puedes cambiar este comportamiento si lo prefieres).
            continue

        prohibidos = restricciones.get(grupo_regalador, [])
        if grupo_receptor in prohibidos:
            return False

    return True


def main():
    """Función principal: genera asignaciones hasta que pasen ambas validaciones.

    El bucle se rompe únicamente cuando `validar_auto_regalo` y
    `validar_restricciones_grupo` devuelven True para la misma asignación.
    """
    print("Lista de participantes:")
    for participante in participantes:
        print(f"{participante['nombre']} - Grupo {participante['grupo']}")

    intentos = 0
    while True:
        intentos += 1
        if intentos > MAX_INTENTOS:
            raise RuntimeError(
                f"No se pudo encontrar una asignación válida después de {MAX_INTENTOS} intentos; "
                "las reglas parecen imposibles de cumplir con los participantes actuales."
            )
        pares = generar_asignaciones(participantes)

        if not validar_auto_regalo(pares):
            continue

        if not validar_restricciones_grupo(pares, restricciones):
            continue

        # Si llegamos aquí, ambas validaciones pasaron
        print(f"\nAsignación válida encontrada después de {intentos} intento(s):")

        # Construir la lista final con códigos de acceso únicos
        resultado = []
        for regalador, receptor in pares:
            codigo = generar_codigo_unico()
            entrada = {
                "nombre_participante": regalador.get("nombre"),
                "codigo_acceso": codigo,
                "nombre_amigo_secreto": receptor.get("nombre"),
            }
            resultado.append(entrada)

        print("\nEstructura final con códigos de acceso:")
        for item in resultado:
            print(f"{item['nombre_participante']} | {item['codigo_acceso']}")

        # Guardar en JSON para que la web pueda leer la base de datos sin recalcular
        try:
            guardar_datos_json(resultado)
            print("\nDatos guardados en 'db_amigo_secreto.json'.")
        except Exception:
            print("\nError al guardar 'db_amigo_secreto.json'.")

        # Además crear y guardar un JSON público que NO incluya el nombre del amigo secreto
        publico = []
        for item in resultado:
            publico.append({
                "nombre_participante": item.get("nombre_participante"),
                "codigo_acceso": item.get("codigo_acceso"),
            })

        try:
            guardar_datos_json(publico, filename='db_participantes.json')
            print("Datos públicos guardados en 'db_participantes.json'.")
        except Exception:
            print("Error al guardar 'db_participantes.json'.")

        break


if __name__ == "__main__":
    main()

