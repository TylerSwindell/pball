from flask import Flask, request, jsonify
import subprocess

# from nacl.signing import VerifyKey  # pip install PyNaCl
# from nacl.exceptions import BadSignatureError

app = Flask(__name__)

# PUBLIC_KEY = "your_discord_app_public_key"

# def verify_signature(req):
#     signature = req.headers.get("X-Signature-Ed25519")
#     timestamp = req.headers.get("X-Signature-Timestamp")
#     body = req.data.decode("utf-8")
#     verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
#     verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))

@app.route("/interactions", methods=["POST"])
def interactions():
    data = request.json

    # Discord sends a PING on setup — must respond with PONG
    if data["type"] == 1:
        return jsonify({"type": 1})

    # Slash command interaction (type 2)
    if data["type"] == 2:
        command = data["data"]["name"]
        if command == "hello":
            return jsonify({
                "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
                "data": {"content": "Hello from my server!"}
            })

if __name__ == "__main__":
    app.run(port=8181)