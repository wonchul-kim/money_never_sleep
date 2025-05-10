import os
from dotenv import load_dotenv    
from youtube.utils.google_drive import GoogleDrive

load_dotenv('/HDD/github/youtube/.env')
YOUTUBE_SERVICE_ACCOUNT_FILE = os.getenv("YOUTUBE_SERVICE_ACCOUNT_FILE")


gdrive = GoogleDrive(YOUTUBE_SERVICE_ACCOUNT_FILE)
### 1 ===================================================================
folder_id = gdrive.get_folder_id('한경 글로벌마켓')
print("📂 찾은 폴더 ID:", folder_id)
gdrive.delete_file('한경 글로벌마켓')
folder_id = gdrive.get_folder_id('한경 글로벌마켓')
print("📂 찾은 폴더 ID:", folder_id)

# ### 2 ===================================================================
# folder_id = gdrive.get_folder_id('Youtube')
# # gdrive.create_folder('한경 글로벌마켓', folder_id)
# gdrive.create_folder('매일경제TV', folder_id)

# ## 3 ===================================================================
dirs = 'Youtube/매일경제TV/2025/03/09'
dirs = dirs.split("/")
for idx, _dir in enumerate(dirs):
    folder_id = gdrive.get_folder_id(_dir)
    if folder_id is None:
        if idx != 0:
            gdrive.create_folder(_dir, gdrive.get_folder_id(dirs[idx - 1]))
        else:
            gdrive.create_folder(_dir)
# folder_id = gdrive.get_folder_id("매일경제TV", youtube_folder_id)
# print('folder: ', folder_id)

# if youtube_folder_id:
#     # 2️⃣ Youtube 폴더 아래 "매일경제TV/2025" 생성
#     final_folder_id = gdrive.get_or_create_folder_by_path("매일경제TV/2025", youtube_folder_id)
#     print(f"📂 최종 폴더 ID: {final_folder_id}")
# else:
#     print("❌ 'Youtube' 폴더를 찾을 수 없습니다.")
