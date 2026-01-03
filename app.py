from flask import Flask, render_template, request, jsonify, session

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
        conversations = ChatService.get_conversation_list()
        print(conversations)
        return render_template(
            'chatbot.html',
            conversations=conversations
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

        # init history
        if "chat_history" not in session:
            session["chat_history"] = [
                {
                    "role": "system",
                    "content": "Bạn là trợ lý AI. Trả lời đúng câu hỏi, không chào lại nếu không cần."
                }
            ]

        session["chat_history"].append({
            "role": "user",
            "content": user_text
        })

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": session["chat_history"],
                    "temperature": 0.2
                },
                timeout=30
            )

            result = response.json()

            if "error" in result:
                return jsonify({
                    "reply": f"Lỗi AI: {result['error']['message']}"
                })

            ai_reply = result["choices"][0]["message"]["content"]

            session["chat_history"].append({
                "role": "assistant",
                "content": ai_reply
            })

            # giới hạn lịch sử (tránh quá dài)
            session["chat_history"] = session["chat_history"][-20:]

            return jsonify({"reply": ai_reply})

        except Exception as e:
            return jsonify({"reply": f"Lỗi server: {str(e)}"})

    # =========================
    # RESET CHAT
    # =========================
    @app.route("/reset-chat", methods=["POST"])
    def reset_chat():
        session.pop("chat_history", None)
        return jsonify({"status": "ok"})

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

    @app.route("/get-all-conversation")
    def get_all_conversation():
        conversations = ChatService.get_all_conversation()

        data = []
        for c in conversations:
            last_msg = (
                Message.query
                .filter_by(conversation_id=c.id)
                .order_by(Message.created_at.desc())
                .first()
            )

            data.append({
                "conversation_id": c.id,
                "title": last_msg.message[:50] if last_msg else "Cuộc trò chuyện mới",
                "last_message_at": (
                    last_msg.created_at.isoformat()
                    if last_msg else c.created_at.isoformat()
                )
            })

        return jsonify({"data": data})
    return app
app = create_app()

if __name__ == "__main__":

    app.run(debug=True)
