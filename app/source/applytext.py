import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


def create_image(quote: str, pic: str):
    """Function to create image with text.

    Args:
        quote (str): text sent by the user.
        pic (list(str)): picture sent by the user.

    Returns:
        path (str): path to created image.

    """
    try:
        picture = Image.open(f"./photos/{pic}.jpg")
    except FileNotFoundError:
        return FileNotFoundError
    picture_edit = ImageDraw.Draw(picture)

    quote_font = ImageFont.truetype('source/OpenSans-Light.ttf', 100)
    # quote_font = ImageFont.load_default()
    width_picture, _ = picture.size
    lines = textwrap.wrap(quote, 20)

    height = 10
    for line in lines:
        width_text, height_text = quote_font.getsize(line)
        picture_edit.text(((width_picture-width_text)/2, height),
                          line, (237, 230, 211), font=quote_font)
        height += height_text

    path = f"./output/{pic}.jpg"
    picture.save(path)
    picture.close()
    os.remove(f"./photos/{pic}.jpg")

    return path
