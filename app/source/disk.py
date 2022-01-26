import os

import yadisk

my_token = "disktoken"


def upload_to_yadisk(user_id: int, file_path: str, _type: str):
    """Function to upload created media to yadisk.

    Media is stored by the file type and user id.

    Args:
        user_id (int): id of a specific user.
        file_path (str): path to created media.
        _type (str): type of created media.

    """
    y = yadisk.YaDisk(token=my_token)
    if not y.is_dir('/quotecreator/' + f'{_type}'):
        y.mkdir('/quotecreator/' + f'{_type}')
    if not y.is_dir('/quotecreator/' + f'{_type}/' + f'{user_id}'):
        y.mkdir('/quotecreator/' + f'{_type}/' + f'{user_id}')
    try:
        y.upload(file_path, '/quotecreator/' + f'{_type}/' + f'{user_id}/' +
                 file_path.replace('output/', ''))
        os.remove(file_path)
    except yadisk.exceptions.ParentNotFoundError:
        return yadisk.exceptions.ParentNotFoundError


def get_user_GIFs(user_id: int):
    """Function to download gifs created by specific user from yadisk.

    Args:
        user_id (int): id of a specific user.

    Returns:
        list: urls to gifs

    """
    y = yadisk.YaDisk(token=my_token)
    files = []
    if y.is_dir(f"/quotecreator/gif_private/{user_id}/"):
        [files.append(f.file)
         for f in y.listdir(f"/quotecreator/gif_private/{user_id}")]
    if y.is_dir(f"/quotecreator/gif/{user_id}/"):
        [files.append(f.file)
         for f in y.listdir(f"/quotecreator/gif/{user_id}")]
    return files


def get_all_users_GIFs():
    """Function to download gifs created by all users from yadisk.

    Returns:
        list: urls to gifs

    """
    y = yadisk.YaDisk(token=my_token)
    folders = [f.name for f in y.listdir("/quotecreator/gif/")]
    files = []
    for folder in folders:
        [files.append(f.file)
         for f in y.listdir(f"/quotecreator/gif/{folder}")]
    return files
