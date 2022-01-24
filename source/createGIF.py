import os
from typing import List

from imageio import imread, mimsave
from PIL import Image, ImageDraw, ImageFont


def create_GIF(name_id: str, data: List[str]):
    """Function to create gif out of photos.

    Args:
        name_id (str): name for created file.
        data (list(str)): list of file ids.

    Returns:
        path (str): path to created gif.

    """
    gif = []
    quote_font = ImageFont.truetype('source/OpenSans-Light.ttf', 35)

    picture = Image.open(f'./photos/{data[0]}.jpg').convert('RGBA')
    size = picture.size

    for file_id in data:
        picture = Image.open(f'./photos/{file_id}.jpg').convert('RGBA')
        os.remove(f'./photos/{file_id}.jpg')
        picture.thumbnail(size, Image.ANTIALIAS)
        txt = Image.new('RGBA', picture.size, (255, 255, 255, 0))

        picture_edit = ImageDraw.Draw(txt)
        picture_edit.text((15, 15), 'QC', (237, 230, 211), font=quote_font)

        watermarked = Image.alpha_composite(picture, txt)
        watermarked.save(f'./photos/{file_id}.png')
        picture.close()

        gif.append(imread(f'./photos/{file_id}.png'))
        os.remove(f'./photos/{file_id}.png')
    path = f'output/{name_id}.gif'
    mimsave(path, gif, duration=0.5)
    return path
