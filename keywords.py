# 關鍵字對應懶人包內容
# 可以自由新增、修改關鍵字和對應的訊息

KEYWORD_REPLIES = {
    "懶人包": "嗨！這是你要的懶人包 👉 [請把連結貼在這裡]",
    "+1": "嗨！感謝你的留言，這是相關資料 👉 [請把連結貼在這裡]",
    "資料": "嗨！這是詳細資料 👉 [請把連結貼在這裡]",
    # 在這裡新增更多關鍵字...
}

def get_reply(comment_text: str) -> str | None:
    """
    根據留言內容找對應的回覆。
    回傳訊息文字，若沒有符合的關鍵字則回傳 None。
    """
    comment_lower = comment_text.lower().strip()
    for keyword, reply in KEYWORD_REPLIES.items():
        if keyword.lower() in comment_lower:
            return reply
    return None
