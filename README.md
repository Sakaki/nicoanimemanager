# nicoanimemanager
ニコニコ動画の公式が放送しているアニメをダウンロード・管理します

## 準備
pipとかでflaskとbeautifulsoup4を入れてください。

## 使い方
```
python server.py
```
を実行すると、9090番ポートでサーバーが起動します。
アクセスして、設定画面からニコニコ動画アカウントの設定を行ってください。

cronで
```
curl 192.168.XXX.XXX:9090/api/updatechinfo
curl 192.168.XXX.XXX:9090/api/dlallanimes
```
とか登録しておくと自動的にダウンロードしてくれるかも・・・

## 動画再生について
[MediaElement.js](http://mediaelementjs.com/)を使わせていただいています。
ソースにも含まれていますので、その部分のライセンスはMediaElement.jsを参照してください。