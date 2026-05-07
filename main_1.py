import requests,re,os
from bs4 import BeautifulSoup
from pathlib import Path
import random
import datetime
from opencc import OpenCC
import cloudinary
import cloudinary.uploader
#
# ##cloudinary 雲端 設定--begin
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)
# ##cloudinary 雲端 設定--end
#
#
#
# # 取得每日早安問候句--begin
# #1.取得百日問候語
url = 'https://www.diyifanwen.com/tool/youmeijuzi/685168.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
html = requests.get(url,headers = headers)
print(html)
html.encoding = html.apparent_encoding#修正簡體亂碼日
bs = BeautifulSoup(html.text, 'lxml')
content = bs.select('div.content p')
# print(content)
trash = "0123456789.、 "
content_txt = [x.text.strip().lstrip(trash) for x in content if x.text.strip()]
# print(content_txt)
# #
# # 2簡體轉繁體
cc = OpenCC('s2t')
content_tradition = [cc.convert(x) for x in content_txt]
# # for m in content_tradition:
# #     print(m)
# #3 . 產生當日訊息
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
message_text = random.choice(content_tradition[5:]) + "\n" + f"🌞 早安！今天是 {today}"
print(message_text)
# # 取得每日早安問候句--end
#
#
#
# ##-----下載圖片--begin
url="https://sticker.fpg.com.tw/sticker.aspx?sticker_id=200000602"
res=requests.get(url)
soup=BeautifulSoup(res.text,'lxml')
img_list=soup.find_all('img')
# print(img_list)
pattern=re.compile(r'.+\.jpg$',re.IGNORECASE)
img_set = set()
# #
for x in img_list:
    src = x.get('data-original', '')
    if pattern.match(src):
        # 如果不是 http 開頭，就補上完整網址
        if not src.startswith('http'):
            src = 'https://sticker.fpg.com.tw/' + src
        img_set.add(src)
img_list_final=sorted(list(img_set))
img_list_final = img_list_final[10:51]
print(f"共找到 {len(img_set)} 張圖片，準備下載前 {len(img_list_final)} 張。")
# #
for x in img_list_final:
    print("ok",x)
dir_name = 'data'
if not os.path.exists(dir_name):
    os.mkdir(dir_name)
for i, x in enumerate(img_list_final):
    content = requests.get(x).content
    file_name = f'{dir_name}/img{i}.jpg'
    with open(file_name, 'wb') as fwb:
        fwb.write(content)
print(f"共下載 {len(img_list_final)} 張圖片")
# ##-----下載圖片--end
#
#
#
# ###上傳圖片到 cloudinary --begin
# # 1.搜尋資料夾內有無.jpg的圖檔 glob('*.jpg)
image_files=[]
try:
    image_files = list(Path("data").glob("*.jpg"))
    if not image_files:
        raise FileNotFoundError
except FileNotFoundError:
    print(" 沒有找到 data 資料夾中的 JPG 圖片。請放入至少一張。")
#
selected_image = random.choice(image_files)
print(f"選中的圖片: {selected_image.name}")
#
# # 2.上傳圖片到 Cloudinary ----
def upload_to_cloudinary(image_path):
    try:
        result = cloudinary.uploader.upload(str(image_path))
        img_url = result["secure_url"]
        print(f"圖片上傳成功：{img_url}")
        return img_url
    except Exception as e:
        raise Exception(f" Cloudinary 上傳失敗: {e}")
#
print("上傳圖片到 Cloudinary 中...")
cloud_url = upload_to_cloudinary(selected_image)
print("網址為:",cloud_url)
# '''
# {
# result：這是重點！上傳成功後，Cloudinary 會回傳一個「字典（Dictionary）」
# 格式的資料夾，裡面包含了這張圖片在雲端的所有資訊（例如：檔案大小、解析度、
# 上傳時間，以及最重要的——網址）。
#     "public_id": "sample_id",
#     "width": 800,
#     "height": 600,
#     "format": "jpg",
#     "url": "http://res.cloudinary.com/demo/image/upload/sample.jpg",
#     "secure_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
#     ...
# }
# '''
# ###上傳圖片到 cloudinary --end


## line 發送訊息設定--begin

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# USER_ID = "Uf51ffd305ce026921198cca620f8b554"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

# 廣播模式
payload = {
    "messages": [
        {
            "type": "text",
            "text": message_text
        },
        {
            "type": "image",
            "originalContentUrl": cloud_url,
            "previewImageUrl": cloud_url
        }
    ]
}

print("傳送廣播訊息到 LINE 所有好友...")
# broadcast網址
broadcast_url = "https://api.line.me/v2/bot/message/broadcast"
print(payload)
res = requests.post(broadcast_url, headers=headers, json=payload)
print("LINE 傳送結果:", res.status_code, res.text)
## line 發送訊息設定--end
