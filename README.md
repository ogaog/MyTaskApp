これは[この記事](https://qiita.com/drafts/174b0de5467ddf5362c5/edit)のアプリです．

### ファイル構成
```
MyTaskApp/
├── .env
├── credentials_service.json
├── serviceApi.py
└── window.py
```
- **.env**
  
タスクを管理する google カレンダーのIDと，ChatGPT の API を保存しておくファイル．serviceApi.py で呼び出される．
- **credentials_service.json**

Google Cloud Platform で OAuth Client を作成した時にダウンロードした Json ファイル．serviceApi.py で呼び出される．
- **serviceApi.py**

API を扱う関数をまとめたファイル．window.py でインポートされる．
- **window.py**

アプリを動かすメインのファイルで，このファイルを実行する．Flet を用いた GUI の記述がほとんど．

### よく出てくるデータ
[google calendar api で扱う **event** ](https://developers.google.com/calendar/api/v3/reference/events)は次のような dict 型で，一つのイベント情報を記録しています．serviceApi.py , window.py に出てくる ``event`` , ``*_event`` という変数にはこのデータが入るようにしたはずです．
```python
{
  "id": string,
  "summary": string,
  "description": string,
  "start": {
    "dateTime": datetime
  },
  "end": {
    "dateTime": datetime
  }
}
```
