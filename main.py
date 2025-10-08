import pandas as pd
import numpy as np
import sqlite3
import tkinter as tk
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tkinter import ttk, messagebox

# -----------------------------
# 1. Carregamento dos dados Spotify_Youtube
# -----------------------------
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

# -----------------------------
# 2. Criar matriz usuário-item
# -----------------------------
rows = df_ratings['userId'].map(u2idx)
cols = df_ratings.index.map(lambda x: x % len(df_music))
data = df_ratings['binary_rating'].values
M = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(df_music))).toarray()

# -----------------------------
# 3. AutoEncoder
# -----------------------------
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

# -----------------------------
# 4. Função de recomendação
# -----------------------------
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

# -----------------------------
# 5. Banco de dados usuários
# -----------------------------
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

# -----------------------------
# 6. Interfaces Tkinter
# -----------------------------
def abrir_tela_recomendacao(usuario):
    tela_login.destroy()
    rec_window = tk.Tk()
    rec_window.title("Sistema de Recomendação de Músicas")
    rec_window.geometry("600x500")

    ttk.Label(rec_window, text=f"Bem-vindo, {usuario[1]}!", font=("Arial", 14)).pack(pady=10)

    ttk.Label(rec_window, text="Artista preferido (opcional):").pack(pady=2)
    entry_artista = ttk.Entry(rec_window)
    entry_artista.pack(pady=2)

    text_result = tk.Text(rec_window, wrap="word", height=20, width=70)
    text_result.pack(pady=10)

    def recomendar_com_filtro():
        user_id = usuario[0]
        artista = entry_artista.get().strip().lower()

        recs = recommend_autoencoder(user_id, topk=50)

        if artista:
            recs = recs[recs['Artist'].str.lower().str.contains(artista)]

        if not recs.empty:
            recs = recs.sample(n=min(5, len(recs)), replace=False, random_state=None)

        text_result.delete("1.0", tk.END)
        text_result.insert(tk.END, " Músicas recomendadas:\n\n")
        if recs.empty:
            text_result.insert(tk.END, "Nenhuma música encontrada com esses filtros.\n")
        else:
            for _, row in recs.iterrows():
                text_result.insert(tk.END, f"- {row['Track']} | {row['Artist']} \n")

    ttk.Button(rec_window, text="Recomendar", command=recomendar_com_filtro).pack(pady=5)
    rec_window.mainloop()

def abrir_tela_cadastro():
    def cadastrar():
        nome = entry_nome.get()
        email = entry_email.get()
        senha = entry_senha.get()

        if nome and email and senha:
            if cadastrar_usuario(nome, email, senha):
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                cadastro_window.destroy()
            else:
                messagebox.showerror("Erro", "Email já cadastrado!")
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")

    cadastro_window = tk.Toplevel(tela_login)
    cadastro_window.title("Cadastro")
    cadastro_window.geometry("400x300")

    ttk.Label(cadastro_window, text="Nome:").pack(pady=5)
    entry_nome = ttk.Entry(cadastro_window)
    entry_nome.pack(pady=5)

    ttk.Label(cadastro_window, text="Email:").pack(pady=5)
    entry_email = ttk.Entry(cadastro_window)
    entry_email.pack(pady=5)

    ttk.Label(cadastro_window, text="Senha:").pack(pady=5)
    entry_senha = ttk.Entry(cadastro_window, show="*")
    entry_senha.pack(pady=5)

    btn_cadastrar = ttk.Button(cadastro_window, text="Cadastrar", command=cadastrar)
    btn_cadastrar.pack(pady=10)

def fazer_login():
    email = entry_email.get()
    senha = entry_senha.get()

    user = validar_login(email, senha)
    if user:
        abrir_tela_recomendacao(user)
    else:
        messagebox.showerror("Erro", "Email ou senha inválidos!")

# -----------------------------
# 7. Tela de Login principal
# -----------------------------
init_db()

tela_login = tk.Tk()
tela_login.title("Login - Sistema de Recomendação")
tela_login.geometry("400x250")

ttk.Label(tela_login, text="Email:").pack(pady=5)
entry_email = ttk.Entry(tela_login)
entry_email.pack(pady=5)

ttk.Label(tela_login, text="Senha:").pack(pady=5)
entry_senha = ttk.Entry(tela_login, show="*")
entry_senha.pack(pady=5)

btn_login = ttk.Button(tela_login, text="Login", command=fazer_login)
btn_login.pack(pady=10)

btn_cadastro = ttk.Button(tela_login, text="Cadastrar", command=abrir_tela_cadastro)
btn_cadastro.pack(pady=5)

tela_login.mainloop()