# ============================================================
# 關鍵字設定檔 - 你只需要修改這裡！
# ============================================================
#
# 格式說明：
#   "留言關鍵字": {
#       "name": "懶人包名稱（顯示在第一則私訊）",
#       "initial_message": "粉絲留言後收到的第一則私訊",
#       "content": "點按鈕後收到的懶人包內容（連結＋說明）",
#   },
#
# ============================================================

KEYWORD_CONTENT = {
    "懶人包": {
        "name": "理財懶人包",
        "initial_message": "嗨！想領取【理財懶人包】嗎？📚\n\n請先完成以下步驟：\n✅ 追蹤我們的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你！",
        "content": "這是你的理財懶人包 📚\n\n👉 https://你的連結放這裡\n\n這份懶人包包含了...\n（在這裡加上簡單說明）",
    },
    "+1": {
        "name": "存錢攻略",
        "initial_message": "嗨！想領取【存錢攻略】嗎？💰\n\n請先完成以下步驟：\n✅ 追蹤我們的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你！",
        "content": "這是你的存錢攻略 💰\n\n👉 https://你的連結放這裡\n\n這份攻略包含了...\n（在這裡加上簡單說明）",
    },
    "投資": {
        "name": "投資入門指南",
        "initial_message": "嗨！想領取【投資入門指南】嗎？📈\n\n請先完成以下步驟：\n✅ 追蹤我們的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你！",
        "content": "這是你的投資入門指南 📈\n\n👉 https://你的連結放這裡\n\n這份指南包含了...\n（在這裡加上簡單說明）",
    },
    # ↓ 在這裡繼續新增更多關鍵字 ↓
}


def get_content_by_keyword(comment_text: str):
    """根據留言找對應的懶人包，回傳 dict 或 None"""
    comment_lower = comment_text.lower().strip()
    for keyword, content in KEYWORD_CONTENT.items():
        if keyword.lower() in comment_lower:
            return content
    return None
