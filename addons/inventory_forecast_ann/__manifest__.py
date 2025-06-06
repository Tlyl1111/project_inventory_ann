{
    'name': 'Inventory Forecast ANN',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Dự đoán tồn kho tuần tới bằng mạng nơ-ron nhân tạo (ANN)',
    'depends': ['stock', 'product'],
    'data': [
        'views/product_view.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
}
