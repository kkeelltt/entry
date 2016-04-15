<!DOCTYPE html>
<html lang=ja>
<head>
<meta charset="UTF-8">
<title>共用計算機 (remote) アカウント申請受付 - 九州工業大学 学生自治ネットワーク委員会</title>
</head>

<body>
<div class="box" style="margin: 1em;">
    <h2 class="box-header"><span class="mw-headline"><big>申請フォーム</big></span></h2>
    <p>九州工業大学 学生自治ネットワーク委員会 御中</p>
    <p>共用計算機利用規約に同意し、共用計算機 (remote.club.kyutech.ac.jp) のアカウントの発行を申請します。</p>
    <div style="display: {{display}}">
        <ul>{{!msg}}</ul>
    </div>
    <form action="/form" method="POST">
        <fieldset>
            <legend>申請者情報</legend>
            <dl>
                <dt>氏名</dt>
                <dd><strong>姓</strong>(例: 九工)</dd>
                <dd><input name="name_last" size="30" value="{{name_last}}"></dd>
                <dd><strong>名</strong>(例: 太郎)</dd>
                <dd><input name="name_first" size="30" value="{{name_first}}"></dd>
                <dt>ふりがな</dt>
                <dd><strong>せい</strong>(例: きゅうこう)</dd>
                <dd><input name="name_last_kana" size="30" value="{{name_last_kana}}"></dd>
                <dd><strong>めい</strong>(例: たろう)</dd>
                <dd><input name="name_first_kana" size="30" value="{{name_first_kana}}"></dd>
                <dt>学生番号</dt>
                <dd>例: 12230000</dd>
                <dd><input name="student_number" size="20" value="{{student_number}}"></dd>
                <dt>九工大ID(情報科学センターアカウント名)</dt>
                <dd>例: m230000i</dd>
                <dd><input name="isc_account" size="20" value="{{isc_account}}">@mail.kyutech.jp<br>
            </dl>
        </fieldset>
        <fieldset>
            <legend>アカウント情報</legend>
            <dl>
                <dt>希望アカウント名</dt>
                <dd><strong>注:以下のすべての条件を満たしてください。</strong></dd>
                <dd>
                    <ul>
                    <li>３～８文字のもの</li>
                    <li>英大文字、記号、全角文字などを含まないもの</li>
                    <li>先頭に数字を用いていないもの</li>
                    </ul>
                </dd>
                <dd><input name="club_account" size="10" value="{{club_account}}">@club.kyutech.ac.jp</dd>
                <dt>パスワード</dt>
                <dd><strong>注:以下のいずれかの条件を満たしてください。</strong></dd>
                <dd>
                    <ul>
                    <li>８文字以上で数字、英大文字、英小文字、記号のすべてを含んでいるもの</li>
                    <li>１６文字以上のもの</li>
                    </ul>
                </dd>
                <dd><input name="password" size="20" value="{{password}}"></dd>
                <dt>パスワード(確認)</dt>
                <dd><input name="password_confirm" size="20" value="{{password_confirm}}"></dd>
            </dl>
        </fieldset>
        <fieldset>
            <legend>申請</legend>
            <div class="buttons">
                <p><input type="checkbox" name="agreement" value="checked" {{agreement}}>利用規約に同意し、アカウントを申請します。</p>
                <p><input type="submit" value="確認する"></p>
            </div>
        </fieldset>
    </form>
</div>
</body>

</html>
