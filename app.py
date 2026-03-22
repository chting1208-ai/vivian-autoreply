from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

VERIFY_TOKEN = "vivian_webhook_2024"
ACCESS_TOKEN = "IGAAXPrqTf5ZBhBZAFlaWHE1VHRVc3V1UHB5c2pHb3ByckpSYm9oLXQtQjh5LUZAQeEZA3WVFwenFKS2JXWjJjU3ZA5dHhrcW9QZADVQTmtzdzNad3BGMXVpWDQ5bDQ5aGItdTZAoaDVTbjZAaYUFMY2xrWVZAmNDNQbHJ5NU1SZATZAoc1AwcwZDZD"

LAZY_PACK_MESSAGE = """📦 感謝你的留言！這是我準備的懶人包：

💡 重點1：（你的內容）
💡 重點2：（你的內容）
💡 重點3：（你的內容）

🔗 更多資訊：（你的連結）

有任何問題歡迎繼續私訊我 😊"""

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
    print(f"=== 收到 Webhook ===")
    print(f"完整資料: {json.dumps(data, ensure_ascii=False)}")

    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            print(f"entry: {json.dumps(entry, ensure_ascii=False)}")
            for change in entry.get("changes", []):
                print(f"change field: {change.get('field')}")
                if change.get("field") == "comments":
                    comment_data = change.get("value", {})
                    comment_text = comment_data.get("text", "").lower()
                    commenter_id = comment_data.get("from", {}).get("id")
                    print(f"留言內容: {comment_text}")
                    print(f"留言者 ID: {commenter_id}")
                    keyword_match = any(k in comment_text for k in KEYWORDS)
                    print(f"關鍵字符合: {keyword_match}")
                    if keyword_match:
                        if commenter_id:
                            print(f"準備傳送 DM 給 {commenter_id}")
                            send_dm(commenter_id, LAZY_PACK_MESSAGE)
                        else:
                            print("錯誤：找不到留言者 ID")
    else:
        print(f"非 instagram 物件: {data.get('object')}")

    return jsonify({"status": "ok"}), 200

def send_dm(user_id, message):
    url = "https://graph.instagram.com/v21.0/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "access_token": ACCESS_TOKEN
    }
    print(f"傳送 DM 到 URL: {url}")
    print(f"recipient id: {user_id}")
    r = requests.post(url, json=payload)
    print(f"傳送結果: {r.status_code}, {r.text}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
