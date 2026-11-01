import json
import os

DATA_FILE = "data.json"
ALLOWED_FORMATS = ["jpg", "jpeg", "png", "webp"]

def load_data():
    if not (os.path.exists(DATA_FILE)):
        return{
            "Comic": [],
            "Author": [],
            "Comic_Author": [],
            "Chapter": [],
            "File": [],
            "Moderation": [],
            "Statistics": []
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            tables = ["Comic", "Author", "Comic_Author", 
                    "Chapter", "File", "Moderation", "Statistics"]
            for table in tables:
                if table not in data:
                    data[table] = []
            return data
    except (json.JSONDecodeError, OSError):
        print("Ошибка чтения файла")
        return None


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except OSError:
        print("Ошибка при сохранении файла")
        return False

def get_next_id(records, field):
    if not records:
        return 1
    return max(record[field] for record in records)+1

def find_comic_by_title(data, title):
    for comic in data["Comic"]:
        if comic["title"].strip().lower() == title.strip().lower():
            return comic
    return None


def register_comic(data):
    print("Регистрация нового комикса")
    title = input("Введите название комикса: ").strip()
    genre = input("Введите жанр комикса: ").strip()
    decript = input("Введите описание комикса: ").strip()

    if not title or not genre or not decript:
        print("Ошибка: необходимо ввести все данные")
        return False
    if find_comic_by_title(data, title):
        print("Ошибка: комикс с таким названием уже зарегистрирован")
        return False
    try:
        authors_count = int(input("Введите количество авторов: "))
        if authors_count <= 0:
            print("Ошибка: число авторов должно быть больше 0")
            return False
    except ValueError:
        print("Ошибка: необходимо ввести целое число")
        return False

    authors = []
    for i in range(authors_count):
        print(f"Введите данные автора №{i+1}")
        name = input("Введите имя или псевдоним автора: ").strip()
        email = input("Введите адрес электронной почты: ").strip()
        if not name or not email:
            print("Ошибка: необходимо ввести все данные")
            return False
        authors.append({
            "name": name,
            "email": email
        })
    comic_id = get_next_id(data["Comic"], "comic_id")
    comic = {
        "comic_id": comic_id,
        "title": title,
        "genre": genre,
        "description": decript,
        "status": "Ожидает модерации"
    }

    data["Comic"].append(comic)
    author_id = get_next_id(data["Author"], "author_id")

    for author_data in authors:
        author = {
            "author_id": author_id,
            "name": author_data["name"],
            "email": author_data["email"]
        }
        data["Author"].append(author)
        comic_author = {
            "comic_id": comic_id,
            "author_id": author_id
        }
        data["Comic_Author"].append(comic_author)
        author_id += 1
    print("Комикс успешно зарегистрирован")
    return True


def add_new_chapter(data):
    print("Добавление новой главы")
    comic_title = input("Введите название комикса: ").strip()
    comic = find_comic_by_title(data, comic_title)
    if comic is None:
        print("Ошибка: комикс не найден")
        return False
    
    chapter_title = input("Введите название главы: ").strip()
    if not chapter_title:
        print("Ошибка: не введено название главы")
        return False
    try:
            chapter_number = int(input("Введите порядковый номер: "))
            if chapter_number < 0:
                print("Ошибка: номер главы должен быть положительным")
                return False
    except ValueError:
            print("Ошибка: необходимо ввести целое число")
            return False
        
    for chapter in data["Chapter"]:
        if chapter["comic_id"] == comic["comic_id"] and chapter["chapter_number"] == chapter_number:
            print("Ошибка: глава с таким номером уже существует")
            return False
    
    try:
        files_count = int(input("Введите количество файлов: "))
        if files_count <= 0:
            print("Ошибка: число файлов должно быть больше 0")
            return False
    except ValueError:
        print("Ошибка: необходимо ввести целое число")
        return False
        
    files = []
    for i in range(files_count):
        print(f"Файл №{i+1}")
        name = input("Введите имя файла с расширением: ").strip()
        
        if not name or "." not in name:
            print("Ошибка: некорректное имя файла")
            return False
        
        file_format = name.rsplit(".", 1)[1].lower()
        if file_format not in ALLOWED_FORMATS:
            print("Ошибка: некорректный формат файла")
            print("Допустимые форматы:", ", ".join(ALLOWED_FORMATS))
            return False
        
        try:
            file_size = float(input("Введите размер файла в КБ: "))
            if file_size <= 0:
                print("Ошибка: размер файлов должен быть больше 0")
                return False
        except ValueError:
            print("Ошибка: необходимо ввести число")
            return False
        
        files.append({
            "file_name": name,
            "format": file_format,
            "file_size": file_size
        })
    chapter_id = get_next_id(data["Chapter"], "chapter_id")
    chapter = {
        "chapter_id": chapter_id,
        "comic_id": comic["comic_id"],
        "title": chapter_title,
        "chapter_number": chapter_number,
        "status": "Ожидает модерации"
    }
    
    data["Chapter"].append(chapter)
    
    for file in files:
        file_record = {
            "file_id": get_next_id(data["File"], "file_id"),
            "chapter_id": chapter_id,
            "format": file["format"],
            "file_name": file["file_name"],
            "file_size": file["file_size"]
        }
        
        data["File"].append(file_record)
        
    print("Глава успешно добавлена")
    return True


def moderate_comic(data):
    print("Модерация комикса")
    comic_title = input("Введите название комикса: ").strip()
    comic = find_comic_by_title(data, comic_title)
    if comic is None:
        print("Ошибка: комикс не найден")
        return False
    moder_name = input("Введите имя модератора: ").strip()
    if not moder_name:
        print("Ошибка: не введено имя модератора")
        return False
        
    print("Результат проверки:")
    print("1. Одобрить комикс")
    print("2. Отправить комикс на доработку")
    
    choice = input("Выберите результат модерации: ").strip()
    
    if choice == "1":
        result = "Одобрено"
        comic["status"] = "Опубликован"
    elif choice == "2":
        result = "На доработке"
        comic["status"] = result
    else:
        print("Ошибка: неверный вариант")
        return False
    comment = input("Введите комментарий модератора: ").strip()
    
    moderation = {
        "moderation_id": get_next_id(data["Moderation"], "moderation_id"),
        "comic_id": comic["comic_id"],
        "moderator_name": moder_name,
        "result": result,
        "comment": comment
    }
    
    data["Moderation"].append(moderation)
    print("Модерация успешно завершена")
    print("Текущий статус комикса:", comic["status"])
    return True
        
        
def update_statistics(data):
    print("Обновление статистики")
    comic_title = input("Введите название комикса: ").strip()
    comic = find_comic_by_title(data, comic_title)
    if comic is None:
        print("Ошибка: комикс не найден")
        return False
    
    print("Выберите тип действия: ")
    print("1. Просмотр")
    print("2. Отметка «Нравится»")
    print("3. Добавление комментария")
    
    choice = input("Введите номер действия: ").strip()
    if choice not in ["1", "2", "3"]:
        print("Ошибка: неверный вариант действия")
        return False
    
    statistics = None
    for record in data["Statistics"]:
        if record["comic_id"] == comic["comic_id"]:
            statistics = record
            break
        
    if statistics is None:
        statistics = {
            "statistics_id": get_next_id(data["Statistics"], "statistics_id"),
            "comic_id": comic["comic_id"],
            "views": 0,
            "likes": 0,
            "comments_count": 0
        }
        data["Statistics"].append(statistics)
        
    if choice == "1":
        statistics["views"] += 1
        print("Число просмотров увеличено")
    elif choice == "2":
        statistics["likes"] += 1
        print("Количество отметок «Нравится» увеличено")
    elif choice == "3":
        statistics["comments_count"] += 1
        print("Количество комментариев увеличено")
        
    print("Текущая статистика комикса:")
    print("Просмотры:", statistics["views"])
    print("Отметки «Нравится»:", statistics["likes"])
    print("Комментарии:", statistics["comments_count"])

    return True

def show_comics(data):
    print("Полный список комиксов")
    if not data["Comic"]:
        print("Зарегистрированные комиксы отсутствуют")
        return 
    for comic in data["Comic"]:
        print(
            f'Название: {comic["title"]} | '
            f'Жанр: {comic["genre"]} | '
            f'Статус: {comic["status"]}'
        )


def main():
    data = load_data()
    if data is None:
        return 
    
    while True:
        print("1. Регистрация нового комикса")
        print("2. Добавление новой главы")
        print("3. Модерация и публикация комикса")
        print("4. Сбор и обновление статистики")
        print("5. Просмотр списка комиксов")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        result = False
        if choice == "1":
            result = register_comic(data)       
        elif choice == "2":
            result = add_new_chapter(data)
        elif choice == "3":
            result = moderate_comic(data)
        elif choice == "4":
            result = update_statistics(data)
        elif choice == "5":
            show_comics(data)
        elif choice == "0":
            save_data(data)
            print("Работа программы завершена.")
            break
        else:
            print("Ошибка: выберите пункт из меню.")
            continue
        
        if result:
            save_data(data)


if __name__ == "__main__":
    main()
        