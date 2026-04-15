import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from keywords import get_reply

load_dotenv()

app = Flask(__name__)

sent_dmrecords = set()  # 防止重複發送（同一則留言只發一次）


def send_dm(user_id: str, message: str):
    """發送私訊給指定用戶"""
    access_token = os.getenv("ACCESS_TOKEN")
    ig_user_id = os.getenv("IG_USER_ID")
    url = f"https://graph.instagram.com/v21.0/{ig_user_id}/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "access_token": access_token,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"[OK] 已發送私訊給 {user_id}")
    else:
        print(f"[ERROR] 發送失敗: {response.status_code} {response.text}")
    return response


@app.route("/health", methods=["GET"])
def health():
    """健康檢查"""
    return jsonify({
        "status": "ok",
        "verify_token_set": bool(os.getenv("VERIFY_TOKEN")),
        "access_token_set": bool(os.getenv("ACCESS_TOKEN")),
        "ig_user_id_set": bool(os.getenv("IG_USER_ID")),
    }), 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta Webhook 驗證"""
    verify_token = os.getenv("VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print(f"[驗證] mode={mode}, token={token}, VERIFY_TOKEN={verify_token}")

    if mode == "subscribe" and token == verify_token:
        print("[OK] Webhook 驗證成功")
        return challenge, 200
    else:
        print("[ERROR] Webhook 驗證失敗")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """接收 Instagram 留言通知"""
    data = request.get_json()
    print(f"[收到] {data}")

    try:
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                if change.get("field") != "comments":
                    continue

                value = change.get("value", {})
                comment_id = value.get("id")
                comment_text = value.get("text", "")
                commenter_id = value.get("from", {}).get("id")

                if not commenter_id or not comment_id:
                    continue

                # 防止重複處理同一則留言
                if comment_id in sent_dmrecords:
                    continue

                reply_message = get_reply(comment_text)
                if reply_message:
                    sent_dmrecords.add(comment_id)
                    send_dm(commenter_id, reply_message)
                    print(f"[觸發] 關鍵字命中，留言：{comment_text!r}")
                else:
                    print(f"[略過] 無關鍵字，留言：{comment_text!r}")

    except Exception as e:
        print(f"[ERROR] 處理失敗: {e}")

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
