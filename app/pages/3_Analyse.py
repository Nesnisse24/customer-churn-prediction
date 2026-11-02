import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Analyse", layout="wide")

RACINE = Path(__file__).resolve().parent.parent.parent


@st.cache_data
def charger_donnees():
    df = pd.read_csv(RACINE / "data" / "telco_clean.csv")
    # Au cas où Churn serait encore en texte (Yes/No)
    if df["Churn"].dtype == object or str(df["Churn"].dtype) == "str":
        df["Churn"] = (df["Churn"] == "Yes").astype(int)
    df["Tranche_anciennete"] = pd.cut(
        df["tenure"],
        bins=[-1, 6, 12, 24, 48, 72],
        labels=["0-6 mois", "7-12 mois", "13-24 mois", "25-48 mois", "49-72 mois"],
    )
    return df


df = charger_donnees()

st.title("Analyse du churn")

# Filtres
st.sidebar.header("Filtres")
contrats = st.sidebar.multiselect(
    "Type de contrat", df["Contract"].unique(), default=list(df["Contract"].unique())
)
internet = st.sidebar.multiselect(
    "Service internet", df["InternetService"].unique(),
    default=list(df["InternetService"].unique()),
)
paiements = st.sidebar.multiselect(
    "Mode de paiement", df["PaymentMethod"].unique(),
    default=list(df["PaymentMethod"].unique()),
)
anc_min, anc_max = st.sidebar.slider(
    "Ancienneté (mois)", int(df["tenure"].min()), int(df["tenure"].max()),
    (int(df["tenure"].min()), int(df["tenure"].max())),
)

f = df[
    df["Contract"].isin(contrats)
    & df["InternetService"].isin(internet)
    & df["PaymentMethod"].isin(paiements)
    & df["tenure"].between(anc_min, anc_max)
]

if f.empty:
    st.warning("Aucun client ne correspond à ces filtres.")
    st.stop()

# Indicateurs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Clients", f"{len(f):,}")
c2.metric("Taux de churn", f"{f['Churn'].mean():.1%}",
          delta=f"{f['Churn'].mean() - df['Churn'].mean():+.1%} vs base totale",
          delta_color="inverse")
c3.metric("Clients partis", f"{int(f['Churn'].sum()):,}")
c4.metric("Revenu mensuel perdu", f"{f.loc[f['Churn'] == 1, 'MonthlyCharges'].sum():,.0f} $")


def taux_par(colonne, titre, ordre=None):
    t = f.groupby(colonne, observed=True)["Churn"].mean().reset_index()
    t["Churn"] = t["Churn"] * 100
    fig = px.bar(t, x=colonne, y="Churn", title=titre, text_auto=".1f",
                 labels={"Churn": "Taux de churn (%)"})
    if ordre:
        fig.update_xaxes(categoryorder="array", categoryarray=ordre)
    return fig


col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(taux_par("Contract", "Taux de churn par type de contrat"))
with col_b:
    st.plotly_chart(taux_par(
        "Tranche_anciennete", "Taux de churn par ancienneté",
        ["0-6 mois", "7-12 mois", "13-24 mois", "25-48 mois", "49-72 mois"],
    ))

col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(taux_par("InternetService", "Taux de churn par service internet"))
with col_d:
    st.plotly_chart(taux_par("PaymentMethod", "Taux de churn par mode de paiement"))

f_box = f.assign(Statut=f["Churn"].map({0: "Reste", 1: "Part"}))
fig_box = px.box(f_box, x="Statut", y="MonthlyCharges", color="Statut",
                 title="Charges mensuelles selon le churn",
                 labels={"MonthlyCharges": "Charges mensuelles ($)"})
st.plotly_chart(fig_box)