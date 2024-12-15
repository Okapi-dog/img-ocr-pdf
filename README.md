# 概要
img-ocr-pdfはJPGイメージの集合から検索可能なPDFを[Google Cloud Vision](https://cloud.google.com/vision)を用いて作成します。
また、[Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP)を埋め込んだりすることで、表現可能な文字を増やしています。
さらに、既存のGoogle Cloud Visionを使ったOCRでは、文字の下にアンダーバーのように検索用の文字が埋め込まれていましたが、このプログラムでは元の文字と同等の大きさの文字を埋め込んでいます。また、並行に処理を実行することで、google vision apiを叩く時間を大幅に短縮しました。


また、スクリーンショットの自動化はOS固有の自動化ソフトを使うか、このプログラムに添付されているScreenShotGUI.pyを使ってください。ScreenShotGUIに必要なPyAutoGUIはセキュリティ上の理由から、requirements.txt上ではコメントアウトしているので必要な方はコメントアウトを外してインストールしてください。

<!-- BEGIN-MARKDOWN-TOC -->
* [インストール](#インストール)
* [使用方法](#使用方法)
    * [スクリーンショットを自動で撮る](#スクリーンショットを自動で撮る)
    * [jpgから検索可能なpdfを作る](#jpgから検索可能なpdfを作る)
* [ライブラリの使用方法](#ライブラリの使用方法)
	* [GCVからOCRデータを取得する方法](#gcvからocrデータを取得する方法)
    * [GCVのOCRデータをhocrに変換する方法](#gcvのocrデータをhocrに変換する方法)
    * [hocrから検索可能なPDFを作成する方法](#hocrから検索可能なpdfを作成する方法)
* [ソースコード元](#ソースコード元)
* [ライセンス](#ライセンス)

<!-- END-MARKDOWN-TOC -->

## インストール

1. ファイルをダウンロード後、そのディレクトリに移動します。

2. ScreenShotGUI.pyを使用する方は、下のようにrequirements.txtにあるpyautoguiのコメントアウトを外してください。
```txt
#pyautogui #説明書き    <-コメントアウトしてる状態
pyautogui #説明書き     <-コメントアウト外した状態
```


3. venvなどの仮想環境下で以下のコマンドを実行し、Pythonライブラリをインストールします。
```sh
$ pip3 install -r requirements.txt
```

4. tkinterライブラリをインストールします。インストール方法はOSによって異なります。

5. Google Cloud Vision APIを使用するためのAPIキーを取得します。[この記事](https://zenn.dev/tmitsuoka0423/articles/get-gcp-api-key)などが参考になります。

## 使用方法

### スクリーンショットを自動で撮る

1. 以下のコマンドをダウンロードしたディレクトリ内で実行して、アプリを起動します。

```sh
$ python3 ScreenShotGUI.py
```

2. "Config"ボタンを押して、撮影準備時間や撮影間隔などを半角数字で設定します。

3. "Set JPG dir"ボタンを押して保存先ディレクトリを選択します。2,3回押すと、選択ウィンドウが出てきたりします。

4. 保存先ディレクトリ選択後、撮影準備時間が経過するとすぐに撮影が開始されるので、すぐさま撮影したい画面を写しておきます。

5. 終わったら"Quit"でアプリを終了しても大丈夫です。

6. 保存先ディレクトリ内に画像が格納されています。

### jpgから検索可能なpdfを作る

注意. Google Cloud Vision APIを使用する関係上、課金される可能性があります。詳しくはAPIの料金説明をご確認ください。

1. 以下のコマンドをダウンロードしたディレクトリ内で実行して、アプリを起動します。

```sh
$ python3 makepdfGUI.py
```

2. "Config"ボタンを押してGoogle APIキーを設定します。


3. "Set JPG dir"ボタンを押して入力画像ファイル（__.jpg で終わるファイルのみ__）のディレクトリを選択します。2,3回押すと、選択ウィンドウが出てきたりします。

4. "Done"と表示されるまで待ちます。終わったら"Quit"でアプリを終了しても大丈夫です。

5. 入力画像ファイルのディレクトリ内にout0.pdfが作成されます。

## ライブラリの使用方法


### GCVからOCRデータを取得する方法

```sh
$ python3 gcv.py
```

There are API & image path settigns on gcv.py's code

This outputs `test.jpg.json`

`test.jpg.json` is a output of [Google Cloud Vision OCR](https://cloud.google.com/vision/docs/).

### GCVのOCRデータをhocrに変換する方法
```sh
$ python3 gcv2hocr.py test.jpg.json output.hocr
```
`test.jpg.json`はgcv.pyが出力したGCVのOCRデータ(json)です。
`output.hocr` はgcv2hocr.pyの出力先です。




### hocrから検索可能なPDFを作成する方法:

検索可能なPDFを作成するには、 hocr2pdf.py を使用します。


## ソースコード元
gcv2hocr.py: https://github.com/dinosauria123/gcv2hocr/blob/master/gcv2hocr.py

hocr-pdf.py: slightly modified from https://github.com/tmbdev/hocr-tools/blob/master/hocr-pdf

makepdfGUI.py: slightly modified from https://github.com/dinosauria123/gcv2hocr/blob/master/makepdfGUI.py

## ライセンス

gcv.pyのライセンスはMITです。

その他のファイルは、元のソースコードのライセンスに従います。

