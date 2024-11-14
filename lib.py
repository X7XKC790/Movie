import sqlite3
import json

DB_PATH = 'movies.db'
JSON_IN_PATH = 'movies.json'
JSON_OUT_PATH = 'exported.json'

def connect_db():
    # 建立數據庫連接
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def list_rpt(movies):
    """顯示電影清單報表"""
    print("\n電影清單報表")
    print("-" * 90)
    print(f"{'編號':<6}{'電影名稱':<16}{'導演':<22}{'類型':<10}{'上映年份':<10}{'評分':<5}")
    print("-" * 90)

    for movie in movies:
        print(f"{movie['id']:<8}{movie['title']:{chr(12288)}<10}{movie['director']:{chr(12288)}<12}"
              f"{movie['genre']:<10}{movie['year']:<15}{movie['rating']:<5}")


def create_table():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS movies
            (id        INTEGER PRIMARY KEY AUTOINCREMENT,
             title     TEXT NOT NULL,
             director  TEXT NOT NULL,
             genre     TEXT NOT NULL,
             year      INTEGER NOT NULL,
             rating    REAL CHECK (rating >= 1.0 AND rating <= 10.0) )'''
    )
    conn.commit()
# 創建全局連接
conn, cursor = connect_db()

def import_movies(filename="movies.json"):
    data = []
    try:
        # 讀取 JSON 文件
        with open(filename, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        for movie in data:
            cursor.execute(
                '''INSERT INTO movies(title, director, genre, year, rating) VALUES (?, ?, ?, ?, ?)''',
                (movie['title'], movie['director'], movie['genre'], movie['year'], movie['rating'])
            )
        conn.commit()
        print("電影資料已成功匯入")
        return True

    except FileNotFoundError:
        print(f"錯誤:找不到文件{filename}")
    except json.JSONDecodeError:
        print(f"錯誤:無法解析 JSON 檔案{filename}")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"錯誤：數據導入失敗 - {str(e)}")
    except Exception as e:
        conn.rollback()
        print(f"錯誤:讀取檔案時發生未知錯誤{str(e)}")
    return False

def search_movies(title=None):
    """查詢電影"""
    try:
        # 新增使用者輸入部分
        if title is None:
            search_all = input("查詢全部電影嗎？(y/n): ").lower()
            if search_all != 'y':
                title = input("請輸入電影名稱: ")

        if title:
            cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{title}%',))
        else:
            cursor.execute('SELECT * FROM movies')

        movies = cursor.fetchall()

        if movies:
            print("\n查詢結果:")
            print("-" * 90)
            print(f"{'電影名稱':<20}{'導演':<25}{'類型':<10}{'年份':<10}{'評分':<5}")
            print("-" * 90)

            for movie in movies:
                print(f"{movie['title']:{chr(12288)}<10}{movie['director']:{chr(12288)}<12}"
                      f"{movie['genre']:<10}{movie['year']:<10}{movie['rating']:<5}")
        else:
            print("未找到符合條件的電影")
        return movies

    except sqlite3.Error as e:
        print(f"查詢錯誤:{str(e)}")
        return []

def add_movie():
    """新增電影"""
    try:
        title = input("電影名稱: ")
        director = input("導演名稱: ")
        genre = input("電影類型: ")
        year = int(input("年份(1900-2100): "))
        rating = float(input("評分(1.0-10.0): "))

        if year < 1900 or year > 2100:
            raise ValueError("年份必須在 1900-2100之間")

        if rating < 1.0 or rating > 10.0:
            raise ValueError("評分必須在 1.0-10.0 之間")

        cursor.execute(
            '''INSERT INTO movies(title, director, genre, year, rating)
            VALUES (?, ?, ?, ?, ?)''',
            (title, director, genre, year, rating))
        conn.commit()
        print("電影新增成功")

        # 顯示新增的電影資料
        print("\n新增的電影資料:")
        print(f"{'電影名稱':<10}{'導演':<20}{'類型':<10}{'年份':<10}{'評分':<5}")
        print("-" * 75)
        print(f"{title:<10}{director:<20}{genre:<10}{year:<10}{rating:<5}")

        return True
    except ValueError as e:
        print(f"資料格式錯誤: {str(e)}")
    except sqlite3.Error as e:
        print(f"新增錯誤: {str(e)}")
        return False

def modifly_movie():
    """修改電影資料"""
    title = input("請輸入要修改的電影名稱: ")

    cursor.execute('SELECT * FROM movies WHERE title = ?', (title,))
    movie = cursor.fetchone()

    if not movie:
        print("找不到指定的電影")
        return False

    print("\n電影名稱\t導演\t\t類型\t上映年份\t評分")
    print("-" * 60)
    print(f"{movie['title']}\t{movie['director']}\t{movie['genre']}\t{movie['year']}\t{movie['rating']}")
    print("-" * 60)

    new_data = {}

    new_title = input("請輸入新的電影名稱 (若不修改請直接按 Enter): ")
    if new_title:
        new_data['title'] = new_title

    new_director = input("請輸入新的導演名稱 (若不修改請直接按 Enter): ")
    if new_director:
        new_data['director'] = new_director

    new_genre = input("請輸入新的類型名稱 (若不修改請直接按 Enter): ")
    if new_genre:
        new_data['genre'] = new_genre

    new_year = input("請輸入新的上映年份 (若不修改請直接按 Enter): ")
    if new_year:
        new_data['year'] = int(new_year)

    new_rating = input("請輸入新的評分 (1.0 - 10.0) (若不修改請直接按 Enter): ")
    if new_rating:
        new_data['rating'] = float(new_rating)

    try:
        update_fields = []
        values = []
        for key, value in new_data.items():
            if value:
                update_fields.append(f"{key} = ?")
                values.append(value)

        if not update_fields:
            print("沒有需要更新的資料")
            return False

        values.append(title)
        update_sql = f"UPDATE movies SET {', '.join(update_fields)} WHERE title = ?"
        cursor.execute(update_sql, values)
        conn.commit()
        print("電影資料已更新")

        # 顯示更新後的電影資料
        print("\n更新的電影資料:")
        print(f"{'編號':<6}{'電影名稱':<12}{'導演':<20}{'類型':<10}{'上映年份':<10}{'評分':<5}")
        print("-" * 80)
        print(f"{movie['id']:<6}{new_data.get('title', movie['title']):<12}"
              f"{new_data.get('director', movie['director']):<20}"
              f"{new_data.get('genre', movie['genre']):<10}"
              f"{new_data.get('year', movie['year']):<10}"
              f"{new_data.get('rating', movie['rating']):<5}")

        return True

    except sqlite3.Error as e:
        print(f"更新錯誤:{str(e)}")
        return False

def delete_movies(title=None):
    """刪除電影
    Args:
        title: 電影名稱，若為 None 則刪除所有電影
    """
    try:
        if title:
            cursor.execute('DELETE FROM movies WHERE title = ?', (title,))
            if cursor.rowcount == 0:
                print("找不到指定的電影")
                return False
        else:
            confirm = input("確定要刪除所有電影嗎？(y/n): ").lower()
            if confirm != 'y':
                return False
            cursor.execute('DELETE FROM movies')

        conn.commit()
        print(f"已刪除 {cursor.rowcount} 筆電影資料")
        return True

    except sqlite3.Error as e:
        print(f"刪除錯誤：{str(e)}")
        return False

def export_movies(title=None, filename="exported.json"):
    """匯出電影資料
    Args:
        title: 電影名稱，若為 None 則匯出所有電影
        filename: 匯出的檔案名稱
    """
    try:
        if title:
            cursor.execute('SELECT * FROM movies WHERE title = ?',(title,))
        else:
            cursor.execute('SELECT * FROM movies')

        movies = cursor.fetchall()
        if not movies:
            print("沒有符合條件的電影可供匯出")
            return False

        movie_list = []
        for movie in movies:
            movie_dict = {
                'title': movie['title'],
                'director': movie['director'],
                'genre': movie['genre'],
                'year': movie['year'],
                'rating': movie['rating']
            }
            movie_list.append(movie_dict)

        with open(filename, 'w', encoding='UTF-8') as f:
            json.dump(movie_list, f, ensure_ascii=False, indent=2)

        print(f"已將 {len(movies)} 筆電影資料匯出至 {(filename)}")
        return True

    except Exception as e:
        print(f"會出錯誤: {str(e)}")
        return False