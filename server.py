from flask import Flask, render_template, request, redirect, url_for, session, make_response
from pydub import AudioSegment
import nlp
import sql
import os
import modelos
import pickle
import base64



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
    return render_template('index.html')


@app.route("/registro", methods = ["GET", "POST"])
def registro():
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
    password = session.get('password')
    return render_template('mostrar_contrasena.html', password=password)


@app.route('/principal', methods=['GET', 'POST'])
def principal():
    return render_template('principal.html', nombre = session['nombre'])


@app.route('/transcriptor', methods=['GET', 'POST'])
def transcriptor():
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
             # Se guarda resultado['text'] en la base de datos para analizar ese texto
             sql.guardar_transcripcion(session['email'], session['transcripcion'], filename)
             return redirect(url_for('resultado_transcripcion'))
        # else:
        #    return render_template('transcriptor.html', error="Error: Debe seleccionar un archivo de video válido (mp4, mov o avi)")
     else:
         return render_template('transcriptor.html', nombre = session['nombre'])

@app.route('/resultado_transcripcion')
def resultado_transcripcion():
    historial = sql.consultar_filenames(session['email'])
    # add numeration to the filenames as a dictionary
    historial = {i+1: historial[i] for i in range(0, len(historial))}

    return render_template('resultado_transcripcion.html', 
                            transcripcion = session['transcripcion'],
                            historial = historial)

@app.route('/descargar_transcripcion')  
def descargar_transcripcion():
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
    texto = sql.consultar_ult_texto(session['email'])
    resumen = nlp.hacer_resumen(texto)
    return render_template('resumen.html', resumen = resumen)

@app.route('/estadisticas')
def estadisticas():
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