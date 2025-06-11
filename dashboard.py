import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
from faker import Faker

st.set_page_config(page_title="Q7 – Email Scoring Dashboard", layout="wide")

# --- Geração dos dados
@st.cache_data
def gerar_dados():
    fake = Faker()
    dados = []

    for _ in range(100):
        is_corp = random.choice([True, False])
        domain = fake.domain_name() if is_corp else random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}@{domain}"
        sources = random.randint(1, 5)
        bounce = random.choice([0, 1, None])
        last_updated = random.randint(0, 365)
        verified = random.choice([0, 1])
        social = random.choice([0, 1])
        conf = random.choices([0.9, 0.7, 0.5, 0.3], weights=[0.4, 0.3, 0.2, 0.1])[0]

        score = (
            (1 if is_corp else 0.7) * 15 +
            (sources / 5) * 20 +
            (0 if bounce == 1 else 15) +
            (1 - last_updated / 365) * 10 +
            verified * 15 +
            social * 10 +
            conf * 15
        )

        dados.append({
            'name': name,
            'email': email,
            'type': 'corporate' if is_corp else 'personal',
            'sources': sources,
            'bounce': bounce,
            'last_updated_days': last_updated,
            'verified_domain': verified,
            'social_presence': social,
            'source_confidence': conf,
            'score': round(score, 2)
        })

    return pd.DataFrame(dados)

df = gerar_dados()

# --- Título
st.title("📊 Q7 — Email Quality Score Dashboard")

# --- KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Leads Totais", len(df))
col2.metric("Score Médio", f"{df['score'].mean():.2f}")
col3.metric("% com Bounce", f"{(df['bounce'].fillna(0).mean()*100):.1f}%")
col4.metric("% Corporativo", f"{(df['type'].value_counts(normalize=True).get('corporate', 0)*100):.1f}%")
col5.metric("% com Redes Sociais", f"{(df['social_presence'].mean()*100):.1f}%")
col6.metric("Score Fonte > 0.7", f"{df[df['source_confidence'] >= 0.7]['score'].mean():.2f}")

# --- Gráficos e tabela lado a lado
col1, col2, col3 = st.columns(3)

# Gráfico 1: Score médio por tipo
with col1:
    st.markdown("### 📧 Score por Tipo de E-mail")
    fig1 = px.bar(df.groupby("type")["score"].mean().reset_index(), x="type", y="score", color="type",
                  color_discrete_map={"corporate": "#4CAF50", "personal": "#FFC107"}, text_auto='.2f')
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Score médio com/sem bounce
with col2:
    st.markdown("### 🚫 Score vs Bounce")
    df['bounce_status'] = df['bounce'].apply(lambda x: 'Sem bounce' if x != 1 else 'Com bounce')
    fig2 = px.bar(df.groupby("bounce_status")["score"].mean().reset_index(), x="bounce_status", y="score",
                  color="bounce_status", color_discrete_map={"Com bounce": "#E74C3C", "Sem bounce": "#2ECC71"},
                  text_auto='.2f')
    st.plotly_chart(fig2, use_container_width=True)

# Tabela dos Top 5
with col3:
    st.markdown("### 🏆 Top 5 Contatos")
    top = df.sort_values(by="score", ascending=False).head(5)[["name", "email", "type", "score"]]
    st.dataframe(top, use_container_width=True, height=270)