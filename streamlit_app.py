import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard GetAround", layout="wide")
st.title("🚗 GetAround - Analyse des retards")

# --- Affichage de l'état du chargement ---
st.write("🔍 Recherche du fichier de données...")

# Chemin du fichier
file_path = "Data/get_around_delay_analysis.xlsx"

# Vérifier si le fichier existe
if not os.path.exists(file_path):
    st.error(f"❌ Fichier introuvable : `{file_path}`")
    st.info("Veuillez placer le fichier `get_around_delay_analysis.xlsx` dans le dossier `Data/` à la racine du projet.")
    st.stop()

st.success(f"✅ Fichier trouvé : `{file_path}`")

# Chargement des données
@st.cache_data
def load_data():
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return pd.DataFrame()

data = load_data()

if data.empty:
    st.error("❌ Les données sont vides. Vérifiez le fichier.")
    st.stop()

st.write(f"✅ Données chargées : {len(data)} lignes")

# Renommer les colonnes
data = data.rename(columns={
    "checkin_type": "type",
    "delay_at_checkout_in_minutes": "delay",
    "previous_ended_rental_id": "prev_id",
    "time_delta_with_previous_rental_in_minutes": "time_delta"
})

# Filtre : locations terminées
data_enable = data[data['state'] == 'ended'].copy()

# --- COLONNE DE GAUCHE : Paramètres ---
st.sidebar.header("Paramètres")
threshold_mobile = st.sidebar.slider("Seuil pour Mobile (minutes)", 0, 300, 120)
threshold_connect = st.sidebar.slider("Seuil pour Connect (minutes)", 0, 300, 60)

# --- ANALYSE 1 : Impact du seuil ---
st.subheader("📊 Impact du seuil sur les locations")
df_miss = pd.DataFrame(data_enable['time_delta'].dropna().unique(), columns=['threshold'])
df_miss = df_miss.sort_values('threshold')

data_mobile = data_enable[data_enable['type'] == 'mobile']
data_connect = data_enable[data_enable['type'] == 'connect']
nb_total = len(data_enable)

df_miss['mobile_data'] = df_miss['threshold'].apply(lambda thr: sum(data_mobile['time_delta'] < thr) * 100 / nb_total)
df_miss['connect_data'] = df_miss['threshold'].apply(lambda thr: sum(data_connect['time_delta'] < thr) * 100 / nb_total)
df_miss['global_data'] = df_miss['mobile_data'] + df_miss['connect_data']

fig1 = px.bar(df_miss, x='threshold', y=['mobile_data', 'connect_data', 'global_data'],
              barmode='group', labels={'value': 'Locations affectées (%)', 'threshold': 'Seuil (minutes)'},
              title="Pourcentage de locations affectées")
st.plotly_chart(fig1, use_container_width=True)

# --- ANALYSE 2 : Retards ---
st.subheader("⏰ Proportion de retards")
data_enable['late_or_early'] = data_enable['delay'].map(lambda v: 'En retard' if v > 0 else 'En avance')
fig2 = px.pie(data_enable, names='late_or_early', title="Retards vs Avances")
st.plotly_chart(fig2, use_container_width=True)

# --- ANALYSE 3 : Cas problématiques ---
st.subheader("⚠️ Cas problématiques (retard précédent > time_delta)")
data_join = data.merge(data[['rental_id', 'type', 'delay']],
                       how='inner', left_on='prev_id', right_on='rental_id',
                       suffixes=('_actuel', '_precedent'))

data_join['problematique'] = data_join['time_delta'] < data_join['delay_precedent']
data_join['label'] = data_join['problematique'].map(lambda v: 'Problématique' if v else 'Non problématique')

col1, col2 = st.columns(2)
with col1:
    fig3 = px.pie(data_join, names='label', title="Cas problématiques")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    pct = data_join['problematique'].mean() * 100
    st.metric("Pourcentage de cas problématiques", f"{pct:.2f}%")

# --- ANALYSE 4 : Distribution des retards ---
st.subheader("📈 Distribution des retards (sans outliers)")
to_keep = abs(data_enable['delay'] - data_enable['delay'].mean()) <= 2 * data_enable['delay'].std()
data_red = data_enable[to_keep]
fig4 = px.histogram(data_red, x='delay', nbins=100, color='type', barmode='overlay',
                    marginal='box', title="Distribution des retards par type")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Dashboard réalisé pour l'étude de cas GetAround - recommandations : 120 min (Mobile), 60 min (Connect)")
