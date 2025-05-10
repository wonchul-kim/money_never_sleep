import os
import os.path as osp
from dotenv import load_dotenv    
from youtube.utils.google_drive import GoogleDrive
from youtube.utils.youtube import get_youtube_video_data, extract_channel_id, get_videos_from_channel, arrange_title

load_dotenv('/HDD/github/youtube/.env')
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
YOUTUBE_SERVICE_ACCOUNT_FILE = os.getenv("YOUTUBE_SERVICE_ACCOUNT_FILE")

gdrive = GoogleDrive(YOUTUBE_SERVICE_ACCOUNT_FILE)

## 1 ==================================================================
# youtube_channel_name = '매일경제TV'
# url = "https://www.youtube.com/watch?v=GSqGXQP52GE"

# save_dir = '/HDD/etc'
# data = get_youtube_video_data(url, GOOGLE_CLOUD_API_KEY, save_dir)
# print(data)

# gdrive.upload('abcd', data, youtube_channel_name)


# ### 2 ==================================================================
# url = "https://www.youtube.com/@hkglobalmarket"
# channe_id = extract_channel_id(url, GOOGLE_CLOUD_API_KEY)
# print(channe_id)

# from datetime import datetime 
# published_after = datetime(2024, 3, 5, 15, 30).isoformat("T") + "Z"

# videos = get_videos_from_channel(url, GOOGLE_CLOUD_API_KEY)#, published_after)

# for video in videos:
#     data = get_youtube_video_data(video['url'], GOOGLE_CLOUD_API_KEY)
#     print(data)

### 3 ==================================================================
from youtube.utils.fileio import read_yaml

youtube_urls = read_yaml('/HDD/github/youtube/youtube/configs/youtube.yaml')
print(youtube_urls)

for channel_name, val in youtube_urls.items():
    url = val['url']
    channe_id = extract_channel_id(url, GOOGLE_CLOUD_API_KEY)
    print(channe_id)

    from datetime import datetime 
    published_after = datetime(2024, 3, 8, 00, 00).isoformat("T") + "Z"

    videos = get_videos_from_channel(url, GOOGLE_CLOUD_API_KEY, published_after)
    print(f"THere are {len(videos)} videos")
    
    for idx, video in enumerate(videos):
        video_data = get_youtube_video_data(video['url'], GOOGLE_CLOUD_API_KEY,
                                            save_dir='/HDD/etc/youtube/')
        published_at = video_data['publishedAt']
        year, month = published_at.split('-')[:2]
        day = published_at.split('-')[2].split("T")[0]
        title = arrange_title(video)
        folder_id = gdrive.create_folder(f'Youtube/{channel_name}/{year}/{month}/{day}')
        gdrive.upload(title, video_data, folder_id)
        print(idx, title)
