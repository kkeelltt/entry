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


class Ldap(object):
    def ldifsearch(self, isc_account):
        isc_ldap = {
            'displayName': '',
            'gecos': '',
            'employeeNumber': '',
            'l': '',
            'mail': '',
        }

        for key in isc_ldap.keys():
            cmd = '/home/kelt/entry/isc-ldap/ldifsearch'
            p = Popen([cmd, isc_account, key], stdout=PIPE)
            if key == 'displayName':
                isc_ldap[key] = b64decode(p.communicate()[0].decode())
            else:
                isc_ldap[key] = p.communicate()[0].decode()

        isc_ldap['gecos_last'] = isc_ldap['gecos'].split()[0]

        return isc_ldap

    def ldapsearch(self, club_account):
        arg = 'uid={club_account}'.format(club_account=club_account)
        return Popen(['ldapsearch', arg], stdout=PIPE).communicate()[0]


class Validator(object):
    def wrap_li(self, errors):
        tmp = ''
        for error in errors:
            tmp += '<li>' + error + '</li>'

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
            # else:
            #    l = Ldap()
            #    if 'numEntries' in l.ldapsearch(data['club_account']):
            #        errors.append('この共用計算機アカウント名は既に使用されています')
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
    error_msg = v.check_format(data)
    if error_msg:
        # バリデーションエラー
        return bottle.template('form', display='block',
                               error_msg=v.wrap_li(error_msg), **data)
    else:
        # バリデーションパス -> パスワードの暗号化
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
            session['is'] = ''
            session.save()

        # 確認画面にリダイレクト
        bottle.redirect('/confirm')


@bottle.route('/confirm')
def confirm_get():
    try:
        session = bottle.request.environ.get('beaker.session')
        session['is']
        return bottle.template('confirm', **session)
    except KeyError:
        return bottle.template('lost')


@bottle.route('/confirm', method='POST')
def confirm_post():
    try:
        session = bottle.request.environ.get('beaker.session')
        session['is']

        # メールを送信
        print(bottle.template('for_user', **session, session_id=session.id))
        return bottle.template('identify')
    except KeyError:
        return bottle.template('lost')


@bottle.route('/finish/<session_id>')
def finish_get(session_id=None):
    session = bottle.request.environ.get('beaker.session')
    session['is']
    try:
        if (session_id == session.id) and (session['is'] == ''):
            # セッションIDが正しい
            l = Ldap()
            ldif = bottle.template('ldif',
                                   **l.ldifsearch(session['isc_account']),
                                   **session)
            print(ldif)
            # ldapentry
            # .forward
            # mailman
            # session.delete()
            session['is'] = 'finished'
            session.save()
            return bottle.template('finish',
                                   msg='共用計算機アカウントの申請が完了しました。')
        else:
            return bottle.template('finish',
                                   msg='共用計算機アカウントの申請は完了しています。')
    except KeyError:
        return bottle.template('lost')


if __name__ == '__main__':
    app = SessionMiddleware(bottle.app(), session_opts)
    bottle.run(app=app, host='localhost', port=8080, debug=True, reloader=True)
