from odoo import models, fields, api
from ..forecast.predictor import predict_inventory

class ProductProduct(models.Model):
    _inherit = 'product.product'

    predicted_qty_next_week = fields.Float(string="Tồn kho tuần tới (dự đoán)", readonly=True)

    @api.model
    def update_inventory_forecast(self):
        for product in self.search([]):
            try:
                product.predicted_qty_next_week = predict_inventory(product.id, self.env)
            except Exception as e:
                _logger.warning(f"Lỗi khi dự đoán tồn kho sản phẩm {product.name}: {e}")
