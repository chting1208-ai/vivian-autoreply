from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VERIFY_TOKEN = "vivian_webhook_2024"
ACCESS_TOKEN = "IGAAXPrqTf5ZBhBZAGI3QUdzNjZA4QlVHU29XRnd0Y2VDbUxDbll2N2Frai1lMDFVZAVlnZAjdUUWlsTTdUS0V2dDlqbXY3YXJBblRQSU1yY2pmUWpUZAGY4ZAEpvSHctbDVZANmpwMVVrazdTZAU1YdWhaRk5TeExEcjZAoaHBKaS00N1pEZAwZDZD"

LAZY_PACK_MESSAGE = """感謝你的私訊！這是我準備的懶人包：

重點1：（你的內容）
重點2：（你的內容）
重點3：（你的內容）

更多資訊：（你的連結）

有任何問題歡迎繼續私訊我"""

KEYWORDS = ["懶人包", "+1", "資料", "想要"]

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "驗證失敗", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("=== 收到 Webhook ===")
    if data.get("object") == "instagram":
        MY_ID = "17841401095939446"
        for entry in data.get("entry", []):
            for msg_event in entry.get("messaging", []):
                sender_id = msg_event.get("sender", {}).get("id")
                if sender_id == MY_ID:
                    continue
                msg_text = msg_event.get("message", {}).get("text", "").lower()
                print(f"收到私訊: {msg_text} 來自: {sender_id}")
                if any(k in msg_text for k in KEYWORDS):
                    print(f"關鍵字符合！傳送懶人包")
                    send_dm(sender_id, LAZY_PACK_MESSAGE)
    return jsonify({"status": "ok"}), 200

def send_dm(user_id, message):
    url = "https://graph.instagram.com/v21.0/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print(f"傳送結果: {r.status_code}, {r.text}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
