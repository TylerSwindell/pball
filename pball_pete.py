from flask import Flask, request, jsonify
from get_courts_lib import get_availability_dict
import requests
import threading
from datetime import datetime

from nacl.signing import VerifyKey  # pip install PyNaCl
from nacl.exceptions import BadSignatureError

app = Flask(__name__)

PUBLIC_KEY = "c3c19b382aec52f3c52a0a60d6cf1c3350f67d0a3f6d004736e36f24ee62b17b"


def verify_signature(req):
    """Verify Discord interaction signature."""
    signature = req.headers.get("X-Signature-Ed25519")
    timestamp = req.headers.get("X-Signature-Timestamp")
    body = req.data.decode("utf-8")

    if not signature or not timestamp:
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False


@app.route("/interactions", methods=["POST"])
def interactions():
    print(f"[DEBUG] Received request")

    # Verify the request signature
    if not verify_signature(request):
        print("[DEBUG] Signature verification failed")
        return jsonify({"error": "Invalid signature"}), 401

    print("[DEBUG] Signature verified")
    data = request.json
    print(f"[DEBUG] Request type: {data.get('type')}")

    # Discord sends a PING on setup — must respond with PONG
    if data["type"] == 1:
        print("[DEBUG] Responding to PING")
        return jsonify({"type": 1})

    # Slash command interaction (type 2)
    if data["type"] == 2:
        print("[DEBUG] Slash command received")
        command = data["data"]["name"]
        if command == "get_pball_courts":
            print("[DEBUG] get_pball_courts command")
            options = {
                opt["name"]: opt["value"] for opt in data["data"].get("options", [])
            }
            check_date = options.get("date")
            after_time = options.get("time")

            try:
                print(f"[DEBUG] Fetching availability for {check_date}, after_time={after_time}")
                availability = get_availability_dict(check_date, after_time=after_time)
                print(f"[DEBUG] Got {len(availability)} courts")

                if not availability:
                    content = "No courts available for that date and time."
                else:
                    lines = ["**Available Courts:**\n"]
                    for court_name, info in availability.items():
                        lines.append(
                            f"• {court_name}: {info['start_time']} ({info['duration_str']})"
                        )
                    content = "\n".join(lines)

                print(f"[DEBUG] Sending response")
                return jsonify(
                    {
                        "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
                        "data": {"content": content},
                    }
                )
            except Exception as e:
                print(f"[DEBUG] Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify(
                    {
                        "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
                        "data": {"content": f"Error: {str(e)}"},
                    }
                )

    # Default fallback (no matching command or interaction type)
    print("[DEBUG] No matching command, returning default response")
    return jsonify({"type": 1})


if __name__ == "__main__":
    app.run(port=8181)
