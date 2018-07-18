import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.Certificate('dsn-tracker-firebase-adminsdk-fcee1-d0c0dd6de5.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

address_ref = db.collection(u'peer').document(u'address')
address_ref.set({
    'list': [
        "http://a2b8f7fb.ngrok.io",
        "http://1a902fa4.ngrok.io",
        "http://497b8815.ngrok.io"
    ]
})
