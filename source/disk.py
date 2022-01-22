import yadisk


def upload_to_yadisk(user_id, file_path):
    y = yadisk.YaDisk(token="disk_token")
    if not y.is_dir('/quotecreator/' + f'{user_id}'):
        y.mkdir('/quotecreator/' + f'{user_id}')
    y.upload(file_path, '/quotecreator/' + f'{user_id}/' +
             file_path.replace('output/', ''))
