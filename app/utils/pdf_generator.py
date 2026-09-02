import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from flask import current_app, url_for


def format_indo_date(date_obj):
    if not date_obj:
        return "-"
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    day = date_obj.strftime("%d")
    month = months[date_obj.month - 1]
    year = date_obj.strftime("%Y")
    return f"{day} {month} {year}"


def _make_qr_image(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def generate_surat_bebas_pustaka(pengajuan, nama_institusi, nama_perpustakaan):
    from app.models.sistem_setting import SistemSetting
    if pengajuan.tipe_pengajuan == 'fakultas':
        from app.models.fakultas_setting import FakultasSetting
        setting = FakultasSetting.get_for_fakultas(pengajuan.fakultas)
        nama_perpustakaan = setting.nama_perpustakaan
    else:
        setting = SistemSetting.get()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    static_img_path = os.path.abspath(os.path.join(current_app.root_path, 'static', 'img'))
    logo_unhas_path = os.path.join(static_img_path, 'logo_unhas.png')
    logo_iso_path = os.path.join(static_img_path, 'iso_9001-2015.png')

    # ─── HEADER ───────────────────────────────────────────
    if os.path.exists(logo_unhas_path):
        c.drawImage(logo_unhas_path, 1.5*cm, height - 3.5*cm,
                    width=2.2*cm, height=2.8*cm, mask='auto')

    c.setFont("Times-Bold", 11)
    c.drawString(4.2*cm, height - 1.75*cm, "KEMENTERIAN PENDIDIKAN TINGGI, SAINS,")
    c.drawString(4.2*cm, height - 2.2*cm,  "DAN TEKNOLOGI")
    c.setFont("Times-Bold", 13)
    c.drawString(4.2*cm, height - 2.75*cm, "UNIVERSITAS HASANUDDIN")
    c.drawString(4.2*cm, height - 3.25*cm, nama_perpustakaan.upper())

    c.setFont("Times-Roman", 7)
    c.drawRightString(width - 1.5*cm, height - 1.55*cm, "Jalan Perintis Kemerdekaan Km. 10")
    c.drawRightString(width - 1.5*cm, height - 1.9*cm,  "Tamalanrea, Makassar 90245")
    c.drawRightString(width - 1.5*cm, height - 2.25*cm, "Telepon (0411) 586200")
    c.drawRightString(width - 1.5*cm, height - 2.6*cm,  "Laman https://library.unhas.ac.id")
    c.drawRightString(width - 1.5*cm, height - 2.95*cm, "email : library@unhas.ac.id")

    c.setLineWidth(2)
    c.line(1.5*cm, height - 3.8*cm, width - 1.5*cm, height - 3.8*cm)

    # ─── JUDUL SURAT ──────────────────────────────────────
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 4.8*cm, "SURAT KETERANGAN BEBAS PUSTAKA")
    c.setFont("Helvetica", 11)
    nomor_surat = (
        pengajuan.nomor_surat or
        f"..../{setting.nomor_bagian_tengah}/{setting.nomor_tahun}"
    )
    c.drawCentredString(width / 2, height - 5.3*cm, f"Nomor: {nomor_surat}")

    # ─── ISI SURAT ────────────────────────────────────────
    margin_left = 1.5*cm
    margin_right = 1.5*cm
    text_width = width - margin_left - margin_right

    p_style = ParagraphStyle(
        'body', fontName='Helvetica', fontSize=11, leading=16, alignment=TA_JUSTIFY
    )

    y = height - 6.5*cm
    c.setFont("Helvetica", 11)
    c.drawString(margin_left, y, f"{nama_perpustakaan} dengan ini menerangkan bahwa :")

    y -= 0.9*cm
    rows = [
        ("Nama",         f": {pengajuan.nama}"),
        ("Nomor Pokok",  f": {pengajuan.nim}"),
        ("Program Studi",
         f": {pengajuan.program_studi.nama_prodi if pengajuan.program_studi else '-'}"),
        ("Jenjang",      ": S1"),
        ("Fakultas",
         f": {pengajuan.fakultas.nama_fakultas if pengajuan.fakultas else '-'}"),
        ("Alamat",       f": {pengajuan.alamat}"),
    ]
    for label, val in rows:
        c.setFont("Helvetica", 11)
        c.drawString(2.5*cm, y, label)
        c.drawString(5.5*cm, y, val)
        y -= 0.6*cm

    y -= 0.5*cm
    p1 = Paragraph(
        f"Mahasiswa tersebut diatas benar tidak mempunyai pinjaman bahan pustaka pada {nama_perpustakaan}, "
        "dan surat keterangan ini berlaku sampai dengan :",
        p_style,
    )
    p1_w, p1_h = p1.wrap(text_width, 5*cm)
    p1.drawOn(c, margin_left, y - p1_h)
    y -= p1_h + 0.6*cm

    # Tanggal berlaku (tebal, tengah)
    tgl_disetujui = pengajuan.approved_at or datetime.utcnow()
    tgl_berlaku = tgl_disetujui + timedelta(days=90)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, format_indo_date(tgl_berlaku))
    y -= 1.0*cm

    # Paragraf penutup
    p2 = Paragraph(
        "Demikian keterangan ini kami berikan kepada yang bersangkutan untuk digunakan "
        "sebagaimana mestinya.",
        p_style,
    )
    p2_w, p2_h = p2.wrap(text_width, 5*cm)
    p2.drawOn(c, margin_left, y - p2_h)
    y -= p2_h + 0.3*cm

    # ─── TANDA TANGAN ─────────────────────────────────────
    tgl_cetak = pengajuan.approved_at or datetime.utcnow()
    y_sign = y - 1.2*cm
    c.setFont("Helvetica", 11)
    c.drawRightString(width - margin_right, y_sign, f"Makassar, {format_indo_date(tgl_cetak)}")
    y_sign -= 0.7*cm
    c.drawRightString(width - margin_right, y_sign, "Kepala,")
    y_sign -= 0.5*cm
    # Tulis baris-baris jabatan dari setting
    for baris in setting.pejabat_jabatan.splitlines():
        c.drawRightString(width - margin_right, y_sign, baris.strip())
        y_sign -= 0.5*cm
    y_sign -= 0.1*cm

    # QR Code verifikasi
    qr_size = 2.5*cm
    public_base_url = current_app.config.get('PUBLIC_BASE_URL')
    if public_base_url:
        qr_data = f"{public_base_url}/verifikasi/{pengajuan.id}"
    else:
        qr_data = url_for('main.verifikasi_surat', id=pengajuan.id, _external=True)
    try:
        qr_buf = _make_qr_image(qr_data)
        qr_x = width - margin_right - qr_size
        qr_y = y_sign - qr_size
        c.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)
        y_sign = qr_y - 0.4*cm
    except Exception:
        y_sign -= qr_size + 0.4*cm

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - margin_right, y_sign, setting.pejabat_nama)
    y_sign -= 0.5*cm
    c.setFont("Helvetica", 11)
    c.drawRightString(width - margin_right, y_sign, f"NIP. {setting.pejabat_nip}")

    # ─── TEMBUSAN ─────────────────────────────────────────
    y_tem = 3.5*cm
    c.setFont("Helvetica", 9)
    c.drawString(margin_left, y_tem, "Tembusan yth:")
    c.drawString(margin_left, y_tem - 0.45*cm, "1. Kepala Perpustakaan Unhas")
    c.drawString(margin_left, y_tem - 0.9*cm,  "2. Arsip.")

    # ─── LOGO ISO (Kanan Bawah) ───────────────────────────
    if os.path.exists(logo_iso_path):
        c.drawImage(logo_iso_path, width - 3.5*cm, -10.0*cm,
                    width=2.5*cm, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
