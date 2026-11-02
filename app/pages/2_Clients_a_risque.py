import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

st.set_page_config(page_title="Clients à risque", layout="wide")

RACINE = Path(__file__).resolve().parent.parent.parent


@st.cache_resource
def charger_modele():
    return joblib.load(RACINE / "models" / "churn_model.joblib")


@st.cache_data
def charger_donnees():
    return pd.read_csv(RACINE / "data" / "telco_clean.csv")


@st.cache_data
def calculer_scores():
    modele = charger_modele()
    df = charger_donnees()
    X = df.drop(columns=["customerID", "Churn"])
    resultat = df.copy()
    resultat["Proba_churn"] = modele.predict_proba(X)[:, 1]
    return resultat


st.title("Clients à risque")
st.write("Clients classés par probabilité de départ, du plus risqué au moins risqué.")

df = calculer_scores()

# Filtres dans la barre latérale
st.sidebar.header("Filtres")
seuil = st.sidebar.slider("Probabilité minimale de churn", 0.0, 1.0, 0.5, 0.05)
contrats = st.sidebar.multiselect(
    "Type de contrat", df["Contract"].unique(), default=list(df["Contract"].unique())
)

filtre = df[(df["Proba_churn"] >= seuil) & (df["Contract"].isin(contrats))]
filtre = filtre.sort_values("Proba_churn", ascending=False)

# Indicateurs
col1, col2, col3 = st.columns(3)
col1.metric("Clients à risque", f"{len(filtre)}")
col2.metric("Part de la base", f"{len(filtre) / len(df):.1%}")
col3.metric("Revenu mensuel à risque", f"{filtre['MonthlyCharges'].sum():,.0f} $")

# Tableau
colonnes = ["customerID", "Proba_churn", "Contract", "tenure",
            "MonthlyCharges", "InternetService", "PaymentMethod"]
st.dataframe(
    filtre[colonnes],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Proba_churn": st.column_config.ProgressColumn(
            "Probabilité de churn", min_value=0.0, max_value=1.0, format="%.2f"
        )
    },
)

# Export CSV
st.download_button(
    "Télécharger la liste en CSV",
    data=filtre[colonnes].to_csv(index=False).encode("utf-8"),
    file_name="clients_a_risque.csv",
    mime="text/csv",
)