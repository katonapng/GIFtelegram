import textwrap

from PIL import Image, ImageDraw, ImageFont


def create_image(data):
    quote = data['quote']
    picture = Image.open(f"./photos/{data['picture']}.jpg")
    picture_edit = ImageDraw.Draw(picture)

    quote_font = ImageFont.truetype('source/OpenSans-Light.ttf', 100)
    width_picture, _ = picture.size
    lines = textwrap.wrap(quote, 20)

    height = 10
    for line in lines:
        width_text, height_text = quote_font.getsize(line)
        picture_edit.text(((width_picture-width_text)/2, height),
                          line, (237, 230, 211), font=quote_font)
        height += height_text

    path = f"output/{data['picture']}.jpg"
    picture.save(path)
    return path
