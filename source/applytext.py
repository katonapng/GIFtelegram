import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


def create_image(quote: str, pic: str):
    """Function to create gif out of photos.

    Args:
        name_id (str): name for created file.
        data (list(str)): list of file ids.

    Returns:
        path (str): path to created gif.

    """
    picture = Image.open(f"./photos/{pic}.jpg")
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

    path = f"output/{pic}.jpg"
    picture.save(path)
    picture.close()
    os.remove(f"./photos/{pic}.jpg")

    return path
