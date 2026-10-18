from unittest.mock import patch
import pytest
from app import create_app, db
from app.models.user import User
from app.models.bebas_pustaka import BebasPustaka


@pytest.fixture
def app_instance():
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'INLISLITE_ENABLED': True,
        'INLISLITE_BASE_URL': 'https://inlislite.example.com',
        'INLISLITE_LOGIN_URL': 'https://inlislite.example.com/backend/site/login',
        'INLISLITE_USERNAME': 'admin',
        'INLISLITE_PASSWORD': 'secret',
    })
    return app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_pengajuan_detail_does_not_fetch_inlislite_by_default(client, app_instance):
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='staff', fakultas_id=None).first()
            if not user:
                user = db.session.query(User).filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

            pengajuan = db.session.query(BebasPustaka).filter_by(tipe_pengajuan='pusat').first()
            pengajuan_id = pengajuan.id

    with patch('app.routes.staff._fetch_inlislite_data') as mock_fetch:
        resp = client.get(f'/staff/pengajuan/{pengajuan_id}')
        assert resp.status_code == 200
        # Harus TIDAK memanggil _fetch_inlislite_data secara otomatis
        mock_fetch.assert_not_called()
        html = resp.get_data(as_text=True)
        assert 'INLISLite UNHAS' in html
        assert 'Cek Peminjaman di INLISLite' in html
        assert 'Data peminjaman belum dicek' in html


def test_pengajuan_detail_fetches_inlislite_when_param_set(client, app_instance):
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='staff', fakultas_id=None).first()
            if not user:
                user = db.session.query(User).filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

            pengajuan = db.session.query(BebasPustaka).filter_by(tipe_pengajuan='pusat').first()
            pengajuan_id = pengajuan.id
            pengajuan_nim = pengajuan.nim

    mock_result = {
        'login_success': True,
        'message': 'Login INLISLite berhasil.',
        'member': {
            'member_id': '12345',
            'member_no': pengajuan_nim,
            'full_name': 'Test Mahasiswa',
            'fakultas': 'Fakultas Teknik',
            'jurusan': 'Informatika',
        },
        'loan_history': [],
        'loan_columns': [],
    }

    with patch('app.routes.staff._fetch_inlislite_data', return_value=mock_result) as mock_fetch:
        resp = client.get(f'/staff/pengajuan/{pengajuan_id}?cek_inlislite=1')
        assert resp.status_code == 200
        mock_fetch.assert_called_once_with(pengajuan_nim, force_refresh=False)
        html = resp.get_data(as_text=True)
        assert 'Test Mahasiswa' in html
        assert '12345' in html


def test_pengajuan_cek_inlislite_ajax_endpoint(client, app_instance):
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='staff', fakultas_id=None).first()
            if not user:
                user = db.session.query(User).filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

            pengajuan = db.session.query(BebasPustaka).filter_by(tipe_pengajuan='pusat').first()
            pengajuan_id = pengajuan.id
            pengajuan_nim = pengajuan.nim

    mock_result = {
        'login_success': True,
        'message': 'Berhasil ambil data.',
        'member': {
            'member_id': '999',
            'member_no': pengajuan_nim,
            'full_name': 'Test Mahasiswa',
            'fakultas': 'Teknik',
            'jurusan': 'Informatika',
        },
        'loan_history': [
            {'Judul': 'Pemrograman Python', 'Tgl Pinjam': '2026-01-01', 'Status': 'Kembali'}
        ],
        'loan_columns': ['Judul', 'Tgl Pinjam', 'Status'],
    }

    with patch('app.routes.staff._fetch_inlislite_data', return_value=mock_result) as mock_fetch:
        resp = client.get(f'/staff/pengajuan/{pengajuan_id}/cek-inlislite')
        assert resp.status_code == 200
        mock_fetch.assert_called_once_with(pengajuan_nim, force_refresh=False)
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['member']['member_id'] == '999'
        assert len(data['data']['loan_history']) == 1


def test_inlislite_disabled_hides_card_and_blocks_endpoint(client, app_instance):
    app_instance.config['INLISLITE_ENABLED'] = False
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='staff', fakultas_id=None).first()
            if not user:
                user = db.session.query(User).filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

            pengajuan = db.session.query(BebasPustaka).filter_by(tipe_pengajuan='pusat').first()
            pengajuan_id = pengajuan.id

    # Halaman detail tidak menampilkan kartu INLISLite
    resp = client.get(f'/staff/pengajuan/{pengajuan_id}')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'INLISLite UNHAS' not in html

    # Endpoint AJAX mengembalikan status 400 dan pesan bahwa fitur dinonaktifkan
    resp_ajax = client.get(f'/staff/pengajuan/{pengajuan_id}/cek-inlislite')
    assert resp_ajax.status_code == 400
    data = resp_ajax.get_json()
    assert data['success'] is False
    assert 'dinonaktifkan' in data['message']
