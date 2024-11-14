from lib import *

try:
    create_table()

    while True :
        print("----- 電影管理統 -----")
        print("1. 匯入電影資料檔")  #從 movies.json 檔案匯入電影資料進資料表。
        print("2. 查詢電影")        #可查詢全部電影或特定電影（根據電影名稱）
        print("3. 新增電影")        #年份與評分需確保格式正確
        print("4. 修改電影")        #若欄位沒有輸入新值代表維持原內容（根據電影名稱）
        print("5. 刪除電影")        #可以選擇刪除全部電影或特定電影（根據電影名稱）
        print("6. 匯出電影")        #可以選擇匯出全部電影或特定電影（根據電影名稱），匯出名稱為 exported.json
        print("7. 離開系統")
        print("-" * 22)

        choice = input("請選擇操作選項(1-7): ")

        if choice == "1":
            import_movies()
        elif choice == "2":
            search_movies()
        elif choice == "3":
            add_movie()
        elif choice == "4":
            modifly_movie()
        elif choice == "5":
            delete_movies()
        elif choice == "6":
            export_movies()
        elif choice == "7":
            print("感謝使用，再見！")
            break
        else:
            print("無效選項，請重新選擇。")

except Exception as e:
    print(f"發生錯誤:{e}")
finally:
    try:
        conn.commit()
        cursor.close()
        conn.close()
        print("資料庫連接已關閉")
    except Exception as e:
        print(f"關閉資料庫時發生錯誤:{str(e)}")