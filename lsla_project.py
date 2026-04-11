import os
from directory_tree import DisplayTree
# pip install directory_tree


BASE_DIR = os.getcwd()
BLACKLIST = ["venv", ".git", ".idea", "__pycache__", "app"]
result = ''

def cat_using_open(file_path) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return content

def save_result(content) -> None:
    with open("result_file.txt", "w", encoding="utf-8") as file:
        file.write(content)


def cat_all_file() -> None:
    result = ''
    try:
        for dirpath, dirnames, filenames in list(os.walk(BASE_DIR)):
            if any(blacklist_item in dirpath for blacklist_item in BLACKLIST):
                continue
            for filename in filenames:
                if filename.split('.')[-1] not in ('bak', ) and filename not in ['requirements.txt', 'style.css']:
                    path_file = os.path.join(dirpath, filename)
                    result += '\n' + ('=' * 100) + '\n'
                    result += '\n' + path_file + '\n'
                    result += cat_using_open(path_file)
        save_result(result)
        return 'ok'
    except UnicodeDecodeError as e:
        print('error: ', e)



cat_all_file()
DisplayTree(BASE_DIR, ignoreList=BLACKLIST)
