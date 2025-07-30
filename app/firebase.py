import os
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.getenv("FIREBASE_CREDENTIALS")
if not cred_path:
    raise ValueError("FIREBASE_CREDENTIALS environment variable is not set or is empty.")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()