from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def _fmt_date(value):
    if not value:
        return "N/A"
    try:
        return value.strftime("%Y-%m-%d")
    except Exception:
        return str(value)[:10]


def generate_invoice_pdf(invoice, user, plan) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
    )
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
    )

    amount = getattr(invoice, "total_amount", None)
    if amount is None:
        amount = getattr(invoice, "amount", 0.0) or 0.0

    invoice_status = (getattr(invoice, "status", "") or "N/A").upper()
    user_email = getattr(user, "email", None) or f"User #{getattr(user, 'id', 'N/A')}"
    plan_name = getattr(plan, "name", None) or "Plan"

    story.append(Paragraph("<b>INVOICE</b>", title_style))
    story.append(Spacer(1, 12))

    meta_data = [
        [
            Paragraph(f"<b>Invoice ID:</b> #{invoice.id}", styles['Normal']),
            Paragraph(f"<b>Status:</b> {invoice_status}", styles['Normal']),
        ],
        [
            Paragraph(f"<b>Billed To:</b> {user_email}", styles['Normal']),
            Paragraph(
                f"<b>Created Date:</b> {_fmt_date(getattr(invoice, 'created_at', None))}",
                styles['Normal'],
            ),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    period_str = (
        f"{_fmt_date(getattr(invoice, 'billing_period_start', None))} to "
        f"{_fmt_date(getattr(invoice, 'billing_period_end', None))}"
    )

    table_data = [
        [
            Paragraph("<b>Description</b>", bold_style),
            Paragraph("<b>Billing Period</b>", bold_style),
            Paragraph("<b>Amount</b>", bold_style),
        ],
        [
            Paragraph(f"Subscription - {plan_name}", styles['Normal']),
            Paragraph(period_str, styles['Normal']),
            Paragraph(f"${amount:.2f}", styles['Normal']),
        ],
        [
            Paragraph("<b>Total Due</b>", bold_style),
            Paragraph("", styles['Normal']),
            Paragraph(f"<b>${amount:.2f}</b>", bold_style),
        ],
    ]

    item_table = Table(table_data, colWidths=[240, 200, 100])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ]))
    story.append(item_table)

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes