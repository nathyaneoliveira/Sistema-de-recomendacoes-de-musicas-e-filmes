# 🎯 Sistema de Recomendação de Filmes e Músicas

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Status](https://img.shields.io/badge/status-Em%20Desenvolvimento-yellow)
![License](https://img.shields.io/badge/License-Acad%C3%AAmico-red)
![Framework](https://img.shields.io/badge/Framework-Tkinter-orange)

### Projeto de TCC – Trabalho de Conclusão de Curso

---

## 1. Introdução

O presente projeto foi desenvolvido como parte de um **Trabalho de Conclusão de Curso (TCC)**, com o objetivo de implementar um **sistema de recomendação de filmes e músicas** com autenticação de usuários.

O sistema combina técnicas de **Inteligência Artificial (IA)**, **persistência de dados** e **interface gráfica**, oferecendo recomendações personalizadas para cada usuário com base em **filtragem colaborativa** e **modelos de aprendizado profundo (AutoEncoder)**.

Ele simula uma aplicação real de recomendação, permitindo interação intuitiva e personalização conforme as preferências individuais do usuário.

---

## 2. Objetivos

* Desenvolver um sistema **funcional e interativo** de recomendação de filmes e músicas.
* Aplicar técnicas de **aprendizado de máquina** utilizando **AutoEncoder** para gerar recomendações.
* Explorar o conceito de **persistência poliglota**, utilizando **SQLite** com possibilidade futura de expansão para **NoSQL**.
* Implementar **login e cadastro de usuários**, garantindo segurança e personalização das recomendações.
* Fornecer uma interface gráfica simples e intuitiva com **Tkinter**, adequada para usuários finais.

---

## 3. Tecnologias Utilizadas

**Linguagem principal:** Python 3.12+
**Framework de interface:** Tkinter

**Bibliotecas principais:**

| Biblioteca       | Uso                                            |
| ---------------- | ---------------------------------------------- |
| pandas           | Manipulação e limpeza de dados                 |
| numpy            | Operações numéricas e matrizes                 |
| sqlite3          | Banco de dados relacional local                |
| tkinter          | Interface gráfica                              |
| scipy            | Matrizes esparsas                              |
| scikit-learn     | Divisão de dados em treino e teste             |
| tensorflow.keras | Construção e treinamento do modelo AutoEncoder |

---

## 4. Estrutura do Projeto

```
sistemacc/
│── .venv/                     # Ambiente virtual
│── pages/
│   │── app.py                 # Script principal da interface
│   │── filmes.py              # Módulo de recomendação de filmes
│   │── login.py               # Módulo de autenticação
│   │── main.py                # Execução inicial do sistema
│   │── movies.csv             # Dataset de filmes
│   │── ratings.csv            # Avaliações de filmes
│   │── Spotify_Youtube.csv    # Dataset de músicas
│── usuarios.db                # Banco SQLite de usuários
│── filmes.py                  # Lógica de recomendação de filmes
│── login.py                   # Cadastro e login de usuários
│── main.py                    # Execução principal do sistema
│── requirements.txt           # Dependências do projeto
```

---

## 5. Banco de Dados

### 5.1 SQLite – Usuários

O sistema utiliza **SQLite** para armazenar informações de usuários, garantindo persistência e segurança:

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
);
```

* Cada usuário é identificado pelo **email**.
* O banco `usuarios.db` é criado automaticamente ao iniciar o sistema.
* Permite autenticação e registro de histórico de recomendações.

### 5.2 Datasets de Filmes e Músicas

**Filmes (MovieLens Dataset):**

| Arquivo       | Descrição                                        | Link oficial                                                          |
| ------------- | ------------------------------------------------ | --------------------------------------------------------------------- |
| `movies.csv`  | Catálogo de filmes (id, título, gênero)          | [MovieLens](https://grouplens.org/datasets/movielens/latest/)         |
| `ratings.csv` | Avaliações de usuários (userId, movieId, rating) | [MovieLens Ratings](https://grouplens.org/datasets/movielens/latest/) |

**Músicas (Spotify / YouTube Dataset):**

| Arquivo               | Descrição                                                      | Observação                           |
| --------------------- | -------------------------------------------------------------- | ------------------------------------ |
| `Spotify_Youtube.csv` | Catálogo e avaliações de músicas (id, título, artista, gênero) | Pode ser customizado com dados reais |

* Matrizes **usuário-item** são construídas a partir dos datasets.
* Permite gerar recomendações personalizadas por **filtragem colaborativa**.

---

## 6. Modelo de Recomendação (AutoEncoder)

O sistema utiliza **AutoEncoder** para criar recomendações personalizadas.

**Características do modelo:**

* **Entrada:** matriz usuário-item (filmes ou músicas)
* **Treinamento:** AutoEncoder aprende padrões de preferência dos usuários
* **Saída:** reconstrução da matriz, indicando itens não avaliados e sugeridos
* **Biblioteca utilizada:** TensorFlow / Keras
* **Benefício:** recomendações mais precisas, considerando histórico e padrões de comportamento.

---

## 7. Interface Gráfica (Tkinter)

### 🔹 Tela Inicial

* Opções: **Login** ou **Cadastro**

### 🔹 Cadastro

* Campos: Nome, Email, Senha
* Informações gravadas no banco `usuarios.db`

### 🔹 Login

* Autentica usuário
* Usuário válido → acesso às recomendações

### 🔹 Recomendações

* Listagem de filmes ou músicas sugeridos
* Filtros disponíveis:

  * **Gênero** (filmes)
  * **Artista/Diretor** (músicas ou filmes)
* Atualização dinâmica conforme escolhas do usuário
* Possibilidade de integração futura com visualização de pôster/capa e notas

---

## 8. Fluxo de Uso

1. **Instalar dependências:**

```powershell
pip install -r requirements.txt
```

2. **Executar o sistema:**

```powershell
python pages/main.py
```

3. **Na interface:**

* Se não possui conta → **Cadastrar usuário**
* Se já possui → **Login**

4. **Após login:**

* Sistema mostra recomendações personalizadas
* Usuário pode filtrar por gênero ou artista/diretor
* O modelo de AutoEncoder ajusta recomendações com base nas avaliações passadas
