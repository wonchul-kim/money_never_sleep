import os.path as osp
import re
import requests
import json
from PIL import Image 
from io import BytesIO
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from pathlib import Path 
ROOT = Path(__file__).resolve()
FILE = ROOT.parents[2]

class Youtube:
    def __init__(self, env_filename=osp.join(FILE, 'configs/.env'),
                 verbose=True):
        
        assert osp.exists(env_filename), RuntimeError(f'There is no such file: {env_filename}')
        
        if not load_dotenv(env_filename):
            raise RuntimeError(f"CANNOT load env file: {env_filename}")
        
        self._google_cloud_api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        YOUTUBE_SERVICE_ACCOUNT_FILE = os.getenv("YOUTUBE_SERVICE_ACCOUNT_FILE")
        self.verbose = verbose

    def extract_channel_id(self, url):
        '''
            In order to get channel-id from custom url including "/@channel-name" or :/c/channel-name",
            Need to use YouTube Data API v3(https://developers.google.com/youtube/v3/docs/channels/list)
            
            It requires google cloud console API key.
        '''
        channel_url_name = url.split("/@")[-1]
        API_URL = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=@{channel_url_name}&key={self._google_cloud_api_key}"

        response = requests.get(API_URL)
        data = response.json()
        if "items" in data and data["items"]:
            return data["items"][0]["id"]
        
        return None

    def get_videos_from_channel(self, url, published_after=None):
        
        channel_id = self.extract_channel_id(url)
        if published_after is not None:
            API_URL = f"https://www.googleapis.com/youtube/v3/search?key={self._google_cloud_api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=5&type=video&publishedAfter={published_after}"
            response = requests.get(API_URL)
            data = response.json()

            videos = []
            if "items" in data:
                for item in data["items"]:
                    video_id = item["id"]["videoId"]
                    video_title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    videos.append({'title': video_title, 'url': video_url})
                    
            return videos
        else:
            API_URL = f"https://www.googleapis.com/youtube/v3/search?key={self._google_cloud_api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=1"

            video = get_latest_video(API_URL)
            if video is None:
                return []
            else:
                return [{'title': video[0], 'url': video[1]}]


    def get_info_from_video(self, video, save_dir=None):
        title, url = video['title'], video['url']
        video_id = self.extract_video_id(url)
        info = self.get_youtube_metadata(video_id)
        transcript = self.get_youtube_transcript(url)
        info.update({"transcript": transcript})

        if save_dir and osp.exists(save_dir):
            thumbnail = self.get_thumbnail(info['thumbnails']['standard']['url'])
            published_at = info['publishedAt']
            year, month = published_at.split('-')[:2]
            day = published_at.split('-')[2].split("T")[0]
            title = self.arrange_title(title)

            _save_dir = osp.join(save_dir, title)
            if not osp.exists(_save_dir):
                os.mkdir(_save_dir)
                
            with open(osp.join(_save_dir, title + '.json'), "w", encoding="utf-8") as file:
                json.dump(info, file, ensure_ascii=False, indent=4)

            if thumbnail:
                thumbnail.save(osp.join(_save_dir, 'thumbnail.png'))
            
            if self.verbose:
                print(f"Saved video info at {osp.join(_save_dir, title + '.json')}")

        return info
    
    def get_thumbnail(self, url):
        response = requests.get(url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
        else:
            return None

    def arrange_title(self, title):
        
        title = title.split("#")[:3]
        title = [item.strip() for item in title]
        title = ("_").join(title)
        
        return title

    def get_youtube_metadata(self, video_id):
        '''
            meta-data: 'publishedAt', 'channelId', 'title', 'description', 
                       'thumbnails', 'channelTitle', 'tags', 'categoryId', 
                       'liveBroadcastContent', 'defaultLanguage', 'localized', 
                       'defaultAudioLanguage', 'transcript'
        '''
        
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={self._google_cloud_api_key}&part=snippet"
        response = requests.get(url)
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            snippet = data["items"][0]["snippet"]
            return snippet
        else:
            return None
    
    def get_youtube_transcript(self, url):
        video_id = self.extract_video_id(url)
        if not video_id:
            print("❌ 유효한 유튜브 URL이 아닙니다.")
            return None

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            formatter = TextFormatter()
            script_text = formatter.format_transcript(transcript)
            return script_text
        except Exception as e:
            print(f"❌ 자막을 가져오는 데 실패했습니다: {e}")
            return None
        

    def extract_video_id(self, url):
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        return match.group(1) if match else None




def get_latest_video(url):
    response = requests.get(url)
    data = response.json()

    if "items" in data:
        latest_video = data["items"][0]
        video_id = latest_video["id"]["videoId"]
        video_title = latest_video["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        return video_title, video_url
    
    return None



if __name__ == '__main__':

    import os
    import os.path as osp
    from dotenv import load_dotenv    
    from mns.utils.helpers.fileio import read_yaml

    youtube = Youtube()
    youtube_yaml_filename=osp.join(FILE, 'configs/youtube.yaml')
    youtube_urls = read_yaml(youtube_yaml_filename)
    print("youtue urls: ")
    for key, val in youtube_urls.items():
        print(f"{key}: {val}")

    for channel_name, val in youtube_urls.items():
        url = val['url']

        from datetime import datetime 
        published_after = datetime(2024, 5, 10, 00, 00).isoformat("T") + "Z"

        videos = youtube.get_videos_from_channel(url, published_after)
        print(f"There are {len(videos)} videos")
        
        for idx, video in enumerate(videos):
            video_data = youtube.get_info_from_video(video,
                                                save_dir='/HDD/etc/youtube/')

