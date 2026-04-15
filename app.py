import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from keywords import get_content_by_keyword

load_dotenv()

app = Flask(__name__)

# 追蹤每個用戶的狀態
# { user_id: { "step": "waiting_ok" | "waiting_button", "content": {...} } }
user_states = {}

# 防止重複處理同一則留言
processed_comments = set()


def get_tokens():
    return os.getenv("ACCESS_TOKEN"), os.getenv("IG_USER_ID")


def send_message(user_id: str, text: str, quick_replies=None):
    """發送私訊給指定用戶"""
    access_token, ig_user_id = get_tokens()
    url = f"https://graph.instagram.com/v21.0/{ig_user_id}/messages"

    message = {"text": text}
    if quick_replies:
        message["quick_replies"] = quick_replies

    payload = {
        "recipient": {"id": user_id},
        "message": message,
        "access_token": access_token,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"[OK] 已發送私訊給 {user_id}")
    else:
        print(f"[ERROR] 發送失敗: {response.status_code} {response.text}")
    return response


def send_follow_button(user_id: str):
    """發送「已追蹤」按鈕"""
    quick_replies = [
        {
            "content_type": "text",
            "title": "已追蹤 ✅",
            "payload": "FOLLOWED_CONFIRMED",
        }
    ]
    send_message(
        user_id,
        "還差一步！這個內容是專屬粉絲的 ✨\n\n追蹤我們之後，點擊下方按鈕確認 🎉",
        quick_replies=quick_replies,
    )


def send_content(user_id: str, content: dict):
    """發送最終懶人包內容"""
    send_message(user_id, content["content"])


@app.route("/health", methods=["GET"])
def health():
    access_token, ig_user_id = get_tokens()
    return jsonify({
        "status": "ok",
        "verify_token_set": bool(os.getenv("VERIFY_TOKEN")),
        "access_token_set": bool(access_token),
        "ig_user_id_set": bool(ig_user_id),
    }), 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta Webhook 驗證"""
    verify_token = os.getenv("VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        print("[OK] Webhook 驗證成功")
        return challenge, 200
    print("[ERROR] Webhook 驗證失敗")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """接收 Instagram 通知"""
    data = request.get_json()
    print(f"[收到] {data}")

    try:
        for entry in data.get("entry", []):

            # ── 私訊觸發（entry.messaging 格式）──
            for msg_event in entry.get("messaging", []):
                handle_message(msg_event)

            # ── 留言觸發（entry.changes 格式）──
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})
                if field == "comments":
                    handle_comment(value)

    except Exception as e:
        print(f"[ERROR] 處理失敗: {e}")

    return jsonify({"status": "ok"}), 200


def handle_comment(value: dict):
    """處理留言事件"""
    comment_id = value.get("id")
    comment_text = value.get("text", "")
    commenter_id = value.get("from", {}).get("id")

    if not commenter_id or not comment_id:
        return
    if comment_id in processed_comments:
        return

    content = get_content_by_keyword(comment_text)
    if not content:
        print(f"[略過] 無關鍵字，留言：{comment_text!r}")
        return

    processed_comments.add(comment_id)
    print(f"[觸發] 關鍵字命中，留言：{comment_text!r}")

    # 發送第一則私訊
    send_message(commenter_id, content["initial_message"])

    # 記錄用戶狀態
    user_states[commenter_id] = {
        "step": "waiting_ok",
        "content": content,
    }


def handle_message(value: dict):
    """處理私訊事件"""
    sender_id = value.get("sender", {}).get("id")
    _, ig_user_id = get_tokens()

    # 忽略自己發出的訊息
    if sender_id == ig_user_id:
        return

    # 檢查是否為按鈕點擊（quick reply）
    message = value.get("message", {})
    quick_reply = message.get("quick_reply", {})

    if quick_reply.get("payload") == "FOLLOWED_CONFIRMED":
        # 用戶點了「已追蹤」按鈕
        state = user_states.get(sender_id)
        if state:
            print(f"[按鈕] {sender_id} 點了已追蹤按鈕")
            send_content(sender_id, state["content"])
            del user_states[sender_id]
        return

    # 檢查是否回覆「OK」
    text = message.get("text", "").strip().lower()
    if text in ["ok", "okay", "好", "好的", "已追蹤", "追蹤了"]:
        state = user_states.get(sender_id)
        if state and state["step"] == "waiting_ok":
            print(f"[OK] {sender_id} 回覆了 OK")
            user_states[sender_id]["step"] = "waiting_button"
            send_follow_button(sender_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
