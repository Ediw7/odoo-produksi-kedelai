from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProduksiOrder(models.Model):
    """
    Order / SPK (Surat Perintah Kerja) Produksi.
    Dibuat berdasarkan template produksi. Langkah-langkah proses dan bahan baku
    otomatis di-copy dari template yang dipilih.
    """
    _name = 'produksi.order'
    _description = 'Order Produksi'
    _order = 'tanggal_mulai desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nomor SPK',
        required=True,
        copy=False,
        readonly=True,
        default='Baru',
        tracking=True,
    )
    template_id = fields.Many2one(
        'produksi.template',
        string='Template Produksi',
        required=True,
        tracking=True,
        help='Pilih template/resep produksi. Langkah proses & bahan baku akan otomatis terisi.',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produk',
        related='template_id.product_id',
        store=True,
        readonly=True,
    )
    jumlah_target = fields.Float(
        string='Jumlah Target Produksi',
        default=1.0,
        required=True,
        tracking=True,
    )
    satuan_produksi = fields.Selection([
        ('liter', 'Liter'),
        ('botol', 'Botol'),
        ('pack', 'Pack'),
        ('kg', 'Kilogram'),
        ('pcs', 'Pcs'),
    ], string='Satuan', default='liter')

    # ---- Jadwal & Tim ----
    tanggal_mulai = fields.Date(
        string='Tanggal Mulai',
        default=fields.Date.context_today,
        tracking=True,
    )
    tanggal_selesai = fields.Date(string='Target Selesai', tracking=True)
    penanggung_jawab = fields.Many2one(
        'res.users',
        string='Penanggung Jawab',
        default=lambda self: self.env.user,
        tracking=True,
    )

    # ---- Relasi Langkah & Bahan ----
    step_ids = fields.One2many(
        'produksi.order.step',
        'order_id',
        string='Langkah Proses Produksi',
    )
    bahan_ids = fields.One2many(
        'produksi.order.bahan',
        'order_id',
        string='Bahan Baku',
    )

    catatan = fields.Text(string='Catatan Tambahan')
    asal_sales = fields.Char(string='Asal Sales Order', readonly=True)

    # ---- Status ----
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('in_progress', 'Dalam Proses'),
        ('qc', 'Quality Control'),
        ('done', 'Selesai'),
        ('cancel', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)

    # ---- Computed ----
    progress = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
    )

    @api.depends('step_ids.state')
    def _compute_progress(self):
        for order in self:
            total = len(order.step_ids)
            if total == 0:
                order.progress = 0.0
            else:
                done = len(order.step_ids.filtered(lambda s: s.state == 'done'))
                order.progress = (done / total) * 100


    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Saat template dipilih, auto-fill langkah proses dan bahan baku."""
        if self.template_id:
            
            step_vals = []
            for step in self.template_id.step_ids:
                step_vals.append((0, 0, {
                    'sequence': step.sequence,
                    'name': step.name,
                    'durasi_estimasi': step.durasi_estimasi,
                    'instruksi': step.instruksi,
                }))
            self.step_ids = step_vals

            bahan_vals = []
            for bahan in self.template_id.bahan_ids:
                bahan_vals.append((0, 0, {
                    'sequence': bahan.sequence,
                    'nama_bahan': bahan.nama_bahan,
                    'jumlah': bahan.jumlah,
                    'satuan': bahan.satuan,
                    'keterangan': bahan.keterangan,
                }))
            self.bahan_ids = bahan_vals


    def action_confirm(self):
        for rec in self:
            if not rec.step_ids:
                raise ValidationError('Tidak bisa konfirmasi! Langkah proses produksi masih kosong.')
            rec.state = 'confirmed'

    def action_start(self):
        for rec in self:
            rec.state = 'in_progress'
            
            first_step = rec.step_ids.sorted('sequence')[:1]
            if first_step and first_step.state == 'pending':
                first_step.state = 'in_progress'

    def action_qc(self):
        for rec in self:
            rec.state = 'qc'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

 
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Baru') == 'Baru':
                vals['name'] = self.env['ir.sequence'].next_by_code('produksi.order.seq') or 'Baru'
        return super().create(vals_list)


class ProduksiOrderStep(models.Model):
    """
    Langkah proses produksi di dalam Order.
    Dicopy dari template, bisa di-track status per langkah.
    """
    _name = 'produksi.order.step'
    _description = 'Langkah Proses Order Produksi'
    _order = 'sequence, id'

    order_id = fields.Many2one(
        'produksi.order',
        string='Order Produksi',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Urutan', default=10)
    name = fields.Char(string='Nama Proses', required=True)
    durasi_estimasi = fields.Float(string='Estimasi Durasi (Jam)', default=1.0)
    durasi_aktual = fields.Float(string='Durasi Aktual (Jam)')
    instruksi = fields.Text(string='Instruksi / SOP')
    catatan_operator = fields.Text(string='Catatan Operator')
    state = fields.Selection([
        ('pending', 'Menunggu'),
        ('in_progress', 'Sedang Dikerjakan'),
        ('done', 'Selesai'),
        ('skip', 'Dilewati'),
    ], string='Status', default='pending')

    def action_start_step(self):
        self.ensure_one()
        self.state = 'in_progress'

    def action_done_step(self):
        self.ensure_one()
        self.state = 'done'
        
        next_steps = self.order_id.step_ids.filtered(
            lambda s: s.sequence > self.sequence and s.state == 'pending'
        ).sorted('sequence')
        if next_steps:
            next_steps[0].state = 'in_progress'
        else:
     
            all_done = all(
                s.state in ('done', 'skip') for s in self.order_id.step_ids
            )
            if all_done:
                self.order_id.state = 'qc'

    def action_skip_step(self):
        self.ensure_one()
        self.state = 'skip'


class ProduksiOrderBahan(models.Model):
    """
    Bahan baku yang dibutuhkan per order produksi.
    """
    _name = 'produksi.order.bahan'
    _description = 'Bahan Baku Order Produksi'
    _order = 'sequence, id'

    order_id = fields.Many2one(
        'produksi.order',
        string='Order Produksi',
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
