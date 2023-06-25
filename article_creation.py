import time

from spellchecker import SpellChecker
import openai

openai.api_key = "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"


def split_text(text, max_length):
    fragments = []
    current_fragment = ""
    words = text.split()

    for word in words:
        if len(current_fragment) + len(word) <= max_length:
            current_fragment += " " + word
        else:
            fragments.append(current_fragment.strip())
            current_fragment = word

    if current_fragment:
        fragments.append(current_fragment.strip())

    return fragments


def correct_spelling(text):
    spell = SpellChecker(language='ru')
    words = text.split()
    corrected_words = []
    for word in words:
        corrected_word = spell.correction(word)
        if corrected_word is not None:
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    corrected_text = ' '.join(corrected_words)
    return corrected_text


def create_titles(text):
    print('Создание абзацов')
    fragments = split_text(text, 700)
    result = ''
    # Обрабатываем каждый фрагмент
    for fragment in fragments:
        query_text = f"Разбей статью на абзацы, не изменяя текст, придумай названия абзацам, добавь названия " \
                     f"абзацов в текст, не изменяя текст" \
                     f"названия абзацов," \
                     f"должны начинаться с #*, сам текст cтатьи меняться не должен!!! " \
                     f"- {fragment} "

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query_text}],
            max_tokens=1024,
            temperature=0.8)
        result += completion.choices[0].message.content
        time.sleep(10)
    # correct_result = correct_spelling(result)
    return result


def crate_annotation(text):
    print('Создание аннотации')
    result = ''
    query_text = f"Напиши короткую аннотацию к статье - {text[0:1000]} "
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query_text}],
        max_tokens=1024,
        temperature=0.8)
    result += completion.choices[0].message.content
    return result
