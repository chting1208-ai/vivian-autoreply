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
    "999": {
        "name": "預告登記懶人包",
        "initial_message": "嗨！想領取【預告登記懶人包】嗎？\n\n請先完成以下步驟：\n✅ 追蹤金融女子薇薇安的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你🙋🏻‍♀️",
        "content": "已收到你的留言😻 預告登記懶人包來囉～\nhttps://gemini.google.com/share/8fbd9d02ab4b",
    },
    "666": {
        "name": "共同持有懶人包",
        "initial_message": "嗨！想領取【共同持有懶人包】嗎？\n\n請先完成以下步驟：\n✅ 追蹤金融女子薇薇安的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你🙋🏻‍♀️",
        "content": "已收到您的留言💕\n夫妻共同持有懶人包來囉🏠\nhttps://gemini.google.com/share/f23a683b46a4",
    },
    "養老": {
        "name": "養老懶人包",
        "initial_message": "嗨！想領取【養老懶人包】嗎？\n\n請先完成以下步驟：\n✅ 追蹤金融女子薇薇安的帳號\n✅ 追蹤後回覆「OK」\n\n完成後就會自動發送給你🙋🏻‍♀️",
        "content": "已收到您的留言💕\n以房養老懶人包來囉🏠\nhttps://gemini.google.com/share/d46a5d565128",
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
