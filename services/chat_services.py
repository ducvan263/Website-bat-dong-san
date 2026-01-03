from models.Conversation import Conversation
from models.Message import Message


class ChatService :
    @staticmethod
    def get_all_conversation():
        return (
            Conversation.query
            .order_by(Conversation.last_message_at.desc())
            .all()
        )

    @staticmethod
    def get_conversation_list():
        data = []

        conversations = ChatService.get_all_conversation()

        for c in conversations:
            last_msg = (
                Message.query
                .filter_by(conversation_id=c.id)
                .order_by(Message.created_at.desc())
                .first()
            )

            data.append({
                "id": c.id,
                "title": last_msg.message[:40] if last_msg else "Cuộc trò chuyện mới",
                "last_message_at": (
                    last_msg.created_at if last_msg else c.created_at
                )
            })

        return data


