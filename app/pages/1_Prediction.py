import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

st.set_page_config(page_title="Prédiction", layout="wide")

RACINE = Path(__file__).resolve().parent.parent.parent


@st.cache_resource
def charger_modele():
    return joblib.load(RACINE / "models" / "churn_model.joblib")


@st.cache_data
def charger_donnees():
    return pd.read_csv(RACINE / "data" / "telco_clean.csv")


modele = charger_modele()
df = charger_donnees()

st.title("Prédiction du churn pour un client")
st.write("Renseigne les caractéristiques d'un client pour estimer sa probabilité de départ.")


def choix(colonne, label):
    return st.selectbox(label, sorted(df[colonne].unique()))


col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Profil")
    gender = choix("gender", "Genre")
    senior = st.selectbox("Senior", [0, 1], format_func=lambda x: "Oui" if x else "Non")
    partner = choix("Partner", "En couple")
    dependents = choix("Dependents", "Personnes à charge")
    tenure = st.slider("Ancienneté (mois)", 0, 72, 12)

with col2:
    st.subheader("Services")
    phone = choix("PhoneService", "Service téléphone")
    multiple = choix("MultipleLines", "Lignes multiples")
    internet = choix("InternetService", "Service internet")
    security = choix("OnlineSecurity", "Sécurité en ligne")
    backup = choix("OnlineBackup", "Sauvegarde en ligne")
    protection = choix("DeviceProtection", "Protection appareil")
    support = choix("TechSupport", "Support technique")
    tv = choix("StreamingTV", "Streaming TV")
    movies = choix("StreamingMovies", "Streaming films")

with col3:
    st.subheader("Contrat et facturation")
    contrat = choix("Contract", "Contrat")
    paperless = choix("PaperlessBilling", "Facture dématérialisée")
    paiement = choix("PaymentMethod", "Mode de paiement")
    mensuel = st.number_input("Charges mensuelles ($)", 18.0, 120.0, 70.0, step=1.0)
    total = st.number_input("Charges totales ($)", 0.0, 9000.0, float(mensuel * tenure), step=10.0)

client = pd.DataFrame([{
    "gender": gender, "SeniorCitizen": senior, "Partner": partner,
    "Dependents": dependents, "tenure": tenure, "PhoneService": phone,
    "MultipleLines": multiple, "InternetService": internet,
    "OnlineSecurity": security, "OnlineBackup": backup,
    "DeviceProtection": protection, "TechSupport": support,
    "StreamingTV": tv, "StreamingMovies": movies, "Contract": contrat,
    "PaperlessBilling": paperless, "PaymentMethod": paiement,
    "MonthlyCharges": mensuel, "TotalCharges": total,
}])

st.divider()

if st.button("Prédire", type="primary"):
    proba = modele.predict_proba(client)[0, 1]
    st.metric("Probabilité de churn", f"{proba:.1%}")
    st.progress(float(proba))

    if proba >= 0.6:
        st.error("Risque élevé : ce client est susceptible de partir.")
    elif proba >= 0.3:
        st.warning("Risque moyen : à surveiller.")
    else:
        st.success("Risque faible : ce client devrait rester.")