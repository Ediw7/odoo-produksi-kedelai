from odoo import models, fields, api


class ProduksiTemplate(models.Model):
  
    _name = 'produksi.template'
    _description = 'Template Proses Produksi'
    _order = 'name'

    name = fields.Char(
        string='Nama Template',
        required=True,
        help='Misal: Resep Susu Kedelai Original, Resep Susu Kedelai Cokelat'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produk',
        required=True,
        help='Produk yang dihasilkan dari template ini'
    )
    deskripsi = fields.Text(
        string='Deskripsi',
        help='Penjelasan singkat tentang proses produksi ini'
    )
    step_ids = fields.One2many(
        'produksi.template.step',
        'template_id',
        string='Langkah-Langkah Proses',
        copy=True,
    )
    bahan_ids = fields.One2many(
        'produksi.template.bahan',
        'template_id',
        string='Daftar Bahan Baku',
        copy=True,
    )
    active = fields.Boolean(default=True)

    jumlah_langkah = fields.Integer(
        string='Jumlah Langkah',
        compute='_compute_jumlah_langkah',
        store=True,
    )

    @api.depends('step_ids')
    def _compute_jumlah_langkah(self):
        for rec in self:
            rec.jumlah_langkah = len(rec.step_ids)


class ProduksiTemplateStep(models.Model):
  
    _name = 'produksi.template.step'
    _description = 'Langkah Proses Template'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'produksi.template',
        string='Template',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Urutan', default=10)
    name = fields.Char(
        string='Nama Proses',
        required=True,
        help='Misal: Perendaman, Penggilingan, Perebusan, dll.'
    )
    durasi_estimasi = fields.Float(
        string='Estimasi Durasi (Jam)',
        default=1.0,
        help='Perkiraan waktu yang dibutuhkan untuk proses ini'
    )
    instruksi = fields.Text(
        string='Instruksi / SOP',
        help='Detail instruksi atau SOP untuk langkah ini'
    )


class ProduksiTemplateBahan(models.Model):
  
    _name = 'produksi.template.bahan'
    _description = 'Bahan Baku Template'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'produksi.template',
        string='Template',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Urutan', default=10)
    nama_bahan = fields.Char(string='Nama Bahan', required=True)
    jumlah = fields.Float(string='Jumlah Kebutuhan', default=1.0)
    satuan = fields.Selection([
        ('kg', 'Kilogram'),
        ('gram', 'Gram'),
        ('liter', 'Liter'),
        ('ml', 'Mililiter'),
        ('pcs', 'Pcs'),
        ('pack', 'Pack'),
    ], string='Satuan', default='kg')
    keterangan = fields.Char(string='Keterangan')
