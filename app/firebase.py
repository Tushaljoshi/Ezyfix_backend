import os
import json
from firebase_admin import credentials, firestore, initialize_app

firebase_creds = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_creds:
    raise ValueError("FIREBASE_CREDENTIALS environment variable is not set or is empty.")

cred = credentials.Certificate(json.loads(firebase_creds))
default_app = initialize_app(cred)

db = firestore.client()
