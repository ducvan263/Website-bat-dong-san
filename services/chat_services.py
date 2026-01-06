from models.Conversation import Conversation
from models.Message import Message
from models import db
from services.rag_service import RAGService
from sqlalchemy import func, and_
import requests
import os

class ChatService:

    @staticmethod
    def get_conversation_list(user_id):
        """
        Lấy conversation + tiêu đề là message cuối của USER
        """

        # 🔹 subquery: message cuối của USER trong mỗi conversation
        user_last_msg_sub = (
            db.session.query(
                Message.conversation_id,
                func.max(Message.id).label("last_user_msg_id")
            )
            .join(Conversation, Conversation.id == Message.conversation_id)
            .filter(
                Conversation.created_by == user_id,
                Message.sender_id == user_id
            )
            .group_by(Message.conversation_id)
            .subquery()
        )

        # 🔹 query chính
        rows = (
            db.session.query(Conversation, Message)
            .outerjoin(
                user_last_msg_sub,
                Conversation.id == user_last_msg_sub.c.conversation_id
            )
            .outerjoin(
                Message,
                Message.id == user_last_msg_sub.c.last_user_msg_id
            )
            .filter(Conversation.created_by == user_id)
            .order_by(Conversation.last_message_at.desc())
            .all()
        )

        result = []

        for c, m in rows:
            title = m.message[:40] if m else "Cuộc trò chuyện mới"

            result.append({
                "id": c.id,
                "title": title,
                "last_message_at": c.last_message_at.isoformat()
            })

        return result

    @staticmethod
    def ask_ai(user_text, chat_history):
        """
        Gọi Groq API với context từ DB
        """
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        context = RAGService.build_context(user_text)
        system_prompt = RAGService.build_system_prompt(context)

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Lịch sử chat (tối đa 10 tin gần nhất)
        for msg in chat_history[-10:]:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": user_text
        })

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "temperature": 0.2
            },
            timeout=30
        )

        result = response.json()

        if "error" in result:
            return "Lỗi AI: " + result["error"]["message"]

        return result["choices"][0]["message"]["content"]
