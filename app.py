import os
import random
import threading
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from keywords import get_content_by_keyword

load_dotenv()

app = Flask(__name__)

# 追蹤每個用戶的狀態
user_states = {}

# 防止重複處理同一則留言
processed_comments = set()


def get_tokens():
    return os.getenv("ACCESS_TOKEN"), os.getenv("IG_USER_ID")


def send_message(user_id: str, text: str):
    """發送私訊給指定用戶（用於回覆 OK 後的懶人包）"""
    access_token, ig_user_id = get_tokens()
    url = f"https://graph.instagram.com/v21.0/{ig_user_id}/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text},
        "access_token": access_token,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[OK] 已發送私訊給 {user_id}")
        else:
            print(f"[ERROR] 私訊發送失敗: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] 私訊例外: {e}")


def send_private_reply(comment_id: str, text: str):
    """透過留言 ID 發送私訊（Private Reply，可突破 24 小時限制）"""
    access_token, ig_user_id = get_tokens()
    url = f"https://graph.instagram.com/v21.0/{ig_user_id}/messages"
    payload = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": text},
        "access_token": access_token,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[OK] 已發送 Private Reply 給留言 {comment_id}")
        else:
            print(f"[ERROR] Private Reply 失敗: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] Private Reply 例外: {e}")


# 留言回覆的隨機文字
COMMENT_REPLIES = [
    "分享囉😻",
    "已私訊給你🙋🏻‍♀️",
    "快去收收訊息📩",
    "追蹤我💕 訊息才不會漏掉唷！",
    "傳給你囉～！請留意陌生訊息☺️",
    "懶人包飛過去惹✈️",
]

def reply_to_comment(comment_id: str):
    """自動回覆貼文留言"""
    access_token, _ = get_tokens()
    url = f"https://graph.instagram.com/v21.0/{comment_id}/replies"
    reply_text = random.choice(COMMENT_REPLIES)
    payload = {
        "message": reply_text,
        "access_token": access_token,
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"[OK] 已回覆留言：{reply_text}")
        else:
            print(f"[ERROR] 回覆留言失敗: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] 回覆留言例外: {e}")


def process_comment(comment_id: str, commenter_id: str, content: dict):
    """背景處理：同時回覆留言 + 發送私訊（各自獨立，互不影響）"""
    # 各自跑獨立 thread，確保兩個都會執行
    t1 = threading.Thread(target=reply_to_comment, args=(comment_id,))
    t2 = threading.Thread(target=send_private_reply, args=(comment_id, content["initial_message"]))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # 記錄用戶狀態（等待回覆 OK）
    user_states[commenter_id] = {
        "step": "waiting_ok",
        "content": content,
    }


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
    """接收 Instagram 通知 — 立即回應 Meta，背景處理"""
    data = request.get_json()
    print(f"[收到] {data}")

    # 立刻回應 Meta（避免超時），背景處理實際邏輯
    threading.Thread(target=process_webhook, args=(data,)).start()

    return jsonify({"status": "ok"}), 200


def process_webhook(data: dict):
    """背景處理 Webhook 內容"""
    try:
        for entry in data.get("entry", []):

            # ── 私訊觸發 ──
            for msg_event in entry.get("messaging", []):
                handle_message(msg_event)

            # ── 留言觸發 ──
            for change in entry.get("changes", []):
                if change.get("field") == "comments":
                    handle_comment(change.get("value", {}))

    except Exception as e:
        print(f"[ERROR] 背景處理失敗: {e}")


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

    # 背景同時執行：回覆留言 + 發私訊
    threading.Thread(target=process_comment, args=(comment_id, commenter_id, content)).start()


def handle_message(value: dict):
    """處理私訊事件"""
    sender_id = value.get("sender", {}).get("id")
    _, ig_user_id = get_tokens()

    # 忽略自己發出的訊息
    if sender_id == ig_user_id:
        return

    message = value.get("message", {})
    text = message.get("text", "").strip().lower()

    if text in ["ok", "okay", "好", "好的", "已追蹤", "追蹤了", "ok!"]:
        state = user_states.get(sender_id)
        if state and state["step"] == "waiting_ok":
            print(f"[OK] {sender_id} 回覆了 OK，發送懶人包")
            content = state["content"]
            del user_states[sender_id]
            threading.Thread(target=send_message, args=(sender_id, content["content"])).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
