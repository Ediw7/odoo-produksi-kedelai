{
    'name': 'Produksi Custom Edi',
    'version': '2.0',
    'category': 'Manufacturing',
    'summary': 'Modul Manajemen Produksi dengan Template Proses Multi-Produk',
    'description': """
        Modul produksi custom yang mendukung:
        - Template/Resep proses produksi per produk
        - Beberapa produk dengan proses produksi berbeda-beda
        - Tracking langkah proses per order
        - Integrasi otomatis dari Sales Order
    """,
    'depends': ['sale', 'mail', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/template_view.xml',
        'views/mrp_view.xml',
        'views/sale_order_view.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}