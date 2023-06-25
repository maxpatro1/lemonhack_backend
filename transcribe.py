import whisper
import os
import cv2
import hashlib

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pytube import YouTube
import redis
import json
from moviepy.editor import *

from article_creation import crate_annotation, create_titles
from formatters import format_item, format_titles

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html'])
)
template = env.get_template('article.html')


def saveData(url, data):
    redis.set(url, data)


def checkCache(url):
    return redis.get(url)


def render(article):
    return template.render(article)


def download_video(url, start_time=None, end_time=None):
    print("Start downloading", url)
    yt = YouTube(url)

    hash_file = hashlib.md5()
    hash_file.update(yt.title.encode())

    file_name = f'{hash_file.hexdigest()}.mp4'

    yt.streams.filter(res='720p').first().download("", file_name)
    if start_time and end_time:
        video = VideoFileClip(file_name).subclip(start_time, end_time)
        video.write_videofile("myHolidays_edited.webm", fps=25)
    print("Downloaded to", file_name)

    return {
        "file_name": file_name,
        "title": yt.title
    }


model_name = "base"
model = whisper.load_model(model_name)


def extract_features(file_name, timing):
    video_name = file_name.split('.mp4')[0]
    cap = cv2.VideoCapture(file_name)
    cap.set(cv2.CAP_PROP_POS_MSEC, timing * 1000)
    ret, frame = cap.read()
    if not os.path.exists(f'data/{video_name}'):
        os.mkdir(f'data/{video_name}')
    if ret:
        # Сохранить кадр в файл
        cv2.imwrite(f'data/{video_name}/{timing}.jpg', frame)
        # print('Скриншот создан')
    else:
        print('Не удалось прочитать кадр из видеофайла')

    # Освободить ресурсы
    cap.release()
    cv2.destroyAllWindows()
    return f'data/{video_name}/{timing}.jpg'


def transcribe(url, start_time=None, end_time=None, max_symbols=None):
    if checkCache(url):
        # article = json.loads(checkCache(url))
        # print(article['segments'])
        # print(template.render(article = article))
        return json.loads(checkCache(url))
    video = download_video(url)
    result = model.transcribe(video["file_name"], fp16=False)

    segments = []
    text = ''
    print('Создание скриншотов')
    for item in result["segments"]:
        # print(item)
        text += item['text']
        img = extract_features(video['file_name'], item['start'])
        segments.append(format_item(item, img))
    os.remove(video["file_name"])
    formatted_text = create_titles(text)
    annotation = crate_annotation(text)
    article = create_article(segments, formatted_text)
    dict_str = json.dumps({
        'title': video['title'],
        'annotation': annotation,
        'segments': article,
        'uuid': video['file_name']
    })
    saveData(url, dict_str)
    return {
        'title': video['title'],
        'annotation': annotation,
        'segments': article,
        'uuid': video['file_name']
    }


def create_article(segments, formatted_text):
    segments = segments
    print(segments)
    text = formatted_text
    text_arr = text.split('#')
    result = []

    for paragraph in text_arr:
        timing_arr = []
        img_arr = []
        for segment in segments:
            if segment['text'].strip() in paragraph.strip().replace('\n', ''):
                timing_arr.append(str(segment['time']))
                img_arr.append(str(segment['img']))
        if len(timing_arr) > 0:
            result.append(format_titles(paragraph, timing_arr, img_arr))

    return result


def generate_html(url):
    if checkCache(url):
        article = json.loads(checkCache(url))
        html_content = template.render(article=article)
        file_path = 'index.html'
        print_html_to_file(html_content, file_path)
        return file_path


def print_html_to_file(html_content, file_path):
    with open(file_path, "w") as file:
        file.write(html_content)


print(transcribe('https://www.youtube.com/watch?v=TpIrJmVwfBo'))
