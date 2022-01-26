# syntax=docker/dockerfile:1
FROM python
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD python ./source/bot.py
