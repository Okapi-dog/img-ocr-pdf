# img-ocr-pdf
img-ocr-pdfはJPGイメージの集合から検索可能なPDFを[Google Cloud Vision](https://cloud.google.com/vision)を用いて作成します。
このプロジェクトは環境依存をなるべく無くしています。
また、[Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP)を埋め込んだりすることで、表現可能な文字を増やしています。
さらに、既存のGoogle Cloud Visionを使ったOCRでは、文字の下にアンダーバーのように検索用の文字が埋め込まれていましたが、このプログラムでは元の文字と同等の大きさの文字を埋め込んでいます。

# この下は、編集途中
<!-- BEGIN-MARKDOWN-TOC -->
* [Installation](#installation)
* [Usage](#usage)
* [Usage of libraries](#usage-of-libraries)
	* [How to get OCR (json) data](#how-to-get-ocr-json-data)
    * [How to convert OCR (json) data into hocr](#how-to-convert-ocr-json-data-into-hocr)
    * [How to make a searchable pdf from hocr](#how-to-make-a-searchable-pdf-from-hocr)
* [Acknowledgments](#acknowledgments)
* [Licence](#licence)

<!-- END-MARKDOWN-TOC -->

## Installation
全て同じディレクトリに入れる。

venvなどの仮想環境下で以下のコマンド入れて、pythonライブラリをインストールする。
```sh
$ pip3 install -r requirements.txt
```

tkinterライブラリをインストールする。これは、OSによってインストール方法が異なる。

Google Cloud Vision APIを使用するためのAPIキーを取得します。[この記事](https://zenn.dev/tmitsuoka0423/articles/get-gcp-api-key)などが参考になります。

## Usage

```sh
$ python3 makepdfGUI.py
```

Set Google API Key via press "Config" button.

Set output pdf file via press "Set pdf file" button.

Select input image file(__only end up with ".jpg"__) directry via press "Set IMG dir" button.

Wait until "Done" is shown.

## Usage of libraries


### How to get OCR (json) data:

```sh
$ python3 gcv.py
```

There are API & image path settigns on gcv.py's code

This outputs `test.jpg.json`

`test.jpg.json` is a output of [Google Cloud Vision OCR](https://cloud.google.com/vision/docs/).

### How to convert OCR (json) data into hocr
```sh
$ python3 gcv2hocr.py test.jpg.json output.hocr
```

`output.hocr` is a output of gcv2hocr.py




### How to make a searchable pdf from hocr:

To create a searchable pdf, use the `hocr2pdf.py`.


## Source codes
gcv2hocr.py: https://github.com/dinosauria123/gcv2hocr/blob/master/gcv2hocr.py

hocr-pdf.py: slightly modified from https://github.com/tmbdev/hocr-tools/blob/master/hocr-pdf

makepdfGUI.py: slightly modified from https://github.com/dinosauria123/gcv2hocr/blob/master/makepdfGUI.py

## Licence

Licence for gcv.py is MIT.

Other files follow original source code licenses.

