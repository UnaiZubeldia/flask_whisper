from flask import Flask, render_template, request, redirect, url_for, session, make_response
from pydub import AudioSegment
import nlp
import sql
import os
import modelos
import pickle

# Necesario ffmeg
# https://es.wikihow.com/instalar-FFmpeg-en-Windows


if not os.path.exists('modelos'):
    modelos.main()

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = '<<<$$$super_secret_key$$$>>>'

sql.create_db()

modelos = {
    'tiny': pickle.load(open('modelos/tiny.pkl', 'rb')), 
    'base': pickle.load(open('modelos/base.pkl', 'rb'))}



# PENDIENTE:
# - Falta poner algo (loading.gif) en el loading del modelo
# - Youtube to mp3 (que la ruta incluya el link de youtube, con rutas dinámicas)
# - Que te haga el resumen + que carguen los gráficos (wordcloud e histograma de frecuencias de palabras)

# - Falta meter una galería de imágenes (Jon)


@app.route('/')
def index():
    """Ruta principal de la aplicación.

    Returns:
        render_template: Renderiza la página principal de la aplicación.
    """
    return render_template('index.html')


@app.route("/registro", methods = ["GET", "POST"])
def registro():
    """Ruta para el registro de usuarios.

    Returns:
        render_template: Renderiza la página de registro.
        Si el usuario ya está registrado, le redirige a la página de login.
        Si el usuario se ha registrado correctamente, le redirige a la página de login exitoso.
        Inserta al usuario en la base de datos.
        Devuelve un mensaje de error si el email ya está registrado o la contraseña es demasiado corta.
    """
    if request.method == "POST":
        session['email'] = request.form.get("email")
        session['nombre'] = request.form.get("username")
        session['password'] = request.form.get("password")
        if sql.email_existe(session['email']):
            return render_template('login.html', msg = '¡El email ya está registrado!')
        if len(session['password']) < 5:
            return render_template('registro.html', msg = '¡La contraseña debe tener al menos 5 caracteres!')
        sql.insert_user(session['email'], session['nombre'], session['password'])
        return render_template("login_exitoso.html", nombre = session['nombre'])
    return render_template("registro.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    """Ruta para el login de usuarios.

    Returns:
        render_template: Renderiza la página de login.
        Si el usuario no está registrado o ha metido mal la contraseña, le redirige a la página de login incorrecto.
        Si el usuario se ha logueado correctamente, le redirige a la página de login exitoso.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not sql.email_existe(email):
            return render_template('wrong_login.html', msg_error = 'No te has registrado aún')
        if not sql.comprobar_pwd(email, password):
            return render_template('wrong_login.html', msg_error = 'Contraseña incorrecta')
        return render_template('login_exitoso.html', nombre = session['nombre'])
    return render_template("login.html")

@app.route('/contr_olvidada', methods=['GET', 'POST'])
def contr_olvidada():
    """Ruta para la recuperación de contraseñas.

    Returns:
        render_template: Renderiza la página de recuperación de contraseñas.
    """
    # Obtener la contraseña del usuario de la sesión
    password = session.get('password')
    password_length = len(password) if password else 0
    
    # Si el usuario envió un formulario, comprobar las letras
    letras_correctas = [None] * password_length
    mensaje = ""
    if request.method == 'POST':
        aciertos = []
        fallos = []
        for i in range(password_length):
            letra = request.form.get(f'letra-{i}')
            if letra is None:
                continue
            elif letra == password[i]:
                letras_correctas[i] = True
                aciertos.append(f"{i+1}")
            else:
                letras_correctas[i] = False
                fallos.append(f"{i+1}")
        session['letras_correctas'] = letras_correctas
        acierto_completo = all(letras_correctas)
        mensaje = "Has acertado la letra " + ", ".join(aciertos) if aciertos else ""
        if fallos:
            mensaje += ". Has fallado la letra " + ", ".join(fallos)
        if acierto_completo:
            mensaje = "¡Felicidades! Ya te has acordado de tu contraseña!"
        return render_template('contr_olvidada.html', password_length=password_length, letras_correctas=letras_correctas, mensaje=mensaje)
    
    return render_template('contr_olvidada.html', password_length=password_length, letras_correctas=letras_correctas, mensaje=mensaje)

@app.route('/mostrar_contrasena')
def mostrar_contrasena():
    """Ruta para mostrar la contraseña del usuario.

    Returns:
        render_template: Renderiza la página de mostrar contraseña, donde se muestra la contraseña del usuario.
    """
    password = session.get('password')
    return render_template('mostrar_contrasena.html', password=password)


@app.route('/principal', methods=['GET', 'POST'])
def principal():
    """Ruta a la página principal de la aplicación.

    Returns:
        render_template: Renderiza la página principal de la aplicación.
    """
    return render_template('principal.html', nombre = session['nombre'])


@app.route('/transcriptor', methods=['GET', 'POST'])
def transcriptor():
    """Ruta a la página de transcripción de audio, donde se muestra el botón para subir el archivo de audio.

    Returns:
        render_template: Renderiza la página de transcripción de audio.
    """
    if request.method == 'POST':
         file = request.files['file']
         size = request.form['size']
         if file and file.filename.lower().endswith(('.mp4', '.mov', '.avi')):
             # Conversión del archivo a mp3
             audio = AudioSegment.from_file(file, file.filename.split(".")[-1])
             # get the name of the file
             filename = file.filename
             mp3_path = 'audio.mp3'
             audio.export(mp3_path, format="mp3")
             model = modelos[size]
             print('Transcribiendo...')
             resultado = model.transcribe(mp3_path)
             session['transcripcion'] = resultado['text']
             print('Transcripción completada')
             sql.guardar_transcripcion(session['email'], session['transcripcion'], filename)
             return redirect(url_for('resultado_transcripcion'))
    else:
         return render_template('transcriptor.html', nombre = session['nombre'])

@app.route('/resultado_transcripcion')
def resultado_transcripcion():
    """Muestra el resultado de la transcripción del archivo de audio.

    Returns:
        render_template: Renderiza la página de resultado de la transcripción del archivo de audio.
        Ahí se muestran el resultado de la transcripción y el historial de transcripciones del usuario.
    """
    historial = sql.consultar_filenames(session['email'])
    historial = {i+1: historial[i] for i in range(0, len(historial))}
    return render_template('resultado_transcripcion.html',
                            transcripcion = session['transcripcion'],
                            historial = historial)

@app.route('/descargar_transcripcion')  
def descargar_transcripcion():
    """Descarga el archivo de audio en un archivo de texto.

    Returns:
        respuesta: Archivo de texto con la transcripción del archivo de audio.
    """
    # Carga el contenido de la transcripción
    contenido = session['transcripcion']

    # Crea la respuesta del archivo
    respuesta = make_response(contenido)
    
    # Establece el tipo de contenido y la descarga del archivo
    respuesta.headers['Content-Type'] = 'text/plain'
    respuesta.headers['Content-Disposition'] = 'attachment; filename=transcripcion.txt'

    return respuesta

@app.route('/resumen')
def resumen():
    """Ruta a la página de resumen de texto, donde se muestra el resumen del texto más reciente del usuario.

    Returns:
        render_template: Renderiza la página de resumen de texto.
    """
    texto = sql.consultar_ult_texto(session['email'])
    resumen = nlp.hacer_resumen(texto)
    return render_template('resumen.html', resumen = resumen)

@app.route('/estadisticas')
def estadisticas():
    """Ruta a la página de estadísticas, donde se muestran las estadísticas de los textos transcritos por el usuario.
    Entre las estadísticas se encuentran: la nube de palabras, el histograma de frecuencia de palabras y la longitud promedio de las palabras.
    
    Returns:
        render_template: Renderiza la página de estadísticas.
    """
    texto = sql.consultar_textos(session['email'])
    # muestra una tabla con las palabras más usadas y su frecuencia (obligatorio, no tenemos ninguna tabla de sql!)
    
    wordcloud_base64 = nlp.wordcloud(texto)
    hist_base64, frecuencia_palabras = nlp.generar_histograma(texto)

    # average word length in texto
    longitud = round(nlp.average_word_length(texto),2)
    frases = nlp.n_frases(texto)
    total_palabras = len(texto.split())
    total_palabras_unicas = len(set(texto.split()))

    return render_template('estadisticas.html', 
                            wc=wordcloud_base64, 
                            hist=hist_base64, 
                            longitud=longitud,
                            n_frases=frases, 
                            frecuencia_palabras=frecuencia_palabras, 
                            total_palabras=total_palabras,
                            total_palabras_unicas=total_palabras_unicas)

if __name__ == '__main__':
    app.run(debug=True)