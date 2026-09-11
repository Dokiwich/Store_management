class PromotionService:
    def __init__(self, promotion_dao):
        self.dao = promotion_dao

    def check_promotion(self, code, total_bill):
        return self.dao.check_promotion(code, total_bill)

    def get_active_promotions(self, limit=50, offset=0):
        return self.dao.get_active_promotions(limit, offset)
