from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VERIFY_TOKEN = "vivian_webhook_2024"
ACCESS_TOKEN = "IGAAXPrqTf5ZBhBZAFlWNHY4OVBveDNKQ2lhRTduWHp2UllrZAUk4QmlGMzNkanI2UzdNc1c2cC1GN3ZALYWVmWF96Wnk5clpVc2IyMEo1RW9LMkpLUlljNnlOd1cxYk0zREV6QnRDcUh1LUU0UkVJTjZA2QndRSVVPeV9DUGNObjJxVQZDZD"

LAZY_PACK_MESSAGE = """感謝你的私訊！這是我準備的懶人包：

重點1：（你的內容）
重點2：（你的內容）
重點3：（你的內容）

更多資訊：（你的連結）

有任何問題歡迎繼續私訊我"""

# 留言偵測到關鍵字後，公開回覆這段文字引導對方傳 DM
COMMENT_REPLY = "已私訊你了！請傳訊息給我，馬上就能收到懶人包 😊"

KEYWORDS = ["懶人包", "+1", "資料", "想要"]

# 用來記錄已處理過的訊息/留言 ID（防止重複回覆）
processed_ids = set()

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

            # 處理私訊（DM）
            for msg_event in entry.get("messaging", []):
                sender_id = msg_event.get("sender", {}).get("id")
                if sender_id == MY_ID:
                    continue

                msg_id = msg_event.get("message", {}).get("mid", "")
                if msg_id and msg_id in processed_ids:
                    print(f"已處理過此訊息，略過：{msg_id}")
                    continue
                if msg_id:
                    processed_ids.add(msg_id)

                msg_text = msg_event.get("message", {}).get("text", "").lower()
                print(f"收到私訊: {msg_text} 來自: {sender_id}")
                if any(k in msg_text for k in KEYWORDS):
                    print(f"關鍵字符合！傳送懶人包")
                    send_dm(sender_id, LAZY_PACK_MESSAGE)

            # 處理留言（Comments）
            for change in entry.get("changes", []):
                if change.get("field") != "comments":
                    continue
                value = change.get("value", {})
                comment_id = value.get("id", "")
                comment_text = value.get("text", "").lower()
                commenter_id = value.get("from", {}).get("id", "")

                print(f"收到留言: {comment_text} 來自: {commenter_id}")

                if commenter_id == MY_ID:
                    continue

                if comment_id and comment_id in processed_ids:
                    print(f"已處理過此留言，略過：{comment_id}")
                    continue
                if comment_id:
                    processed_ids.add(comment_id)

                if any(k in comment_text for k in KEYWORDS):
                    print(f"留言關鍵字符合！回覆留言引導私訊")
                    reply_to_comment(comment_id, COMMENT_REPLY)

    return jsonify({"status": "ok"}), 200

def send_dm(user_id, message):
    url = "https://graph.instagram.com/v21.0/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print(f"傳送私訊結果: {r.status_code}, {r.text}")

def reply_to_comment(comment_id, message):
    url = f"https://graph.instagram.com/v21.0/{comment_id}/replies"
    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print(f"回覆留言結果: {r.status_code}, {r.text}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
