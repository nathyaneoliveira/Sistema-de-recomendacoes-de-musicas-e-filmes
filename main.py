import pandas as pd
import numpy as np
import sqlite3
import tkinter as tk
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tkinter import ttk, messagebox

# Carregamento dos dados Spotify_Youtube

df_music = pd.read_csv("pages/Spotify_Youtube.csv")

# Selecionar colunas principais
df_music = df_music[['Track', 'Artist', 'Views', 'Stream',
                     'Danceability', 'Energy', 'Valence',
                     'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness']].dropna()

# Criar coluna binária: música popular se Views >= mediana
df_music['binary_pop'] = (df_music['Views'] >= df_music['Views'].median()).astype(int)

# Mostra 30 usuários simulados
np.random.seed(42)
user_ids = np.arange(1, 31)
df_ratings = []

for u in user_ids:
    sampled = df_music.sample(50, replace=False)  # cada usuário interage com 50 músicas
    sampled = sampled.copy()
    sampled['userId'] = u
    sampled['binary_rating'] = sampled['binary_pop']
    df_ratings.append(sampled)

df_ratings = pd.concat(df_ratings, ignore_index=True)

# Mapear IDs
u2idx = {u: i for i, u in enumerate(user_ids)}
i2idx = {i: j for j, i in enumerate(df_music.index)}
idx2i = {v: k for k, v in i2idx.items()}

# Criar matriz usuário-item

rows = df_ratings['userId'].map(u2idx)
cols = df_ratings.index.map(lambda x: x % len(df_music))
data = df_ratings['binary_rating'].values
M = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(df_music))).toarray()

# AutoEncoder

n_items = M.shape[1]

input_layer = layers.Input(shape=(n_items,))
encoded = layers.Dense(128, activation='relu')(input_layer)
encoded = layers.Dense(64, activation='relu')(encoded)
decoded = layers.Dense(128, activation='relu')(encoded)
output_layer = layers.Dense(n_items, activation='sigmoid')(decoded)

autoencoder = models.Model(input_layer, output_layer)
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

X_train, X_test = train_test_split(M, test_size=0.2, random_state=42)
autoencoder.fit(
    X_train, X_train,
    epochs=5,
    batch_size=16,
    validation_data=(X_test, X_test),
    verbose=0
)

# Função de recomendação

def recommend_autoencoder(user_id, topk=50):
    if user_id not in u2idx:
        populares = df_music.sort_values("Views", ascending=False).head(topk)
        return populares[['Track', 'Artist', 'Views']]

    user_idx = u2idx[user_id]
    user_vector = M[user_idx].reshape(1, -1)

    scores = autoencoder.predict(user_vector, verbose=0)[0]
    seen = np.where(user_vector[0] > 0)[0]
    scores[seen] = -1
    recs_idx = np.argsort(-scores)[:topk]

    recommended_idx = [idx2i[i] for i in recs_idx]
    recs = df_music.loc[recommended_idx][['Track', 'Artist', 'Views']]
    return recs

# Banco de dados usuários

def init_db():
    conn = sqlite3.connect("pages/usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, senha):
    try:
        conn = sqlite3.connect("pages/usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validar_login(email, senha):
    conn = sqlite3.connect("pages/usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    user = cursor.fetchone()
    conn.close()
    return user

def resetar_tabela_usuarios():
    conn = sqlite3.connect("pages/usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='usuarios'")
    conn.commit()
    conn.close()



