from odoo import models, fields, api
import requests
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockAnnForecast(models.Model):
    _name = 'stock.ann.forecast'
    _description = 'Dự báo tồn kho bằng ANN'
    _order = 'prediction_date asc'

    product_id = fields.Many2one('product.product', required=True, string="Sản phẩm")
    prediction_date = fields.Date(required=True, string="Ngày dự báo")
    predicted_qty = fields.Float(string="Số lượng dự báo", required=True)

    @api.model
    def run_ann_forecast(self):
        products = self.env['product.product'].search([])
        for product in products:
            try:
                response = requests.post(
                    'http://localhost:8000/forecast',
                    json={"product_id": product.id}
                )
                if response.ok:
                    forecast_data = response.json()
                    for item in forecast_data:
                        prediction_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
                        predicted_qty = float(item['qty'])
                        self.create({
                            'product_id': product.id,
                            'prediction_date': prediction_date,
                            'predicted_qty': predicted_qty,
                        })
            except Exception as e:
                _logger.error("Lỗi khi dự báo tồn kho cho sản phẩm %s: %s", product.id, str(e))
