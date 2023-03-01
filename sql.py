import sqlite3 as sqlite
import os
import pandas as pd




# DOCSTRINGS




def create_db():
    if not os.path.exists('database.db'):
        conn = sqlite.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users (email text, username text, password text)''')
        c.execute('''CREATE TABLE transcripciones (email text, texto text)''')
        conn.commit()
        conn.close()
        return None

def check_user(username, password):
    conn = sqlite.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    data = c.fetchone()
    conn.close()
    if data:
        return True
    else:
        return False

def insert_user(email:str, username:str, password:str):
    conn = sqlite.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, username, password))
    conn.commit()
    conn.close()
    return None

def email_existe(email:str):
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,)) 
    email_res = cur.fetchone()
    con.close()
    return email_res is not None

def comprobar_pwd(email:str, password:str):
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE email = ?", (email,)) 
    pw = cur.fetchone()[0]
    con.close()
    return password == pw

def consultar_nombre(email:str):
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT nombre FROM users WHERE email = ?", (email,)) 
    nombre = cur.fetchone()[0]
    con.close()
    return nombre



def guardar_transcripcion(email:str, texto:str):
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO transcripciones VALUES (?, ?)", (email, texto))
    con.commit()
    con.close()
    return None

def consultar_ult_texto(email:str):
    # Consulta solo el último texto de un usuario
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT texto FROM transcripciones WHERE email = ?", (email,))
    textos = cur.fetchall()
    texto = textos[-1][0]
    con.close()
    return texto

def consultar_textos(email:str):
    # Consulta todos los textos de un usuario
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT texto FROM transcripciones WHERE email = ?", (email,))
    textos = cur.fetchall()
    # Unirlos todos en un texto unico en formato str:
    textos = ' '.join([texto[0] for texto in textos])
    con.close()
    return textos

def resumidor(texto:str):
    palabras = texto.split()
    resumen = ' '.join(palabras[:5])
    return resumen

def wordcloud(texto:str):
    # Generar wordcloud
    #
    # Guardar wordcloud en static como "wordcloud.png"
    #
    return None

def histograma(texto:str):
    texto = texto.split()
    histograma = {}
    for palabra in texto:
        if palabra in histograma:
            histograma[palabra] += 1
        else:
            histograma[palabra] = 1
    histograma = sorted(histograma.items(), key=lambda x: x[1], reverse=True)
    histograma = histograma[:10]
    histograma = dict(histograma)
    histograma = pd.DataFrame(histograma.items(), columns=['Palabra', 'Frecuencia'])
    histograma.plot.bar(x='Palabra', y='Frecuencia')
    fig = histograma.get_figure()
    fig.savefig('static/histograma.png')
    return None




def provisional():
    resultado = {}
    resultado['text'] = 'texto provisional: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, nisl eget ultricies lacinia, nisl nisl aliquet nisl, eget alique'
    mail = 'jon@provisional.com'
    guardar_transcripcion(mail, resultado['text'])
    return mail