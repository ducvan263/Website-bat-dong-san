from ai.price_predictor import PricePredictor

predictor = PricePredictor("ai/models/price_model.pkl")

class AIService:

    @staticmethod
    def predict_price(data):
        return predictor.predict(
            area=data["area"],
            price_per_m2=data["price_per_m2"],
            legal_status=data["legal_status"],
            land_type=data["land_type"]
        )
