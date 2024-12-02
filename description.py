from GeminiModule import GeminiModule
import pypandoc
import os
import uuid
import config
import json


gm = GeminiModule(config.proxy, config.gemini_token)


def try_generate_description_for_file(file_path) -> str | None:
    basename, extension = os.path.splitext(file_path)

    if extension in config.convertable_to_pdf: #конвертируем в pdf если формат подерживается
        pypandoc.convert_file(file_path, 'pdf', outputfile=f"{basename}-converted-{uuid.uuid4()[:6]}.pdf")
        file_path = f"{basename}-converted-{uuid.uuid4()[:6]}.pdf"
        basename, extension = os.path.splitext(file_path)

    if extension not in config.allowed_extensions: #если формат не поддерживается, выходим
        return

    file_path = gm.upload_file(file_path) #загружаем файл в гугл и запоминаем
    answer = gm.generate(config.prompt, images=[file_path])
    file_path.delete() #после получении описания удаляем загруженный файл

    return answer

def create_description(file_path, description) -> str:
    ''':returns путь к созданному файлу описания'''
    basename, extension = os.path.splitext(file_path)

    description_file_path = f"{basename}.json" # Т.к. json мы не сохраняем, не добавляем к названию файла ничего лишнего
    #подсказки если че я пишу
    with open(description_file_path, "w") as f:
        json.dump({"description": description, "previous extension":f"{extension}"}, f)

    return description_file_path

def try_get_description(file_path) -> str | None:
    if not os.path.exists(file_path):
        return

    basename, extension = os.path.splitext(file_path)

    description_file_path = f"{basename}.json"

    with open(description_file_path, "r") as f:
        description = json.load(f)

    return description
