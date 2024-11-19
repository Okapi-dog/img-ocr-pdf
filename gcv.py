import base64
import json
import requests

def detect_text(image_path, api_key):
  """
  画像からテキストを検出し、結果をJSONファイルに保存する関数

  Args:
    image_path: 画像ファイルのパス
    api_key: Google Cloud Vision APIのAPIキー
  """

  with open(image_path, "rb") as image_file:
    image_content = base64.b64encode(image_file.read()).decode('utf-8')

  request_body = {
    "requests": [
      {
        "image": {
          "content": image_content
        },
        "features": {
          "type": "TEXT_DETECTION",
          "maxResults": 2048
        },
        "imageContext": {
          "languageHints": "ja"
        }
      }
    ]
  }

  response = requests.post(
    url="https://vision.googleapis.com/v1/images:annotate?key={}".format(api_key),
    headers={"Content-Type": "application/json"},
    data=json.dumps(request_body)
  )

  # レスポンスをJSONファイルに保存
  output_file = image_path + ".json"
  with open(output_file, "w") as f:
    json.dump(response.json(), f, indent=2, ensure_ascii=False)

  print(f"結果は {output_file} に保存されました。")

# 使用例
if __name__ == "__main__":
  image_path = "path/to/your/image.jpg"  # 画像ファイルのパスに置き換えてください
  api_key = "YOUR_API_KEY"  # APIキーに置き換えてください
  detect_text(image_path, api_key)