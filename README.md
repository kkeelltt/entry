# アカウント申請自動化ツール

### 使用したサードパーティ製ライブラリ
* bottle  # Webフレームワーク
* beaker  # セッションミドルウェア
* pytz    # タイムゾーン

`# pip install bottle beaker pytz`

***

### ファイル構成
```
.
├── account.py        # メインのスクリプト
└── views
    ├── confirm.tpl   # 確認画面
    ├── finish.tpl    # アカウント発行完了
    ├── for_user.tpl  # 確認メール文面
    ├── form.tpl      # 申請フォーム
    ├── identify.tpl  # 確認メール送信
    ├── ldif.tpl      # ldif文面
    └── lost.tpl      # セッションロスト
```

***

### テスト方法
申請フォーム  
`$ python ./entry.py`  

http://localhost:8080/form
