from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """
        Override sale order confirm → otomatis buat order produksi
        berdasarkan template produksi yang terhubung ke produk.
        """
        res = super(SaleOrderInherit, self).action_confirm()

        for order in self:
            for line in order.order_line:
                # Cari template produksi untuk produk ini
                template = self.env['produksi.template'].search([
                    ('product_id', '=', line.product_id.id),
                    ('active', '=', True),
                ], limit=1)

                if template:
                    # Siapkan langkah proses dari template
                    step_vals = []
                    for step in template.step_ids:
                        step_vals.append((0, 0, {
                            'sequence': step.sequence,
                            'name': step.name,
                            'durasi_estimasi': step.durasi_estimasi,
                            'instruksi': step.instruksi,
                        }))

                    # Siapkan bahan baku dari template
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
                        'jumlah_target': line.product_uom_qty,
                        'asal_sales': f'{order.name} - {order.partner_id.name}',
                        'catatan': f'Otomatis dari Sales Order: {order.name}\n'
                                   f'Pelanggan: {order.partner_id.name}\n'
                                   f'Produk: {line.product_id.name}',
                        'step_ids': step_vals,
                        'bahan_ids': bahan_vals,
                    })

        return res