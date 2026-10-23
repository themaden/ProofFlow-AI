from .models import CaseInput, Evidence


def verify(data: CaseInput) -> list[Evidence]:
    invoice, po = data.invoice, data.purchase_order
    checks = (
        ("purchase_order_match", invoice.po_id == po.po_id, invoice.po_id, po.po_id),
        ("supplier_match", invoice.supplier_id == po.supplier_id, invoice.supplier_id, po.supplier_id),
        ("currency_match", invoice.currency == po.currency, invoice.currency, po.currency),
        ("amount_match", invoice.amount == po.amount, str(invoice.amount), str(po.amount)),
    )
    return [Evidence(rule=name, passed=passed, observed=observed, expected=expected)
            for name, passed, observed, expected in checks]
