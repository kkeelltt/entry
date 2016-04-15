# アカウント申請自動化ツール

### 使用したサードパーティ製ライブラリ
* bottle
* beaker
* pytz

`# pip install bottle beaker pytz`

***

### ファイル構成
```
.
├── account.py        # メインのスクリプト
└── views
    ├── confirm.tpl   # 確認画面
    ├── finish.tpl    # アカウント発行完了
    ├── for_user.tpl  # 確認メールの文面
    ├── form.tpl      # 申請フォーム
    ├── identify.tpl  # 確認メールを送信
    └── ldif.tpl      # ldifの文面
```

***

### テスト方法
申請フォーム  
`$ python ./entry.py`  

http://localhost:8080/form
