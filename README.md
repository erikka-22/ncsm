# ncsm
名古屋市科学館で使う音声入力コミュニケーションツール
This software is released under the MIT License, see LICENSE.txt.

- ファイルを直接見ている人へ
このREADME.mdにはいくつか画像が添付されています．添付画像はGithub上でしか見られないので，下記リンクからGithubの画面を見てもらうのがわかりやすいでしょう．
https://github.com/erikka-22/ncsm

## google_cloud_speech_v1.py
音声認識APIを操作するメインプログラム．
このプログラムを実行するときには，以下の手順を踏む必要があります．
1. Google Cloud Platform の設定 (初回のみ)
2. python仮想環境のactivate
3. websocketサーバ側プログラム(Processingのプログラム)の立ち上げ

### Google Cloud Platform(以下GCP) の設定
本プログラムはGCPで提供されているCloud Speech-to-Text APIを利用しています．$300を上限に，1年間無料で利用できるので，よっぽど課金されることはありません．  
読者として入学当初の右も左もわからなかった私を想定して書いており，かなり丁寧な説明になっています．既にGCPを利用したことがある人はやらなくてもいい手順があるでしょう．必要に応じて飛ばしてください．  
また，これは2020年3月13日時点の情報です．それ以降に，ページのUIや設定方法が変更されていたり，はたまたサービスが終了していたりすることは十分あり得るので，つまづく所があれば最新の情報を確認してください．

#### ブラウザでの作業
1. GCP無料トライアルの登録
まずはGCPのページにアクセス．下記リンクにアクセスしてください．  
https://console.cloud.google.com/  
すると，Googleアカウントのログイン画面が出てきます．ログインしてください．
![googleログイン画面](https://user-images.githubusercontent.com/38452536/76594348-3895b580-653c-11ea-8f76-738662b12e94.png)

ログインしたら，こんな画面が出てきます．
国は日本のまま，2箇所にチェックを入れ，左下の「同意して続行」をクリック．
![同意して続行](https://user-images.githubusercontent.com/38452536/76595415-e6a25f00-653e-11ea-898a-27cbd1b17867.png)

「無料トライアルに登録」をクリック．
![ホーム画面](https://user-images.githubusercontent.com/38452536/76595801-f7070980-653f-11ea-9e22-e854b7c368d9.png)

国は日本のまま，利用規約にチェックを入れて，「続行」をクリック．
![ステップ1/2](https://user-images.githubusercontent.com/38452536/76596364-50236d00-6541-11ea-9a7b-b66caa9a434c.png)

次の画面でも，必要事項を記入して，「無料トライアルを開始」をクリック．内容は正しいものをいれなくても，適当で問題ありません．

2. Cloud Speech-to-Text APIの設定
上部中央の検索窓に「speech」と入力すると，Cloud Speech-to-Text APIが出てくるので，選択してください．
![Cloud Speech-to-Text API](https://user-images.githubusercontent.com/38452536/76597984-24a28180-6545-11ea-9fe8-4451657888c9.png)
似たものに「Cloud Text-to-Speech API」があるので，間違えないようにしてください．ちなみにText~の方は，文字を自動で読み上げるAPIです．



### 仮想環境のactivate
本プログラムを実行する際は，仮想環境で実行してください．
仮想環境でないと，モジュールenums,typesがインポートエラーになってしまいます．

一応，必要なモジュールをインストールした環境を用意したので，それを利用して実行してみてください．
下記のコマンドで仮想環境をアクティベートできます.  
筆者はfishを利用していたので，bashの場合のやつは確認できてないです．zsh等その他のシェルを利用している場合は各自調べてください．  

`$ cd /path/to/thisdirectory`   
`(bashの場合) $ source venv/bin/activate`      
`(fishの場合) $ source venv/bin/activate.fish`  

requirements.txtも用意しました．自身で作成した環境に必要なモジュールをインストールして実行していただいても大丈夫です．


- 先にサーバプログラムを実行すること
- 
