from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from sqlalchemy.sql.functions import current_user

from models.Conversation import Conversation
from models.Message import Message
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.property_routes import property_bp
from services.embedding_service import EmbeddingService
from services.property_service import PropertyService
from services.chat_services import ChatService
from services.review_service import ReviewService
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
        EmbeddingService.build_index()


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

    @app.route('/property/<int:property_id>')
    def property_detail(property_id):
        property = PropertyService.get_property_by_id(property_id)

        images = property.images if property else []
        return render_template(
            'properties-detail.html',
            property=property,
            images=images
        )

    @app.route('/properties')
    def properties():
        return render_template('properties.html')

    @app.route('/user')
    def account():
        return render_template('account/account_profile.html')

    @app.route('/house_price_prediction')
    def house_price_prediction():
        reviews = ReviewService.get_latest_reviews()
        summary = ReviewService.get_rating_summary()

        return render_template(
            "house-price-prediction.html",
            reviews=reviews,
            avg_rating=summary["avg_rating"],
            review_count=summary["review_count"]
        )


    @app.route("/reviews", methods=["POST"])
    def create_review():
        data = request.json
        id = session.get('user_id')
        rating = int(data.get("rating"))
        comment = data.get("comment")

        ReviewService.create_review(
            user_id=id,
            rating=rating,
            comment=comment
        )

        return jsonify({
            "success": True,
            "message": "Đã gửi đánh giá thành công"
        })
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
        db.session.commit()

        # =========================
        # LOAD CHAT HISTORY
        # =========================
        db_messages = (
            Message.query
            .filter_by(conversation_id=conversation.id)
            .order_by(Message.created_at)
            .limit(20)
            .all()
        )

        chat_history = []
        for msg in db_messages:
            chat_history.append({
                "role": "assistant" if msg.sender_id == 0 else "user",
                "content": msg.message
            })

        # =========================
        # ASK AI (RAG)
        # =========================
        ai_reply = ChatService.ask_ai(user_text, chat_history)

        # =========================
        # SAVE AI MESSAGE
        # =========================
        ai_msg = Message(
            conversation_id=conversation.id,
            sender_id=0,
            message=ai_reply
        )
        db.session.add(ai_msg)

        conversation.last_message_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "reply": ai_reply,
            "conversation_id": conversation.id
        })
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
                    "thumbnail": f"static/{p.thumbnail}",
                    "status": p.status,
                    "price_vn": p.price_vn,
                    "address": p.address,
                }
                for p in results
            ]
        })

    @app.route('/test')
    def test():
        texts = []
        property_ids = []
        properties = PropertyService.get_all_property()
        for p in properties:
            texts.append(PropertyService.property_to_text(p))
            property_ids.append(p.id)

        print(texts)
        return texts


    return app
app = create_app()

if __name__ == "__main__":

    app.run(debug=True)
