class ReportService:
    def __init__(self, report_dao):
        self.dao = report_dao

    def get_summary_stats(self):
        return self.dao.get_summary_stats()

    def get_top_selling_products(self, limit=10, offset=0):
        return self.dao.get_top_selling_products(limit, offset)

    def get_available_years(self):
        return self.dao.get_available_years()

    def get_revenue_by_year(self, year):
        return self.dao.get_revenue_by_year(year)

    def get_category_share(self):
        return self.dao.get_category_share()
