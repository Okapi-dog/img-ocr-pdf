#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Create a searchable PDF from a pile of HOCR + JPEG. Tested with
# Tesseract.

import argparse
import base64
import glob
import io
import os.path
import re
import sys
import zlib

from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from lxml import etree, html
from PIL import Image
font="NotoSansJP-Regular" # 使用するフォント 変更する際は、load_jpn_font2(),load_invisible_font()の部分も変更する必要がある

class StdoutWrapper:
    """
    Wrapper around stdout that ensures 'bytes' data is decoded
    to 'latin1' (0x00 - 0xff) before writing out. This is necessary for
    the invisible font to be injected as bytes but written out as a string.
    """

    def write(self, data, *args, **kwargs):
        if bytes != str and isinstance(data, bytes):
            data = data.decode('latin1')
        sys.stdout.write(data)


def export_pdf(playground, default_dpi, savefile=False,IsLimitingSize=False):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    images = sorted(glob.glob(os.path.join(playground, '*.jpg')))
    if len(images) == 0:
        print(f"WARNING: No JPG images found in the folder {playground}"
              "\nScript cannot proceed without them and will terminate now.\n")
        sys.exit(0)
    pdf = Canvas(savefile if savefile else StdoutWrapper(), pageCompression=1)


    load_jpn_font()         # NotoSansJP-Regularを使用する。このフォントは、日本語のOCRに適している。
    #load_jpn_font2()       # if you can't use NotoSansJP-Regular, use HeiseiMin-W3. Notoが使用できない場合に使用する。しかし、このフォントは、Notoより数学系が弱い。 
    #load_invisible_font()  # invisible font cannnot use in japanese. 日本語ではinvisible fontは使えない。
    pdf.setFont(font, 8)    # Set the font to use. 使用するフォントを設定する。 


    pdf.setCreator('hocr-tools')
    pdf.setTitle(os.path.basename(playground))
    dpi = default_dpi
    for image in images:
        im = Image.open(image)
        w, h = im.size
        try:
            dpi = im.info['dpi'][0]
        except KeyError:
            pass
        dpi = calculate_dpi(w,h,dpi,IsLimitingSize)

        width = w * 72 / dpi
        height = h * 72 / dpi
        
        pdf.setPageSize((width, height))
        pdf.drawImage(image, 0, 0, width=width, height=height)
        add_text_layer(pdf, image, height, dpi)
        pdf.showPage()
    pdf.save()

def calculate_dpi(w,h,dpi,IsLimitingSize): # 画像の縦横の最大値がA4の縦に合うようにdpiを計算する(gsが使えない環境でpdfを生成するための処理。これがないと、大きすぎたり小さすぎたりするpdfが)
    if IsLimitingSize:   # 縦横の最大値をA4の縦に合わせるかどうか
        return (max(w,h) * 72) / 595.35
    else:
        return dpi



def add_text_layer(pdf, image, height, dpi):
    
    """Draw an invisible text layer for OCR data"""
    p1 = re.compile(r'bbox((\s+\d+){4})')
    p2 = re.compile(r'baseline((\s+[\d\.\-]+){2})')
    hocrfile = os.path.splitext(image)[0] + ".hocr"
    hocr = etree.parse(hocrfile, html.XHTMLParser())
    for line in hocr.xpath('//*[@class="ocr_line"]'):
        linebox = p1.search(line.attrib['title']).group(1).split()
        try:
            baseline = p2.search(line.attrib['title']).group(1).split()
        except AttributeError:
            baseline = [0, 0]
        linebox = [float(i) for i in linebox]
        baseline = [float(i) for i in baseline]
        xpath_elements = './/*[@class="ocrx_word"]'
        if (not (line.xpath('boolean(' + xpath_elements + ')'))):
            # if there are no words elements present,
            # we switch to lines as elements
            xpath_elements = '.'
        for word in line.xpath(xpath_elements):
            rawtext = word.text_content().strip()
            if rawtext == '':
                continue
            box = p1.search(word.attrib['title']).group(1).split()
            box = [float(i) for i in box]
            b = polyval(baseline,(box[0] + box[2]) / 2 - linebox[0]) + linebox[3]
            #b = polyval(baseline, (box[1] + box[3]) / 2 - linebox[1]) + linebox[3]
            text = pdf.beginText()
            text.setTextRenderMode(3)  # 3 for invisible, 0 for visible
            text.setTextOrigin(box[0] * 72 / dpi, height - b * 72 / dpi)
            box_height = (box[3] - box[1]) * 72 / dpi  # ボックスの高さ
            text_height = 8 * box_height / 10  # テキストの高さをボックスの高さの80%に調整(dpiでポイントサイズに変換済み)
            text.setFont(font, text_height)
            font_width = pdf.stringWidth(rawtext, font, text_height)
            if font_width <= 0:
                continue
            box_width = (box[2] - box[0]) * 72 / dpi
            text.setHorizScale(100.0 * box_width / font_width)
            rawtext = get_display(rawtext)
            text.textLine(rawtext)
            pdf.drawText(text)



def polyval(poly, x):
    return x * poly[0] + poly[1]


# Glyphless variation of vedaal's invisible font retrieved from
# http://www.angelfire.com/pr/pgpf/if.html, which says:
# 'Invisible font' is unrestricted freeware. Enjoy, Improve, Distribute freely

def load_jpn_font():
    font_path = '/Users/hitoshi/Desktop/tech/ocr/gcv2hocr2/Noto_Sans_JP/static/NotoSansJP-Regular.ttf'  
    font_path = os.path.join(os.path.dirname(__file__), 'Noto_Sans_JP/static/NotoSansJP-Regular.ttf')
    pdfmetrics.registerFont(TTFont('NotoSansJP-Regular', font_path))  # Register the font with ReportLab(any font-name is fine)

def load_jpn_font2():
     # if you can't use NotoSansJP-Regular, use HeiseiMin-W3. However, this font is weaker in math than Noto.
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

def load_invisible_font():
    font = """
eJzdlk1sG0UUx/+zs3btNEmrUKpCPxikSqRS4jpfFURUagmkEQQoiRXgAl07Y3vL2mvt2ml8APXG
hQPiUEGEVDhWVHyIC1REPSAhBOWA+BCgSoULUqsKcWhVBKjhzfPU+VCi3Flrdn7vzZv33ryZ3TUE
gC6chsTx8fHck1ONd98D0jnS7jn26GPjyMIleZhk9fT0wcHFl1/9GRDPkTxTqHg1dMkzJH9CbbTk
xbWlJfKEdB+Np0pBswi+nH/Nvay92VtfJp4nvEztUJkUHXsdksUOkveXK/X5FNuLD838ICx4dv4N
I1e8+ZqbxwCNP2jyqXoV/fmhy+WW/2SqFsb1pX68SfEpZ/TCrI3aHzcP//jitodvYmvL+6Xcr5mV
vb1ScCzRnPRPfz+LsRSWNasuwRrZlh1sx0E8AriddyzEDfE6EkglFhJDJO5u9fJbFJ0etEMB78D5
4Djm/7kjT0wqhSNURyS+u/2MGJKRu+0ExNkrt1pJti9p2x6b3TBJgmUXuzgnDmI8UWMbkVxeinCw
Mo311/l/v3rF7+01D+OkZYE0PrbsYAu+sSyxU0jLLtIiYzmBrFiwnCT9FcsdOOK8ZHbFleSn0znP
nDCnxbnAnGT9JeYtrP+FOcV8nTlNnsoc3bBAD85adtCNRcsSffjBsoseca/lBE7Q09LiJOm/ttyB
0+IqcwfncJt5q4krO5k7jV7uY+5m7mPebuLKUea7iHvk48w72OYF5rvZT8C8k/WvMN/Dc19j3s02
bzPvZZv3me9j/ox5P9t/xdzPzPVJcc7yGnPL/1+GO1lPVTXM+VNWOTRRg0YRHgrUK5yj1kvaEA1E
xAWiCtl4qJL2ADKkG6Q3XxYjzEcR0E9hCj5KtBd1xCxp6jV5mKP7LJBr1nTRK2h1TvU2w0akCmGl
5lWbBzJqMJsdyaijQaCm/FK5HqspHetoTtMsn4LO0T2mlqcwmlTVOT/28wGhCVKiNANKLiJRlxqB
F603axQznIzRhDSq6EWZ4UUs+xud0VHsh1U1kMlmNwu9kTuFaRqpURU0VS3PVmZ0iE7gct0MG/8+
2fmUvKlfRLYmisd1w8pk1LSu1XUlryM1MNTH9epTftWv+16gIh1oL9abJZyjrfF5a4qccp3oFAcz
Wxxx4DpvlaKKxuytRDzeth5rW4W8qBFesvEX8RFRmLBHoB+TpCmRVCCb1gFCruzHqhhW6+qUF6tC
pL26nlWN2K+W1LhRjxlVGKmRTFYVo7CiJug09E+GJb+QocMCPMWBK1wvEOfRFF2U0klK8CppqqvG
pylRc2Zn+XDQWZIL8iO5KC9S+1RekOex1uOyZGR/w/Hf1lhzqVfFsxE39B/ws7Rm3N3nDrhPuMfc
w3R/aE28KsfY2J+RPNp+j+KaOoCey4h+Dd48b9O5G0v2K7j0AM6s+5WQ/E0wVoK+pA6/3bup7bJf
CMGjwvxTsr74/f/F95m3TH9x8o0/TU//N+7/D/ScVcA=
""".encode('latin1')
    uncompressed = bytearray(zlib.decompress(base64.b64decode(font)))
    ttf = io.BytesIO(uncompressed)
    setattr(ttf, "name", "(invisible.ttf)")
    pdfmetrics.registerFont(TTFont('invisible', ttf))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a searchable PDF from a pile of hOCR and JPEG")
    parser.add_argument(
        "imgdir",
        help=("directory with the hOCR and JPEG files (corresponding "
              "JPEG and hOCR files have to have the same name with "
              "their respective file ending)")
    )
    parser.add_argument(
        "--savefile",
        help="Save to this file instead of outputting to stdout"
    )
    parser.add_argument('--limitsize', action='store_true', help='Restrict the dimensions of the PDF to standard sizes (e.g., A4, A3)')


    args = parser.parse_args()
    if not os.path.isdir(args.imgdir):
        sys.exit(f"ERROR: Given path '{args.imgdir}' is not a directory")
    
    export_pdf(args.imgdir, 150, args.savefile,args.limitsize)
