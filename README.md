# ncsm
名古屋市科学館で使う音声入力コミュニケーションツール
This software is released under the MIT License, see LICENSE.txt.

- ファイルを直接見ている人へ  
このREADME.mdにはいくつか画像が添付されています．添付画像はGithub上でしか見られないので，下記リンクからGithubの画面を見てもらうのがわかりやすいでしょう．
https://github.com/erikka-22/ncsm

## google_cloud_speech_v1.py
音声認識APIを操作するメインプログラム．

### 起動の説明
このプログラムを実行するときには，以下の手順を踏む必要があります．
1. Google Cloud Platform の設定 (初回のみ)
2. python仮想環境のアクティベート
3. websocketサーバ側プログラム(Processingのプログラム)の立ち上げ

#### Google Cloud Platform(以下GCP) の設定
本プログラムはGCPで提供されているCloud Speech-to-Text APIを利用しています．$300を上限に，1年間無料で利用できるので，よっぽど課金されることはありません．  
読者として入学当初の右も左もわからなかった私を想定して書いており，かなり丁寧な説明になっています．既にGCPを利用したことがある人はやらなくてもいい手順があるでしょう．必要に応じて飛ばしてください．  
また，これは2020年3月13日時点の情報です．それ以降に，ページのUIや設定方法が変更されていたり，はたまたサービスが終了していたりすることは十分あり得るので，つまづく所があれば最新の情報を確認してください．

##### ブラウザでの作業
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
左のナビゲーションメニューから「APIとサービス」>「ライブラリ」を選択．
![nav-choice](https://user-images.githubusercontent.com/38452536/76599133-b01d1200-6547-11ea-9525-89fb666dd28c.png)

「APIとサービスを検索」と書かれた検索窓で，「Cloud Speech-to-Text API」と検索し，結果を選択．
![search](https://user-images.githubusercontent.com/38452536/76599467-70a2f580-6548-11ea-85fb-b5777fd12aee.png)

「有効にする」をクリック．
![有効にする](https://user-images.githubusercontent.com/38452536/76599594-b95aae80-6548-11ea-844d-439f8a77f7a2.png)
その後，「課金を有効にする」をクリック．ここで課金を有効にしても，1年間は$300の無料クレジットが消費されるので，$300を超えない限り費用を請求されることはありません．ただし1年を超えると自動更新されて課金が始まるので，試し終わったらAPIを無効にすることをお勧めします．  
(念のため料金設定について．60分まで無料・60分を超える分は15秒あたり$0.006という料金設定です．無料クレジット利用期間が終了した後でも，高額な請求が行くことはよっぽど無いでしょう．)

3. 認証情報の作成
Cloud Speech-to-Text APIを利用するためには認証が必要です．認証とは，ユーザを識別することです．Cloud Speech-to-Text APIは従量課金制のAPIで，ユーザAが利用した分の請求がユーザBに届くことや，フリーライダー(お金を払わずに使う人)が発生することを防ぐ必要があります．そのための仕組みが認証です．

「認証情報を作成」をクリック．
![認証情報を作成](https://user-images.githubusercontent.com/38452536/76603616-9cc27480-6550-11ea-859c-8980dae58e76.png)

プルダウンから「Cloud Speech-to-Text API」を選択．下のラジオボタンについては，本プログラムを動かすだけならば「いいえ，使用していません」を選択.  
ちなみに，Google Compute Engine はGCPで提供している仮想コンピュータ(VM)，Google App Engine はウェブ/モバイルアプリ運営のためのサーバ管理等を代替するサービスです．例えば，「科学館モバイルガイドが大好評でアクセス数激増！サーバを増強しないと対応できないけど，新しいコンピュータは買えない．．．」的な時に利用できそうな感じのサービスですね．
![認証情報を調べる](https://user-images.githubusercontent.com/38452536/76726443-81e04200-6794-11ea-989c-7bc5210cc116.png)
そして，「必要な認証情報」をクリック．

サービスアカウント名の欄は適当に埋めてください．何でもいいです．  
役割はProject>オーナーを選択してください．キーのタイプはJSONを選択してください．
![サービスアカウント作成](https://user-images.githubusercontent.com/38452536/76727281-f1573100-6796-11ea-9ccf-485bf612a878.png)
そして「次へ」をクリック．

すると，「サービスアカウントとキーが作成されました」と表示されるので，表示を閉じてください．  

##### シェルでの作業
ここからは，自分のパソコンの設定を変更する作業を行います．
「My First Project-(英数字羅列).json」というファイルがダウンロードされていることを確認してください．
確認できたら，「My First Project-(英数字羅列).json」を安全な任意のディレクトリに移動してください．重要な情報が入ったファイルなので，うっかり消してしまったり，うっかりGithubで公開してしまったりする危険性の無いディレクトリに置いてください．

そしたら，環境変数GOOGLE_APPLICATION_CREDENTIALSを設定して，「My First Project-(英数字羅列).json」を指定します．詳しくは下記URLを見てください．
https://cloud.google.com/docs/authentication/getting-started?hl=ja

ちなみにfishだと，config.fishに
`set -x GOOGLE_APPLICATION_CREDENTIALS '/path/to/the/directory/My First Project-(英数字羅列).json'`
と追記すればOKです．


#### 仮想環境のアクティベート
本プログラムを実行する際は，仮想環境で実行してください．
仮想環境でないと，モジュールenums,typesがインポートエラーになってしまいます．

一応，必要なモジュールをインストールした環境を用意したので，それを利用して実行してみてください．(venvというディレクトリが，仮想環境のディレクトリです．)
下記のコマンドで仮想環境をアクティベートできます.  
筆者はfishを利用していたので，bashの場合のやつは確認できてないです．zsh等その他のシェルを利用している場合は各自調べてください．  

`(bashの場合) $ source path/to/ncsm/venv/bin/activate`      
`(fishの場合) $ source path/to/ncsm/venv/bin/activate.fish`  

requirements.txtも用意しました．自身で作成した環境に必要なモジュールをインストールして実行しても大丈夫です．もしトラブルが起きた時は，
- Google Cloud SDKのインストール
- Cloud SDK ツールの承認
辺りが原因として考えられる気がするので，ググって対応してください．

#### websocketサーバ側プログラム(Processingのプログラム)の立ち上げ
google_cloud_speech_v1.pyはaftertaste(Processingのプログラム)と対になっています．
websocketという規格で通信を行っており，aftertasteがサーバ側，google_cloud_speech_v1.pyがクライアント側になっています．
2つのプログラムを動かすことで，アプリケーションを実行できます．この際，必ずサーバ側(aftertaste)から立ち上げてください．クライアント側(google_cloud_speech_v1.py)から立ち上げると，通信エラーでプログラムが止まってしまいます．

### aftertasteから受け取る文字列
|文字列|内容|
|:--|:--|
|connected|音声文字起こしを始めるフラグ|
|end|音声文字起こしを終わるフラグ|
|done|文字起こし結果をJSONファイル書き込むフラグ|
|z + 数字|展示物のユニークID(aftertasteに一覧表があります)|
|数字のみ|似顔絵風顔アイコンのユニークID|

## testWordSending.py
aftertaste(Processing)とwebsokcetで通信して，数字列を送るプログラム．
Processing側プログラムを変更して，動作確認したいけども，声は出しづらい状況．．．っていうときに使ってください．

## functions/
google_cloud_speech_v1.pyで利用されている自作モジュールがあるディレクトリ．

## venv/
実行のための仮想環境のディレクトリ．