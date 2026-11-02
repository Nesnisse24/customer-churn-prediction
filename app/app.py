import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Churn Dashboard", layout="wide")

RACINE = Path(__file__).resolve().parent.parent


@st.cache_data
def charger_donnees():
    return pd.read_csv(RACINE / "data" / "telco_clean.csv")


df = charger_donnees()

st.title("Tableau de bord : churn client")

# ---------- Filtres (barre latérale) ----------
st.sidebar.header("Filtres")

contrats_dispo = sorted(df["Contract"].unique())
contrats = st.sidebar.multiselect("Type de contrat", contrats_dispo, default=contrats_dispo)

internet_dispo = sorted(df["InternetService"].unique())
internet = st.sidebar.multiselect("Service internet", internet_dispo, default=internet_dispo)

anciennete = st.sidebar.slider("Ancienneté (mois)", 0, 72, (0, 72))

filtre = df[
    df["Contract"].isin(contrats)
    & df["InternetService"].isin(internet)
    & df["tenure"].between(anciennete[0], anciennete[1])
]

if filtre.empty:
    st.warning("Aucun client ne correspond à ces filtres.")
    st.stop()

# ---------- KPIs ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de clients", f"{len(filtre):,}".replace(",", " "))
col2.metric("Taux de churn", f"{filtre['Churn'].mean():.1%}")
col3.metric("Clients partis", f"{filtre['Churn'].sum():,}".replace(",", " "))
revenu_perdu = filtre.loc[filtre["Churn"] == 1, "MonthlyCharges"].sum()
col4.metric("Revenu mensuel perdu", f"{revenu_perdu:,.0f} $".replace(",", " "))

st.divider()

# ---------- Graphiques ----------
gauche, droite = st.columns(2)

with gauche:
    par_contrat = filtre.groupby("Contract")["Churn"].mean().reset_index()
    fig1 = px.bar(
        par_contrat, x="Contract", y="Churn",
        title="Taux de churn par type de contrat",
        labels={"Churn": "Taux de churn", "Contract": "Contrat"},
    )
    fig1.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig1)

with droite:
    par_paiement = filtre.groupby("PaymentMethod")["Churn"].mean().reset_index()
    fig2 = px.bar(
        par_paiement, x="Churn", y="PaymentMethod", orientation="h",
        title="Taux de churn par mode de paiement",
        labels={"Churn": "Taux de churn", "PaymentMethod": "Paiement"},
    )
    fig2.update_xaxes(tickformat=".0%")
    st.plotly_chart(fig2)