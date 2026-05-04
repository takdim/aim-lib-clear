import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_surat_bebas_pustaka(pengajuan, nama_institusi, nama_perpustakaan):
    """
    Generate PDF surat bebas pustaka secara on-demand dari data database.
    Returns bytes dari PDF yang dihasilkan.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    styles = getSampleStyleSheet()

    # ─── KOP SURAT ───────────────────────────────────────────────
    style_kop_institusi = ParagraphStyle(
        'KopInstitusi',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=18,
    )
    style_kop_sub = ParagraphStyle(
        'KopSub',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=14,
    )
    style_kop_alamat = ParagraphStyle(
        'KopAlamat',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=12,
    )

    story.append(Paragraph(nama_institusi.upper(), style_kop_institusi))
    story.append(Paragraph(nama_perpustakaan.upper(), style_kop_sub))
    story.append(Paragraph(
        'Jl. Contoh No. 1, Kota Contoh | Telp. (021) 000-0000 | perpustakaan@institusi.ac.id',
        style_kop_alamat
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.black))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.black, spaceAfter=12))

    # ─── JUDUL ───────────────────────────────────────────────────
    style_judul = ParagraphStyle(
        'Judul',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_nomor = ParagraphStyle(
        'Nomor',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    story.append(Paragraph('SURAT KETERANGAN BEBAS PUSTAKA', style_judul))
    story.append(Paragraph(f'Nomor: {pengajuan.nomor_surat}', style_nomor))

    # ─── PEMBUKA ─────────────────────────────────────────────────
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leading=16,
        alignment=TA_JUSTIFY,
    )

    tanggal_terbit = pengajuan.approved_at.strftime('%d %B %Y') if pengajuan.approved_at else datetime.utcnow().strftime('%d %B %Y')

    story.append(Paragraph(
        f'Yang bertanda tangan di bawah ini, Kepala {nama_perpustakaan}, '
        f'menerangkan bahwa mahasiswa berikut:',
        style_body
    ))
    story.append(Spacer(1, 12))

    # ─── DATA MAHASISWA ───────────────────────────────────────────
    data = [
        ['NIM', ':', pengajuan.nim],
        ['Nama', ':', pengajuan.nama],
        ['Fakultas', ':', pengajuan.fakultas.nama_fakultas if pengajuan.fakultas else '-'],
        ['Program Studi', ':', pengajuan.program_studi.nama_prodi if pengajuan.program_studi else '-'],
        ['Alamat', ':', pengajuan.alamat],
    ]

    table = Table(data, colWidths=[3.5 * cm, 0.5 * cm, 11 * cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # ─── ISI SURAT ───────────────────────────────────────────────
    story.append(Paragraph(
        f'<b>DINYATAKAN BEBAS PUSTAKA</b> dari {nama_perpustakaan}. '
        f'Mahasiswa tersebut di atas tidak mempunyai tanggungan buku/koleksi '
        f'yang dipinjam maupun denda keterlambatan.',
        style_body
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Surat keterangan ini diterbitkan untuk digunakan sebagai syarat '
        'pengajuan yudisium / kelulusan.',
        style_body
    ))
    story.append(Spacer(1, 24))

    # ─── TANDA TANGAN ────────────────────────────────────────────
    style_ttd = ParagraphStyle(
        'TTD',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
    )

    # Ambil kota dari config atau default
    kota = 'Kota Contoh'
    story.append(Paragraph(
        f'{kota}, {tanggal_terbit}',
        style_ttd
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'Kepala {nama_perpustakaan}', style_ttd))
    story.append(Spacer(1, 60))
    story.append(Paragraph('(_________________________)', style_ttd))
    story.append(Paragraph('NIP. ..............................', style_ttd))

    # ─── FOOTER ──────────────────────────────────────────────────
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=4,
    )
    story.append(Paragraph(
        f'Dokumen ini digenerate secara digital oleh sistem pada {datetime.utcnow().strftime("%d-%m-%Y %H:%M")} WIB. '
        'Keabsahan dokumen dapat diverifikasi melalui sistem.',
        style_footer
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
