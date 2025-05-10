from pathlib import Path 
ROOT = Path(__file__)
FILE = ROOT.resolve()
import os
import os.path as osp
from dotenv import load_dotenv    
from mns.utils.youtube import get_youtube_video_data, extract_channel_id, get_videos_from_channel, arrange_title
from mns.utils.helpers.fileio import read_yaml

load_dotenv('/HDD/github/youtube/.env')
YOUTUBE_SERVICE_ACCOUNT_FILE = os.getenv("YOUTUBE_SERVICE_ACCOUNT_FILE")
youtube_yaml_filename = osp.join(FILE, 'mns/configs/youtube.yaml')

youtube_urls = read_yaml(youtube_yaml_filename)
print(youtube_urls)

# for channel_name, val in youtube_urls.items():
#     url = val['url']
#     channe_id = extract_channel_id(url, GOOGLE_CLOUD_API_KEY)
#     print(channe_id)

#     from datetime import datetime 
#     published_after = datetime(2024, 3, 8, 00, 00).isoformat("T") + "Z"

#     videos = get_videos_from_channel(url, GOOGLE_CLOUD_API_KEY, published_after)
#     print(f"THere are {len(videos)} videos")
    
#     for idx, video in enumerate(videos):
#         video_data = get_youtube_video_data(video['url'], GOOGLE_CLOUD_API_KEY,
#                                             save_dir='/HDD/etc/youtube/')
#         published_at = video_data['publishedAt']
#         year, month = published_at.split('-')[:2]
#         day = published_at.split('-')[2].split("T")[0]
#         title = arrange_title(video)
#         folder_id = gdrive.create_folder(f'Youtube/{channel_name}/{year}/{month}/{day}')
#         gdrive.upload(title, video_data, folder_id)
#         print(idx, title)
