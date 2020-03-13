# ncsm
名古屋市科学館で使う音声入力コミュニケーションツール
This software is released under the MIT License, see LICENSE.txt.

## google_cloud_speech_v1.py
音声認識APIを操作するメインプログラム．
このプログラムを実行するときには，以下の手順を踏む必要があります．
1. Google Cloud Platform の設定 (初回のみ)
2. python仮想環境のactivate
3. websocketサーバ側プログラム(Processingのプログラム)の立ち上げ

### gcpの認証について
本プログラムはGoogle Cloud Platform で提供されているSpeech-to-Text APIを利用しています．そのため，


### 仮想環境での実行
本プログラムを実行する際は，仮想環境で実行してください．
(仮想環境でないと，モジュールenums,typesがインポートエラーになってしまいます．)

一応，必要なモジュールをインストールした環境を用意したので，それを利用して実行してみてください．
下記のコマンドで仮想環境をアクティベートできます.
(筆者はfishを利用していたので，bashの場合のやつは確認できてないです．zsh等その他のシェルを利用している場合は各自調べてください．)  
`
$ cd /path/to/thisdirectory /n    
(bashの場合) $ source venv/bin/activate      
(fishの場合) $ source venv/bin/activate.fish  
`

requirement.txtも用意しました．自身で作成した環境に必要なモジュールをインストールして実行していただいても大丈夫です．


- 先にサーバプログラムを実行すること
- 
