import re
import json
import urllib.parse
import urllib.request
from html import unescape
from dataclasses import dataclass
from http.cookiejar import CookieJar


@dataclass
class InlisliteLoginResult:
    success: bool
    final_url: str
    status_code: int
    message: str


class InlisliteClient:
    """Headless INLISLite client that works without browser automation."""

    def __init__(self, base_url: str, login_url: str, username: str, password: str, timeout: int = 20):
        self.base_url = (base_url or '').rstrip('/')
        self.login_url = (login_url or '').strip()
        self.username = (username or '').strip()
        self.password = (password or '').strip()
        self.timeout = timeout

        self._cookie_jar = CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookie_jar))
        self._headers = {
            'User-Agent': (
                'Mozilla/5.0 (X11; Linux x86_64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/126.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
        }

    @classmethod
    def from_app_config(cls, app_config):
        return cls(
            base_url=app_config.get('INLISLITE_BASE_URL', ''),
            login_url=app_config.get('INLISLITE_LOGIN_URL', ''),
            username=app_config.get('INLISLITE_USERNAME', ''),
            password=app_config.get('INLISLITE_PASSWORD', ''),
            timeout=int(app_config.get('INLISLITE_TIMEOUT', 20)),
        )

    def can_login(self) -> bool:
        return all([self.login_url, self.username, self.password])

    def login(self) -> InlisliteLoginResult:
        if not self.can_login():
            return InlisliteLoginResult(
                success=False,
                final_url='',
                status_code=0,
                message='Konfigurasi INLISLite belum lengkap.',
            )

        try:
            login_html, _ = self._get(self.login_url)
            token = self._extract_backend_token(login_html)
            if not token:
                return InlisliteLoginResult(
                    success=False,
                    final_url=self.login_url,
                    status_code=0,
                    message='Token login INLISLite tidak ditemukan.',
                )

            post_data = urllib.parse.urlencode(
                {
                    '_backendInlislite': token,
                    'LoginForm[username]': self.username,
                    'LoginForm[password]': self.password,
                    'login-button': '',
                }
            ).encode('utf-8')

            post_headers = dict(self._headers)
            post_headers.update(
                {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': self.base_url or 'https://opac-library.unhas.ac.id',
                    'Referer': self.login_url,
                }
            )

            final_html, response = self._post(self.login_url, post_data, post_headers)
            final_url = response.geturl()
            status_code = getattr(response, 'status', 0)

            success = self._is_logged_in(final_url, final_html)
            message = 'Login INLISLite berhasil.' if success else 'Login INLISLite gagal.'

            return InlisliteLoginResult(
                success=success,
                final_url=final_url,
                status_code=status_code,
                message=message,
            )
        except Exception as exc:
            return InlisliteLoginResult(
                success=False,
                final_url=self.login_url,
                status_code=0,
                message=f'Gagal mengakses INLISLite: {exc}',
            )

    def fetch(self, url: str) -> str:
        html, _ = self._get(url)
        return html

    def search_member_by_nim(self, nim: str) -> list[dict]:
        """Cari data member berdasarkan NIM/MemberNo dari halaman backend member."""
        if not nim:
            return []

        rules = {
            'condition': 'AND',
            'rules': [
                {
                    'id': 'MemberNo',
                    'field': 'MemberNo',
                    'type': 'string',
                    'input': 'text',
                    'operator': 'contains',
                    'value': nim,
                }
            ],
        }
        rules_param = urllib.parse.quote(json.dumps(rules, separators=(',', ':')), safe='')
        member_search_url = f'{self.base_url}/backend/member/member/index?rules={rules_param}'
        html = self.fetch(member_search_url)

        table_html = self._extract_first_table_containing(html, 'No. Anggota')
        if not table_html:
            return []

        rows = self._extract_table_rows(table_html)
        if not rows:
            return []

        normalized_nim = nim.strip().lower()
        results: list[dict] = []
        for row in rows:
            member_no = self._pick_value(
                row,
                ['No. Anggota *', 'No. Anggota', 'MemberNo'],
            )
            if not member_no:
                continue
            if normalized_nim not in member_no.lower():
                continue

            update_href = self._extract_member_update_href(row.get('_raw_html', ''))
            member_id = self._extract_member_id(update_href) or row.get('_data_key')

            results.append(
                {
                    'member_id': member_id,
                    'member_no': member_no,
                    'full_name': self._pick_value(row, ['Nama Lengkap *', 'Nama Lengkap']),
                    'fakultas': self._pick_value(row, ['Fakultas']),
                    'jurusan': self._pick_value(row, ['Jurusan']),
                    'jenis_anggota': self._pick_value(row, ['Jenis Anggota']),
                    'status': self._pick_value(row, ['Status']),
                    'update_url': self._abs_url(update_href),
                    'raw': row,
                }
            )

        return results

    def get_member_loan_history(self, member_id: str | int) -> list[dict]:
        """Ambil tabel riwayat peminjaman dari halaman update member."""
        if not member_id:
            return []

        member_url = f'{self.base_url}/backend/member/member/update?id={member_id}'
        html = self.fetch(member_url)
        block_match = re.search(
            r'<div class="collectionloans-index">(.*?)</table>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not block_match:
            return []

        table_fragment = block_match.group(1)
        headers = self._extract_headers(table_fragment)
        rows = self._extract_table_rows(table_fragment)

        if not rows:
            return []

        # INLISLite menampilkan 1 baris placeholder saat tidak ada riwayat.
        if len(rows) == 1 and any('Tidak ada data' in str(v) for v in rows[0].values()):
            return []

        history = []
        for row in rows:
            cleaned = {}
            for h in headers:
                cleaned[h] = row.get(h, '')
            if any((v or '').strip() for v in cleaned.values()):
                history.append(cleaned)
        return history

    def _get(self, url: str):
        request = urllib.request.Request(url, headers=self._headers)
        with self._opener.open(request, timeout=self.timeout) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return html, response

    def _post(self, url: str, data: bytes, headers: dict):
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with self._opener.open(request, timeout=self.timeout) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return html, response

    @staticmethod
    def _extract_backend_token(html: str) -> str:
        match = re.search(r'name="_backendInlislite"\s+value="([^"]+)"', html)
        return match.group(1) if match else ''

    @staticmethod
    def _clean_text(html_fragment: str) -> str:
        text = re.sub(r'<[^>]+>', '', html_fragment or '')
        text = unescape(text)
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_first_table_containing(self, html: str, marker_text: str) -> str:
        tables = re.findall(r'<table[^>]*>.*?</table>', html, flags=re.IGNORECASE | re.DOTALL)
        marker_lower = marker_text.lower()
        for table in tables:
            if marker_lower in table.lower():
                return table
        return ''

    def _extract_headers(self, table_html: str) -> list[str]:
        headers = re.findall(r'<th[^>]*>(.*?)</th>', table_html, flags=re.IGNORECASE | re.DOTALL)
        return [self._clean_text(h) for h in headers]

    def _extract_table_rows(self, table_html: str) -> list[dict]:
        headers = self._extract_headers(table_html)
        rows = re.findall(r'<tr([^>]*)>(.*?)</tr>', table_html, flags=re.IGNORECASE | re.DOTALL)

        parsed_rows: list[dict] = []
        for tr_attrs, row_html in rows:
            if '<th' in row_html.lower():
                continue

            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, flags=re.IGNORECASE | re.DOTALL)
            if not tds:
                continue

            values = [self._clean_text(td) for td in tds]

            row_data = {}
            for i, value in enumerate(values):
                header = headers[i] if i < len(headers) and headers[i] else f'col_{i}'
                row_data[header] = value

            data_key_match = re.search(r'data-key="([^"]+)"', tr_attrs, flags=re.IGNORECASE)
            row_data['_data_key'] = data_key_match.group(1) if data_key_match else ''
            row_data['_raw_html'] = row_html
            parsed_rows.append(row_data)

        return parsed_rows

    @staticmethod
    def _pick_value(row: dict, candidates: list[str]) -> str:
        for key in candidates:
            value = row.get(key)
            if value:
                return value
        return ''

    @staticmethod
    def _extract_member_update_href(row_html: str) -> str:
        match = re.search(r'href="([^"]*/backend/member/member/update\?id=\d+[^"]*)"', row_html)
        if not match:
            return ''
        return unescape(match.group(1))

    @staticmethod
    def _extract_member_id(url: str) -> str:
        if not url:
            return ''
        match = re.search(r'[?&]id=(\d+)', url)
        return match.group(1) if match else ''

    def _abs_url(self, maybe_relative_url: str) -> str:
        if not maybe_relative_url:
            return ''
        return urllib.parse.urljoin(f'{self.base_url}/', maybe_relative_url)

    def _is_logged_in(self, final_url: str, html: str) -> bool:
        is_not_login_page = 'id="loginform-username"' not in html
        has_logout_marker = ('logout' in html.lower()) or ('/backend/site/logout' in html.lower())

        if self.base_url:
            expected_prefix = f'{self.base_url}/backend'
            on_backend_area = final_url.startswith(expected_prefix)
        else:
            on_backend_area = '/backend' in final_url

        return is_not_login_page and has_logout_marker and on_backend_area
