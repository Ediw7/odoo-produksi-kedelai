from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    produksi_order_ids = fields.One2many(
        'produksi.order',
        'sale_order_id',
        string='Order Produksi',
    )

    def action_confirm(self):

        res = super(SaleOrderInherit, self).action_confirm()

        for order in self:
            for line in order.order_line:

                template = self.env['produksi.template'].search([
                    ('product_id', '=', line.product_id.id),
                    ('active', '=', True),
                ], limit=1)

                if template:

                    step_vals = []
                    for step in template.step_ids:
                        step_vals.append((0, 0, {
                            'sequence': step.sequence,
                            'name': step.name,
                            'durasi_estimasi': step.durasi_estimasi,
                            'instruksi': step.instruksi,
                        }))

                    bahan_vals = []
                    for bahan in template.bahan_ids:
                        bahan_vals.append((0, 0, {
                            'sequence': bahan.sequence,
                            'nama_bahan': bahan.nama_bahan,
                            'jumlah': bahan.jumlah,
                            'satuan': bahan.satuan,
                            'keterangan': bahan.keterangan,
                        }))

                    self.env['produksi.order'].create({
                        'template_id': template.id,
                        'sale_order_id': order.id,
                        'jumlah_target': line.product_uom_qty,
                        'asal_sales': f'{order.name} - {order.partner_id.name}',
                        'catatan': f'Otomatis dari Sales Order: {order.name}\n'
                                   f'Pelanggan: {order.partner_id.name}\n'
                                   f'Produk: {line.product_id.name}',
                        'step_ids': step_vals,
                        'bahan_ids': bahan_vals,
                    })

        return res