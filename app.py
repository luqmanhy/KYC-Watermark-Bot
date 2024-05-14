from flask import Flask, request, jsonify
import os
import sys
import math
import textwrap
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops, ImageOps
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_API_KEY')

def add_mark(image_path, mark, chat_id):
    '''
    Add watermark to the image and send it
    '''
    response = requests.get(image_path)

    im = Image.open(BytesIO(response.content))
    im = ImageOps.exif_transpose(im)
    image = mark(im)

    name = os.path.basename(image_path)
    if image:
        output = image_to_bytes(image)
        send_photo(chat_id, output, "")
        #print(name + " Success.")
    #else:
        #print(name + " Failed.")

def set_opacity(im, opacity):
    '''
    Set watermark opacity
    '''
    assert 0 <= opacity <= 1
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def crop_image(im):
    '''Crop empty edges of the image'''
    bg = Image.new(mode='RGBA', size=im.size)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    del bg
    if bbox:
        return im.crop(bbox)
    return im

def gen_mark(watermark_text):
    '''
    Generate watermark image and return a function to add watermark to other images
    '''
    mark = watermark_text
    size = 40
    font_height_crop = 1.2
    color = "#9C9C9C"
    opacity = 0.20
    space = 70
    angle = 30
    font_family = "./font.ttf"

    width = len(mark) * size
    height = int(size * font_height_crop)
    mark_image = Image.new(mode='RGBA', size=(width, height))
    draw = ImageDraw.Draw(mark_image)
    draw.text(xy=(0, 0), text=mark, fill=color, font=ImageFont.truetype(font_family, size=size))
    del draw
    mark_image = crop_image(mark_image)
    set_opacity(mark_image, opacity)

    def mark_im(im):
        c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))
        mark2 = Image.new(mode='RGBA', size=(c, c))
        y, idx = 0, 0
        while y < c:
            x = -int((mark_image.size[0] + space) * 0.5 * idx)
            idx = (idx + 1) % 2
            while x < c:
                mark2.paste(mark_image, (x, y))
                x = x + mark_image.size[0] + space
            y = y + mark_image.size[1] + space
        mark2 = mark2.rotate(angle)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        im.paste(mark2, (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)), mask=mark2.split()[3])
        del mark2
        return im

    return mark_im

def image_to_bytes(image):
    '''
    Convert image to byte array
    '''
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()

def send_photo(chat_id, photo_bytes, name):
    '''
    Send photo to Telegram chat
    '''
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {'photo': photo_bytes}
    payload = {'chat_id': chat_id, 'caption': name}
    response = requests.post(url, files=files, data=payload)
    return response.json()



def get_photo_url(photo_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
    params = {'file_id': photo_id}
    response = requests.get(url, params=params)
    data = response.json()
    file_path = data['result']['file_path']
    return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()


def delete_message(chat_id, message_id):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    response = requests.post(url, json=payload)
    return response.json()


@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        
        # Check if the message contains a photo
        if 'photo' in message:
            # Get the ID of the largest photo
            photo = message['photo'][-1]
            photo_id = photo['file_id']
            
            # Get the caption of the photo if any
            caption = message.get('caption', '')
            
            # Extract watermark text from the caption
            if caption.startswith('/wm'):
                watermark_text = caption.split('/wm', 1)[1].strip()
                
                # Get the URL of the photo
                photo_url = get_photo_url(photo_id)
                
                # Apply watermark to the photo
                mark = gen_mark(watermark_text)
                add_mark(photo_url, mark, chat_id)

                message_id = message['message_id']
            else:
                text = "Please send a photo with the caption '/wm [your_text]' to add a watermark."
                send_message(chat_id, text)
        else:
            text = "Please send a photo with the caption '/wm [your_text]' to add a watermark."
            send_message(chat_id, text)
            
        # Delete the original photo sent by the user
        if message_id:
            delete_message(chat_id, message_id)
            
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
