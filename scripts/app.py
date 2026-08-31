# app.py - API FastAPI pour Hugging Face

import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import os

# ------------------------------------------------------------
# 1. Initialisation
# ------------------------------------------------------------
app = FastAPI(
    title="GetAround - API de prédiction de prix",
    description="Prédit le prix de location journalier d'une voiture.",
    version="1.0.0"
)

# ------------------------------------------------------------
# 2. Chargement du modèle
# ------------------------------------------------------------
# Pour Hugging Face, le modèle doit être dans le dossier 'models/'
# à la racine du Space (ou on le cherche dans le dossier parent)
MODEL_PATH = "models/pipeline_xgboost.joblib"

# Si on est en local, on remonte d'un dossier
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "../models/pipeline_xgboost.joblib"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modèle non trouvé à {MODEL_PATH}")

pipeline = joblib.load(MODEL_PATH)
print("✅ Modèle chargé avec succès !")

# ------------------------------------------------------------
# 3. Modèles Pydantic
# ------------------------------------------------------------
class PredictionRawInput(BaseModel):
    input: List[List[Union[str, float, bool]]]

# ------------------------------------------------------------
# 4. Endpoints
# ------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API GetAround !", "docs": "/docs"}

@app.post("/predict_raw")
async def predict_raw(data: PredictionRawInput):
    """
    Endpoint conforme à l'énoncé.
    Format : {"input": [[...], [...]]}
    Ordre des colonnes : model_key, mileage, engine_power, fuel, paint_color,
    car_type, private_parking_available, has_gps, has_air_conditioning,
    automatic_car, has_getaround_connect, has_speed_regulator, winter_tires
    """
    try:
        columns = [
            'model_key', 'mileage', 'engine_power', 'fuel', 'paint_color',
            'car_type', 'private_parking_available', 'has_gps',
            'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
            'has_speed_regulator', 'winter_tires'
        ]
        df = pd.DataFrame(data.input, columns=columns)
        predictions = pipeline.predict(df)
        return {"prediction": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------
# 5. Lancement (uniquement si exécuté directement)
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)  # Port par défaut de HF