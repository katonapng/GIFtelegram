# QuoteCreator bot
QuoteCreator is a bot to create images with text and gifs.

Go to https://t.me/QuoteCreatorBot to try it!

Command list:
- /start - begin interaction
- /help - get all available requests
- /quote - create a picture out of given image and text
- /gif - create a gif out of given image or album (can be public or private)
- /getgif - get created gifs (all public gifs or all personal gifs including private ones)
- /cancel - cancel any operation except quote typing

To run this application you should first add a  bot token.
To receive this token proceed to @BotFather and create a bot.
Insert bot token in line token = "token" in quotecreator.py file.
You also need to create a yandex disk and get a OAuth-token.
To do so visit this website https://yandex.ru/dev/disk/rest/.
Insert disk token in line my_token = "disktoken" in disk.py file.



If you have Docker installed on your computer you can run a 'docker-compose up --build' in directory containing docker-compose.yaml file. 

Your application should be running now, go to your bot and strike a conversation.

P.S.
You can open project in any code-editor you like. 
Keep in mind, if you're not using Docker you need to install libraries in requirements.txt file.