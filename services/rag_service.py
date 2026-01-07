from services.embedding_service import EmbeddingService
from services.property_service import PropertyService

class RAGService:

    @staticmethod
    def is_followup_question(text: str) -> bool:
        keywords = [
            "link", "chi tiết", "liên hệ",
            "số điện thoại", "email", "contact"
        ]
        text = text.lower()
        return any(k in text for k in keywords)

    @staticmethod
    def build_context(user_text, session):
        followup = RAGService.is_followup_question(user_text)

        # =============================
        # CASE 1: FOLLOW-UP QUESTION
        # =============================
        if followup:
            property_ids = session.get("last_property_ids")

            if not property_ids:
                return (
                    "Bạn đang muốn xem link hoặc thông tin liên hệ của "
                    "bất động sản nào? Vui lòng hỏi trước về bất động sản.",
                    []
                )

        # =============================
        # CASE 2: NORMAL SEARCH
        # =============================
        else:
            property_ids = EmbeddingService.search(user_text)
            session["last_property_ids"] = property_ids

        # =============================
        # LOAD PROPERTIES
        # =============================
        properties = [
            PropertyService.get_property_by_id(pid)
            for pid in property_ids
            if PropertyService.get_property_by_id(pid)
        ]

        if not properties:
            return "KHÔNG CÓ DỮ LIỆU PHÙ HỢP.", []

        include_private = followup  # 🔥 chỉ bật khi hỏi link / liên hệ

        context = "\n".join(
            PropertyService.property_to_text(
                p,
                include_private=include_private
            )
            for p in properties
        )

        return context, property_ids

    @staticmethod
    def build_system_prompt(context):
        return f"""
Bạn là chatbot bất động sản của website Wealthuring.
CHỈ trả lời dựa trên dữ liệu được cung cấp.
KHÔNG suy đoán, KHÔNG bịa.

QUY TẮC:
- Chỉ cung cấp thông tin liên hệ và link chi tiết khi người dùng yêu cầu.
- Không có dữ liệu thì nói rõ là không có.

DỮ LIỆU WEBSITE:
{context}
"""
