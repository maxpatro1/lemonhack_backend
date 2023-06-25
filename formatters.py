def format_item(item, img=''):
    return {
        "time": item["start"],
        "text": item["text"],
        "img": img
    }


def format_titles(text, time, img):
    return {
        'time': time,
        'text': text,
        'img': img
    }
