from services.embedding_service import EmbeddingService
from services.property_service import PropertyService

class RAGService:

    @staticmethod
    def build_context(user_text):
        property_ids = EmbeddingService.search(user_text)

        properties = [
            PropertyService.get_property_by_id(pid)
            for pid in property_ids
            if PropertyService.get_property_by_id(pid)
        ]

        if not properties:
            return "KHÔNG CÓ DỮ LIỆU PHÙ HỢP."

        return "\n".join(
            PropertyService.property_to_text(p) for p in properties
        )

    @staticmethod
    def build_system_prompt(context):
        return f"""
        Bạn là chatbot bất động sản của website wealthuring.
        CHỈ trả lời dựa trên dữ liệu được cung cấp.
        KHÔNG suy đoán, KHÔNG bịa.
        
        Nếu không có dữ liệu phù hợp, hãy trả lời:
        "Hiện tôi chưa có dữ liệu phù hợp."
        
        DỮ LIỆU WEBSITE:
        {context}
        """
