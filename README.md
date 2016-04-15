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
├── account.py
└── views
    ├── confirm.tpl
    ├── finish.tpl
    ├── for_user.tpl
    ├── form.tpl
    ├── identify.tpl
    └── ldif.tpl
```

***

### テスト方法
申請フォーム  
`$ python ./entry.py`  
`http://localhost:8080/form`
