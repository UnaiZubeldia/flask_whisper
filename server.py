from flask import Flask, render_template, request, redirect, url_for, session, make_response
from pydub import AudioSegment
import whisper
import sql
import os
import modelos
import pickle

#necesario ffmeg
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
# - Que se guarde el login en la bbdd
# - Comprobar que el usuario está logueado para dejarle acceder a la transcripción
# - Falta poner algo (algún meme de programación?) en el loading del modelo
# - Falta la galería de imágenes, que se podría hacer al elegir el modelo, en los memes del loading o al enseñar los gráficos
# - Se podria hacer que se compruebe si existe la carpeta modelos con los 3 modelos dentro y si no existe que se descarguen
# - Youtube to mp3 (que la ruta incluya el link de youtube, con rutas dinámicas)
# - Que se pueda elegir el idioma del resumen


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/registro", methods = ["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        session['nombre'] = username
        sql.insert_user(email, username, password)
        return render_template("login_exitoso.html", nombre = username)
    return render_template("registro.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        session['email'] = email
        password = request.form.get("password")
        if not sql.email_existe(email):
            return render_template('wrong_email.html')
        if not sql.comprobar_pwd(email, password):
            return render_template('wrong_pwd.html')
        nombre = sql.consultar_nombre(email)
        session['nombre'] = nombre
        return render_template('login_exitoso.html', nombre = session['nombre'])
    return render_template("login.html")


@app.route('/transcriptor', methods=['GET', 'POST'])
def transcriptor():
     if request.method == 'POST':
         file = request.files['file']
         size = request.form['size']
         if file and file.filename.lower().endswith(('.mp4', '.mov', '.avi')):
             # Conversión del archivo a mp3
             audio = AudioSegment.from_file(file, file.filename.split(".")[-1])
             mp3_path = 'audio.mp3'
             audio.export(mp3_path, format="mp3")
             model = modelos[size]
             print('Transcribiendo...')
             resultado = model.transcribe(mp3_path)
             session['transcripcion'] = resultado['text']
             print('Transcripción completada')
             # Se guarda resultado['text'] en la base de datos para analizar ese texto
             sql.guardar_transcripcion(session['email'], resultado['text'])
             return render_template('resultado_transcripcion.html')
        # else:
        #    return render_template('transcriptor.html', error="Error: Debe seleccionar un archivo de video válido (mp4, mov o avi)")
     else:
         return render_template('transcriptor.html')

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
    session['email'] = sql.provisional() # PROVISIONAL
    texto = sql.consultar_ult_texto(session['email'])
    resumen = sql.resumidor(texto)
    return render_template('resumen.html', resumen = resumen)

@app.route('/estadisticas')
def estadisticas():
    session['email'] = sql.provisional() # PROVISIONAL
    textos = sql.consultar_textos(session['email'])
    sql.wordcloud(textos) # genera la imagen del wordcloud y la guarda en la carpeta static
    sql.histograma(textos) # genera la imagen del histograma y la guarda en la carpeta static
    return render_template('estadisticas.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('nombre', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)