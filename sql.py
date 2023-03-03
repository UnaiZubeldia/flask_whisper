import sqlite3 as sqlite
import os
import pandas as pd
import matplotlib.pyplot as plt

def create_db():
    """Crea la base de datos si no existe, y dentro de ella las tablas "users" y "transcripciones".

    Returns:
        None
    """
    if not os.path.exists('database.db'):
        conn = sqlite.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users (email text, username text, password text)''')
        c.execute('''CREATE TABLE transcripciones (email text, texto text, filename text)''')
        conn.commit()
        conn.close()
        return None

def check_user(username, password):
    """Comprueba si un usuario existe en la base de datos.

    Args:
        username (str): EL nombre de usuario.
        password (str): La contraseña.

    Returns:
        bool: True si el usuario existe, False si no.
    """
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
    """Inserta un usuario que se acaba de registrar en la base de datos.

    Args:
        email (str): El email del usuario.
        username (str): El nombre de usuario.
        password (str): La contraseña.

    Returns:
        None
    """
    conn = sqlite.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, username, password))
    conn.commit()
    conn.close()
    return None

def email_existe(email:str):
    """Comprueba si un email ya existe en la base de datos (para evitar que se registren dos usuarios con el mismo email).

    Args:
        email (str): El email a comprobar.

    Returns:
        bool: True si el email ya existe, False si no.
    """
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,)) 
    email_res = cur.fetchone()
    con.close()
    return email_res is not None

def comprobar_pwd(email:str, password:str):
    """Comprueba si la contraseña introducida por el usuario es correcta.

    Args:
        email (str): El email del usuario.
        password (str): La contraseña introducida por el usuario.

    Returns:
        bool: True si la contraseña es correcta, False si no.
    """
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE email = ?", (email,)) 
    pw = cur.fetchone()[0]
    con.close()
    print(password)
    print(pw)
    return password == pw


def guardar_transcripcion(email:str, texto:str, filename:str):
    """Guarda el texto de la transcripción en la base de datos.

    Args:
        email (str): El email del usuario.
        texto (str): El texto de la transcripción.
        filename (str): El nombre del archivo de audio transcrito.

    Returns:
        None
    """
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO transcripciones VALUES (?, ?, ?)", (email, texto, filename))
    con.commit()
    con.close()
    return None

def consultar_ult_texto(email:str):
    """Consulta el último texto de un usuario.

    Args:
        email (str): El email del usuario.

    Returns:
        texto (str): El último texto de un usuario.
    """
    # Consulta solo el último texto de un usuario
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT texto FROM transcripciones WHERE email = ?", (email,))
    textos = cur.fetchall()
    texto = textos[-1][0]
    con.close()
    return texto

def consultar_textos(email:str):
    """Consulta todos los textos de un usuario.

    Args:
        email (str): El email del usuario.

    Returns:
        textos (str): Todos los textos de un usuario.
    """
    # Consulta todos los textos de un usuario
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT texto FROM transcripciones WHERE email = ?", (email,))
    textos = cur.fetchall()
    # Unirlos todos en un texto unico en formato str:
    textos = ' '.join([texto[0] for texto in textos])
    con.close()
    return textos

def consultar_filenames(email:str):
    """Consulta todos los nombres de los archivos transcritos de un usuario.

    Args:
        email (str): El email del usuario.

    Returns:
        filenames (str): Todos los nombres de los archivos transcritos de un usuario.
    """
    # Consulta todos los filenames de un usuario
    con = sqlite.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT filename FROM transcripciones WHERE email = ?", (email,))
    filenames = cur.fetchall()
    con.close()
    return filenames