from flask import Flask, request, jsonify
import json
import hmac
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)

with open("known_hashes.json", "r") as f:
    trusted_hash = json.load(f)["trusted_hash"]

with open("keys/private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

SERVER_SECRET = b"bank_server_secret"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    client_hash = data.get("hash")

    if client_hash != trusted_hash:
        return jsonify({
            "status": "rejected",
            "message": "Session expired / Fake APK detected"
        }), 400

    key_value = hmac.new(SERVER_SECRET, client_hash.encode(), hashlib.sha256).hexdigest()

    signature = private_key.sign(
        client_hash.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return jsonify({
        "status": "approved",
        "key": key_value,
        "signature": signature.hex(),
        "message": "APK verified successfully"
    })

if __name__ == "__main__":
    app.run(debug=True)