import streamlit as st
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models

st.set_page_config(page_title="Sistema de Recomendação", page_icon="🎬", layout="wide")

# Bloqueia acesso se o usuário não estiver logado
if "usuario" not in st.session_state:
    st.warning("⚠️ Você precisa fazer login para acessar o sistema.")
    st.page_link("login.py", label="Ir para Login", icon="🔑")
    st.stop()

# ========================
# 🔹 Dados e Funções
# ========================
@st.cache_resource
def carregar_dados():
    filmes = pd.read_csv("pages/movies.csv")
    musicas = pd.read_csv("pages/Spotify_Youtube.csv")
    return filmes, musicas

@st.cache_resource
def treinar_modelo_filmes(df_movies, df_ratings_full):
    df_ratings_full['binary_rating'] = (df_ratings_full['rating'] >= 4).astype(int)
    np.random.seed(42)
    sample_users = np.random.choice(df_ratings_full['userId'].unique(), size=30, replace=False)
    df_ratings = df_ratings_full[df_ratings_full['userId'].isin(sample_users)]

    user_ids = df_ratings['userId'].unique()
    movie_ids = df_ratings['movieId'].unique()

    u2idx = {u: i for i, u in enumerate(user_ids)}
    i2idx = {i: j for j, i in enumerate(movie_ids)}
    idx2i = {v: k for k, v in i2idx.items()}

    rows = df_ratings['userId'].map(u2idx)
    cols = df_ratings['movieId'].map(i2idx)
    data = df_ratings['binary_rating'].values
    M = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(movie_ids))).toarray()

    n_items = M.shape[1]
    input_layer = layers.Input(shape=(n_items,))
    encoded = layers.Dense(128, activation='relu')(input_layer)
    encoded = layers.Dense(64, activation='relu')(encoded)
    decoded = layers.Dense(128, activation='relu')(encoded)
    output_layer = layers.Dense(n_items, activation='sigmoid')(decoded)
    autoencoder = models.Model(input_layer, output_layer)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

    X_train, X_test = train_test_split(M, test_size=0.2, random_state=42)
    autoencoder.fit(X_train, X_train, epochs=5, batch_size=16, validation_data=(X_test, X_test), verbose=0)

    return autoencoder, u2idx, idx2i, M, df_movies

# ========================
#  Interface principal
# ========================
st.sidebar.title(f"👋 Olá, {st.session_state['usuario'][1]}")
if st.sidebar.button("Sair"):
    st.session_state.clear()
    st.switch_page("../login.py")

# Carregar dados
filmes, df_music = carregar_dados()

# Tabs
abas = st.tabs(["🎬 Filmes", "🎵 Músicas"])

# --- FILMES ---
with abas[0]:
    st.subheader("🎬 Recomendador de Filmes")

    # Barra de pesquisa por gênero
    generos = sorted(set(g.strip() for sublist in filmes['genres'].str.split('|') for g in sublist))
    genero_selecionado = st.selectbox("Filtrar por gênero:", ["Todos"] + generos)

    if st.button("Mostrar Filmes Recomendados"):
        if genero_selecionado != "Todos":
            recs_filmes = filmes[filmes['genres'].str.contains(genero_selecionado)].sample(10)
        else:
            recs_filmes = filmes.sample(10)
        st.dataframe(recs_filmes[['title', 'genres']])

# --- MÚSICAS ---
with abas[1]:
    st.subheader("🎵 Recomendador de Músicas")

    # Barra de pesquisa por artista
    artistas = sorted(df_music['Artist'].unique())
    artista_selecionado = st.selectbox("Filtrar por artista:", ["Todos"] + artistas)

    if st.button("Mostrar Músicas Recomendadas"):
        if artista_selecionado != "Todos":
            recs_musicas = df_music[df_music['Artist'] == artista_selecionado].sample(10)
        else:
            recs_musicas = df_music.sample(10)
        st.dataframe(recs_musicas[['Track', 'Artist']])
