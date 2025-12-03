from flask import Flask, render_template, request
import os
import json

app = Flask(__name__)


def buscar_por_codigo(codigo, filename='db_amigo_secreto.json'):
    """Busca una entrada en el archivo JSON por su `codigo_acceso`.

    Devuelve el diccionario de la persona si se encuentra, o `None` si no.
    La búsqueda no es sensible a mayúsculas.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None

    if not isinstance(datos, list):
        return None

    codigo_buscar = codigo.upper() if isinstance(codigo, str) else codigo
    for entrada in datos:
        if not isinstance(entrada, dict):
            continue
        valor = entrada.get('codigo_acceso')
        if isinstance(valor, str) and valor.upper() == codigo_buscar:
            return entrada

    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resultado', methods=['POST'])
def resultado():
    codigo = request.form.get('codigo')
    participante = buscar_por_codigo(codigo)

    if participante:
        return render_template('resultado.html', 
                               nombre=participante['nombre_participante'], 
                               amigo=participante['nombre_amigo_secreto'])
    else:
        # Volver a la pantalla de inicio mostrando un mensaje de error y
        # rellenando el campo con el código introducido. Retornar 200 para
        # que el navegador trate la página normalmente.
        return render_template('index.html', error='Código inválido, inténtalo nuevamente', codigo=codigo)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

