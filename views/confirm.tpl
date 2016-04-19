<!DOCtYPE html>
<html lang=ja>
<head>
<meta charset="UTF-8">
<title>共用計算機アカウント申請確認</title>
</head>

<body>
<h1>確認</h1>
<p>以下の内容で申請しますが、よろしいですか？</p>
<p>=================================================================</p>
<p> 共用計算機アカウント発行依頼</p>
<p>=================================================================</p>
<p>  Name    : {{name_last}} {{name_first}} ({{name_last_kana}} {{name_first_kana}})</p>
<p>  Number  : {{student_number}}</p>
<p>  ISC-Mail: {{isc_account}}@mail.kyutech.jp</p>
<p>----------------------------------------------------------------</p>
<p>  Account : {{club_account}}</p>
<p>----------------------------------------------------------------</p>
<p>  Date    : {{format_time}}</p>
<p>  From    : {{remote_host}} ({{remote_addr}})</p>
<p>=================================================================</p>
<form action="/confirm" method="POST">
    <input type="submit" value="申請する">
    <input type="button" value="修正する" onclick="location.href='/form'">
</form>
</body>

</html>
