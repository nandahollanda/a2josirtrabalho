import streamlit as st
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import re

st.set_page_config(page_title="Nuvem YouTube", layout="wide")
st.title("📺 Nuvem de Palavras - Comentários Reais do YouTube")

# CHAVE DA API
API_KEY = "AIzaSyAziHDNILJUujR7rt-tZq4V1QUsX-iaZI8" 

# Função para buscar comentários reais do YouTube
def buscar_comentarios(palavra_chave, max_videos=3):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    pesquisa = youtube.search().list(
        q=palavra_chave,
        part='id',
        type='video',
        maxResults=max_videos
    ).execute()

    video_ids = [item['id']['videoId'] for item in pesquisa.get('items', [])]
    comentarios = []

    for video_id in video_ids:
        try:
            resposta = youtube.commentThreads().list(
                videoId=video_id,
                part='snippet',
                maxResults=50,
                textFormat="plainText"
            ).execute()

            for item in resposta.get('items', []):
                texto = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comentarios.append(texto)
        except:
            continue

    return comentarios

# Limpeza do texto
def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+|[^a-zA-Záéíóúãõâêîôûç\s]", "", texto)
    return texto

# Geração da nuvem
def gerar_nuvem(texto):
    wc = WordCloud(width=800, height=400, background_color='white').generate(texto)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# Interface do usuário
palavra = st.text_input("Digite o tema (ex: funk, política, futebol)")

if st.button("Gerar Nuvem") and palavra:
    comentarios = buscar_comentarios(palavra)
    
    if comentarios:
        comentarios_limpos = [limpar_texto(c) for c in comentarios]
        texto_total = " ".join(comentarios_limpos)

        st.subheader("☁️ Nuvem de Palavras")
        gerar_nuvem(texto_total)

        st.subheader("📋 Palavras mais frequentes")
        palavras = texto_total.split()
        frequencia = pd.Series(palavras).value_counts().reset_index()
        frequencia.columns = ['Palavra', 'Frequência']
        st.dataframe(frequencia.head(20))
    else:
        st.warning("Nenhum comentário encontrado.")
