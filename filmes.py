import pandas as pd
import numpy as np
import sqlite3
import tkinter as tk
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tkinter import ttk, messagebox

# Carregamento dos dados MovieLens

df_movies = pd.read_csv("movies.csv")
df_ratings_full = pd.read_csv("ratings.csv")

# Converter notas para binário

df_ratings_full['binary_rating'] = (df_ratings_full['rating'] >= 4).astype(int)

# Mostra 30 usuários

np.random.seed(42)
sample_users = np.random.choice(df_ratings_full['userId'].unique(), size=30, replace=False)
df_ratings = df_ratings_full[df_ratings_full['userId'].isin(sample_users)]

# Mapear IDs para índices

user_ids = df_ratings['userId'].unique()
movie_ids = df_ratings['movieId'].unique()

u2idx = {u: i for i, u in enumerate(user_ids)}
i2idx = {i: j for j, i in enumerate(movie_ids)}
idx2i = {v: k for k, v in i2idx.items()}

# Criar matriz usuário-item

rows = df_ratings['userId'].map(u2idx)
cols = df_ratings['movieId'].map(i2idx)
data = df_ratings['binary_rating'].values
M = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(movie_ids))).toarray()

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
    epochs=10,
    batch_size=16,
    validation_data=(X_test, X_test),
    verbose=0
)

# Função de recomendação

def recommend_autoencoder(user_id, topk=20):
    if user_id not in u2idx:
        populares = df_ratings_full.groupby("movieId")['rating'].count().sort_values(ascending=False).head(topk).index
        recs = df_movies[df_movies['movieId'].isin(populares)][['title', 'genres', 'movieId']]
        return recs

    user_idx = u2idx[user_id]
    user_vector = M[user_idx].reshape(1, -1)

    scores = autoencoder.predict(user_vector, verbose=0)[0]
    seen = np.where(user_vector[0] > 0)[0]
    scores[seen] = -1
    recs_idx = np.argsort(-scores)[:topk]

    recommended_movieIds = [idx2i[i] for i in recs_idx]
    recs = df_movies[df_movies['movieId'].isin(recommended_movieIds)][['title', 'genres', 'movieId']]
    return recs

# Banco de dados usuários

def init_db():
    conn = sqlite3.connect("usuarios.db")
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
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validar_login(email, senha):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    user = cursor.fetchone()
    conn.close()
    return user