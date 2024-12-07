from GeminiModule import GeminiModule
import pypandoc
import os
import uuid
import config
import json


gm = GeminiModule(config.proxy, config.gemini_token)

class FileWithDescription:
    def __init__(self, file_path, description):
        self.file_path = file_path
        self.description = description

def create_description(file_path, description) -> str:
    ''':returns путь к созданному файлу описания'''
    basename, extension = os.path.splitext(file_path)

    description_file_path = f"Files/{basename}.json" # Т.к. json мы не сохраняем, не добавляем к названию файла ничего лишнего
    #подсказки если че я пишу
    with open(description_file_path, "w") as f:
        json.dump({"description": description, "previous extension":f"{extension}"}, f)

    return description_file_path

def try_get_description(file_path) -> str | None:
    if not os.path.exists(file_path):
        return

    basename, extension = os.path.splitext(file_path)

    description_file_path = f"{basename.split("-")[0]}-{basename.split("-")[2]}.json"

    with open(f"{description_file_path}", "r") as f:
        description = json.load(f)

    return description

def try_search_files(query) -> list[FileWithDescription]:
    files = []

    for file in os.listdir("Files"):
        if query in file:
            files.append(FileWithDescription(f"Files\\{file}", try_get_description(f"Files\\{file}")))

    return files

def is_txt(file_path) -> bool:
    try:
        with open(file_path, "r") as f:
            f.readline()
            return True
    except:
        return False