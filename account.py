#!/user/bin/python
# -*- coding: utf-8 -*-

from base64 import b64decode
from base64 import b64encode
from datetime import datetime
# from email.mime.text import MIMEText
# from email.utils import formatdate
import hashlib
import re
# from smtplib import SMTP
from socket import gethostbyaddr
from subprocess import PIPE
from subprocess import Popen

from beaker.middleware import SessionMiddleware
import bottle
import pytz

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 60 * 60,
    'session.data_dir': './session',
    'session.auto': False
}

form_keys = [
    'name_last',
    'name_first',
    'name_last_kana',
    'name_first_kana',
    'student_number',
    'isc_account',
    'club_account',
    'password',
    'password_confirm',
    'agreement'
]


class Validator(object):
    def wrap_li(self, errors):
        tmp = ''
        for error in errors:
            tmp += '<li>' + error + '</li>'
        else:
            return tmp

    def check_format(self, data):
        errors = []
        # 性
        if not data['name_last']:
            errors.append('氏名（性）が未入力です')
        # 名
        if not data['name_first']:
            errors.append('氏名（名）が未入力です')
        # せい
        if not data['name_last_kana']:
            errors.append('ふりがな（せい）が未入力です')
        # めい
        if not data['name_first_kana']:
            errors.append('ふりがな（めい）が未入力です')
        # 学籍番号
        if not data['student_number']:
            errors.append('学生番号が未入力です')
        else:
            if not re.match('^[0-9]{8}$', data['student_number']):
                errors.append('学生番号が不正です。')
        # ISCアカウント
        if not data['isc_account']:
            errors.append('情報科学センターアカウント名が未入力です')
        else:
            if not re.match('^[a-z][0-9]{6}[a-z]$', data['isc_account']):
                errors.append('情報科学センターアカウント名が不正です。')
        # 共用計算機アカウント
        if not data['club_account']:
            errors.append('共用計算機アカウント名が未入力です')
        else:
            if not re.match('^[a-z][a-z0-9_]{2,7}$', data['club_account']):
                errors.append('共用計算機アカウント名が不正です。')
        # パスワード
        ptn1 = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])[ -~]{8,}$'
        ptn2 = '^[ -~]{16,}$'
        if not data['password']:
            errors.append('パスワードが未入力です')
        else:
            if not (re.match(ptn1, data['password']) or
                    re.match(ptn2, data['password'])):
                    errors.append('パスワードが不正です')
            else:
                # パスワード（確認）
                if not data['password'] == data['password_confirm']:
                    errors.append('パスワードが一致しません。')
        # 同意チェック
        if not data['agreement'] == 'checked':
            errors.append('規約に同意しないとアカウントは申請できません。')

        return errors

        def check_ldap(self, data):
            pass


class SubProcess(object):
    isc_ldap = {
        'displayName': '',
        'gecos': '',
        'employeeNumber': '',
        'l': '',
        'mail': '',
    }

    def ldifsearch(self, data):
        for key in self.isc_ldap.keys():
            cmd = '/home/kelt/entry/isc-ldap/ldifsearch'
            p = Popen([cmd, data['isc_account'], key], stdout=PIPE)
            if key == 'displayName':
                self.isc_ldap[key] = b64decode(p.communicate()[0].decode())
            else:
                self.isc_ldap[key] = p.communicate()[0].decode()
        else:
            self.isc_ldap['gecos_last'] = self.isc_ldap['gecos'].split()[0]

    def ldapsearch(self, data):
        arg = 'uid={club_account}'.format(**data)
        return Popen(['ldapsearch', arg], stdout=PIPE)


@bottle.route('/form')
def form_get():
    try:
        # セッション情報がある
        session = bottle.request.environ.get('beaker.session')
        session['is']
        return bottle.template('form', display='none', error_msg='', **session)
    except KeyError:
        # セッション情報がない
        data = {key: '' for key in form_keys}
        return bottle.template('form', display='none', error_msg='', **data)


@bottle.route('/form', method='POST')
def form_post():
    # ポストデータを取得
    data = {key: '' for key in form_keys}
    for key, value in bottle.request.forms.decode().items():
        if 'password' in key:
            # パスワードは生入力を使用
            data[key] = value
        else:
            data[key] = value.strip()

    # バリデーション
    v = Validator()
    errors = v.check_format(data)
    if errors:
        # フォーマットバリデーションエラー
        return bottle.template('form', display='block',
                               error_msg=v.wrap_li(errors), **data)
    elif False:
        pass
    else:
        # バリデーションパス
        # パスワードの暗号化
        h = hashlib.sha1()
        h.update(data['password'].encode())
        data['shadow_password'] = '{SHA}' + b64encode(h.digest()).decode()

        # 申請日時と申請元アドレスを取得
        tmp = datetime.now(pytz.timezone('Asia/Tokyo'))
        data['format_time'] = tmp.strftime('%Y-%m-%d %H:%M:%S %z')
        data['remote_addr'] = bottle.request.remote_addr
        try:
            data['remote_host'] = gethostbyaddr(data['remote_addr'])[0]
        except OSError:
            data['remote_host'] = '-----'

        # セッションに保存
        session = bottle.request.environ.get('beaker.session')
        for key, value in data.items():
            session[key] = value
        else:
            session['is'] = None
            session.save()
            # 確認画面にリダイレクト
            bottle.redirect('/confirm')


@bottle.route('/confirm')
def confirm_get():
    session = bottle.request.environ.get('beaker.session')
    return bottle.template('confirm', **session)


@bottle.route('/confirm', method='POST')
def confirm_post():
    session = bottle.request.environ.get('beaker.session')
    # メールの文面を標準出力
    print(bottle.template('for_user', **session, session_id=session.id))
    bottle.redirect('/identify')


@bottle.route('/identify')
def identify_get():
    return bottle.template('identify')


@bottle.route('/finish/<key>')
def finish_get(key=None):
    session = bottle.request.environ.get('beaker.session')

    s = SubProcess()
    s.ldifsearch(session)
    print(bottle.template('ldif', **s.isc_ldap, **session))
    # .forward
    # mailman
    session.delete()
    return bottle.template('finish')


if __name__ == '__main__':
    app = SessionMiddleware(bottle.app(), session_opts)
    bottle.run(app=app, host='localhost', port=8080, debug=True, reloader=True)
