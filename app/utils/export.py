# ABOUTME: Export utilities for generating CSV and PDF reports
# ABOUTME: CSV via stdlib csv module, PDF via reportlab with table formatting

import csv
import io
from datetime import date

from flask import make_response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def export_csv(filename, headers, rows):
    """Generate a CSV file response.

    Args:
        filename: Download filename (without extension)
        headers: List of column header strings
        rows: List of lists, each inner list is a row of values
    Returns:
        Flask Response with CSV content
    """
    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel compatibility
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


def export_pdf(filename, title, headers, rows):
    """Generate a PDF file response with a formatted table.

    Args:
        filename: Download filename (without extension)
        title: Report title shown at top of PDF
        headers: List of column header strings
        rows: List of lists, each inner list is a row of values
    Returns:
        Flask Response with PDF content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(
        f'Generated: {date.today().strftime("%d/%m/%Y")}',
        styles['Normal']
    ))
    elements.append(Spacer(1, 10 * mm))

    # Build table data
    table_data = [headers] + rows

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response
