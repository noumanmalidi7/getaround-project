# Projet GetAround - Analyse & Prédiction

Ce projet répond au besoin de GetAround (Airbnb de la voiture) en deux volets :
1. **Dashboard** : aide le Product Manager à choisir le délai minimum entre deux locations.
2. **API** : prédit le prix de location journalier via un modèle XGBoost.

## Lancer le projet en local

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

#2. Installer les dépendances: 
pip install -r requirements.txt

##3 Lancer le Dashboard Streamlit: 
streamlit run streamlit_app.py


##4 Lancer l'API FastAPI (dans un autre terminal):
uvicorn scripts.app:app --reload --port 8888

##Tester l'API:
python scripts/test_api.py




