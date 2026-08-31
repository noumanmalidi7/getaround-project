# test_api.py - Tester l'API localement

import requests

BASE_URL = "http://localhost:8888"

print("🔍 Test 1 : Vérification du serveur...")
print(requests.get(f"{BASE_URL}/").json())

print("\n🔍 Test 2 : Endpoint /predict_raw (format liste)")
json_data = {
    "input": [
        ["Citroën", 183297, 120, "diesel", "white", "convertible", False, False, False, False, True, False, True],
        ["Citroën", 128035, 135, "diesel", "red", "convertible", True, True, False, False, True, True, True]
    ]
}
response = requests.post(f"{BASE_URL}/predict_raw", json=json_data)
print("Réponse :", response.json())

print("\n✅ Tests terminés.")