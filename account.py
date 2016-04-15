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

keys = [
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


class Validator(object):
    error_msg = {
        'display': None,
        'msg': None
    }

    error_cases = {
        'blank': 'フォームに空欄があります。',
        'student_number': '学生番号が不正です。',
        'isc_account': '情報科学センターアカウントが不正です。',
        'club_account': '共用計算機アカウントが不正です。',
        'password': 'パスワードが不正です。',
        'password_confirm': 'パスワードが一致しません。',
        'agreement': '規約に同意しないとアカウントは申請できません。',

        'used': 'このアカウント名は既に使用されています。'
    }

    def __init__(self):
        self.error_msg['display'] = 'none'
        self.error_msg['msg'] = ''

    def default(self, data):
        errors = []
        # フォームの空欄
        for key, value in data.items():
            if key == 'agreement':
                pass
            elif not value:
                errors.append(self.error_cases['blank'])
                break
        # 学籍番号
        if not re.match('^[0-9]{8}$', data['student_number']):
            errors.append(self.error_cases['student_number'])
        # ISCアカウント
        if not re.match('^[a-z][0-9]{6}[a-z]$', data['isc_account']):
            errors.append(self.error_cases['isc_account'])
        # 共用計算機アカウント
        if not re.match('^[a-z][a-z0-9]{2,7}$', data['club_account']):
            errors.append(self.error_cases['club_account'])
        # パスワード
        ptn1 = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])[ -~]{8,}$'
        ptn2 = '^[ -~]{16,}$'
        if not (re.match(ptn1, data['password']) or
                re.match(ptn2, data['password'])):
            errors.append(self.error_cases['password'])
        else:
            # パスワード（確認）
            if not data['password'] == data['password_confirm']:
                errors.append(self.error_cases['password_confirm'])
        # 同意チェック
        if not data['agreement'] == 'checked':
            errors.append(self.error_cases['agreement'])
        # エラーメッセージをリスト化
        for error in errors:
            self.error_msg['msg'] += '<li>' + error + '</li>'
        # エラーメッセージを表示
        if self.error_msg['msg']:
            self.error_msg['display'] = 'block'

        def collate(self):
            pass


@bottle.route('/form')
def form_get():
    v = Validator()
    try:
        # セッション情報がある
        session = bottle.request.environ.get('beaker.session')
        session['is']
        return bottle.template('form', **v.error_msg, **session)
    except KeyError:
        # セッション情報がない
        data = {key: '' for key in keys}
        return bottle.template('form', **v.error_msg, **data)


@bottle.route('/form', method='POST')
def form_post():
    # ポストデータを取得
    data = {key: '' for key in keys}
    for key, value in bottle.request.forms.decode().items():
        if 'password' in key:
            # パスワードは生入力を使用
            data[key] = value
        else:
            data[key] = value.strip()

    v = Validator()
    if v.validate(data):
        # バリデーションエラー
        return bottle.template('form', **v.error_msg, **data)
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
