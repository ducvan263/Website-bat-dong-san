from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from models.Conversation import Conversation
from models.Message import Message
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.property_routes import property_bp
from services.property_service import PropertyService
from services.chat_services import ChatService
from models import db
from models.Property import Property
from models.Province import Province
from models.PropertyType import PropertyType
import requests
import os


# =========================
# CONFIG
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "secret_key_chatbot"
    app.config.from_pyfile('config.py')


    # =========================
    # INIT DB
    # =========================
    db.init_app(app)

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)

    with app.app_context():
        db.create_all()

    # =========================
    # WEB ROUTES
    # =========================
    @app.route("/")
    def home():
        page = request.args.get('page', 1, type=int)

        pagination = PropertyService.get_properties_paginated(
            page=page,
            per_page=9
        )

        return render_template(
            'index.html',
            properties=pagination["items"],
            total_pages=pagination["total_pages"],
            current_page=pagination["current_page"]
        )

    @app.route('/blog-detail')
    def blog_detail_3():
        return render_template('blog-detail.html')

    @app.route('/property-detail')
    def property_detail():
        return render_template('properties-detail.html')

    @app.route('/properties')
    def properties():
        return render_template('properties.html')

    @app.route('/user')
    def account():
        return render_template('account/account_profile.html')

    @app.route('/chat-bot')
    def chat_bot():
        user_id = session.get("user_id")

        conversations = ChatService.get_conversation_list(user_id)

        active_conversation_id = None
        messages = []

        if conversations:
            # 🔥 lấy conversation mới nhất
            active_conversation_id = conversations[0]["id"]

            # set vào session
            session["conversation_id"] = active_conversation_id

            # load messages
            db_messages = (
                Message.query
                .filter_by(conversation_id=active_conversation_id)
                .order_by(Message.created_at)
                .all()
            )

            messages = [
                {
                    "sender_id": m.sender_id,
                    "message": m.message,
                    "created_at": m.created_at.isoformat()
                }
                for m in db_messages
            ]

        return render_template(
            'chatbot.html',
            conversations=conversations,
            messages=messages,
            active_conversation_id=active_conversation_id
        )

    # =========================
    # CHAT API
    # =========================
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        user_text = data.get("message", "").strip()

        if not user_text:
            return jsonify({"reply": "Bạn chưa nhập nội dung."})

        user_id = session.get("user_id")

        # =========================
        # GET / CREATE CONVERSATION
        # =========================
        conversation_id = session.get("conversation_id")

        if not conversation_id:
            conversation = Conversation(
                created_by=user_id,
                created_at=datetime.utcnow(),
                last_message_at=datetime.utcnow()
            )
            db.session.add(conversation)
            db.session.commit()

            session["conversation_id"] = conversation.id
        else:
            conversation = Conversation.query.get(conversation_id)

        # =========================
        # SAVE USER MESSAGE
        # =========================
        user_msg = Message(
            conversation_id=conversation.id,
            sender_id=user_id,
            message=user_text
        )
        db.session.add(user_msg)

        conversation.last_message_at = datetime.utcnow()
        db.session.commit()

        # =========================
        # LOAD HISTORY FROM DB
        # =========================
        messages = [
            {
                "role": "system",
                "content": "Bạn là trợ lý AI. Trả lời đúng câu hỏi, không chào lại nếu không cần."
            }
        ]

        db_messages = (
            Message.query
            .filter_by(conversation_id=conversation.id)
            .order_by(Message.created_at)
            .limit(20)
            .all()
        )

        for msg in db_messages:
            messages.append({
                "role": "assistant" if msg.sender_id == 0 else "user",
                "content": msg.message
            })

        # =========================
        # CALL GROQ API
        # =========================
        try:
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
                return jsonify({"reply": f"Lỗi AI: {result['error']['message']}"})

            ai_reply = result["choices"][0]["message"]["content"]

            # =========================
            # SAVE AI MESSAGE
            # =========================
            ai_msg = Message(
                conversation_id=conversation.id,
                sender_id=0,  # AI
                message=ai_reply
            )
            db.session.add(ai_msg)

            conversation.last_message_at = datetime.utcnow()
            db.session.commit()

            return jsonify({
                "reply": ai_reply,
                "conversation_id": conversation.id
            })

        except Exception as e:
            return jsonify({"reply": f"Lỗi server: {str(e)}"})

    # =========================
    # RESET CHAT
    # =========================
    @app.route("/reset-chat", methods=["POST"])
    def reset_chat():
        conversation_id = session.get("conversation_id")

        if not conversation_id:
            return jsonify({"status": "no_conversation"})

        conversation = Conversation.query.get(conversation_id)

        if conversation:
            db.session.delete(conversation)
            db.session.commit()

        session.pop("conversation_id", None)

        return jsonify({"status": "deleted"})

    @app.route("/api/conversation/<int:conversation_id>/messages")
    def get_messages(conversation_id):
        messages = (
            Message.query
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at)
            .all()
        )

        return jsonify({
            "data": [
                {
                    "sender_id": m.sender_id,
                    "message": m.message,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]
        })

    @app.route("/set-conversation/<int:conversation_id>", methods=["POST"])
    def set_conversation(conversation_id):
        session["conversation_id"] = conversation_id
        return jsonify({"status": "ok"})

    @app.route("/api/conversation/new", methods=["POST"])
    def new_conversation():
        user_id = session.get("user_id")

        conversation = Conversation(
            created_by=user_id,
            created_at=datetime.utcnow(),
            last_message_at=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.commit()

        # set conversation mới vào session
        session["conversation_id"] = conversation.id

        return jsonify({
            "id": conversation.id,
            "title": "Cuộc trò chuyện mới",
            "last_message_at": conversation.created_at.isoformat()
        })

    @app.route("/api/search")
    def api_search():
        query = Property.query

        keyword = request.args.get("keyword")
        khu_vuc = request.args.get("khu_vuc")
        loai_hinh = request.args.get("loai_hinh")
        print(khu_vuc)
        if keyword:
            query = query.filter(Property.title.ilike(f"%{keyword}%"))

        if khu_vuc:
            query = query.join(Province).filter(Province.name == khu_vuc)

        if loai_hinh:
            query = query.join(PropertyType).filter(PropertyType.name == loai_hinh)

        results = query.all()
        print(results)
        return jsonify({
            "data": [
                {
                    "id": p.id,
                    "title": p.title,
                    "thumbnail": p.thumbnail,
                    "status": p.status,
                    "price_vn": p.price_vn,
                    "province": p.province.name if p.province else ""
                }
                for p in results
            ]
        })


    return app
app = create_app()

if __name__ == "__main__":

    app.run(debug=True)


