import os.path as osp
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_youtube_metadata(video_id, API_KEY):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet"
    response = requests.get(url)
    data = response.json()
    
    if "items" in data and len(data["items"]) > 0:
        snippet = data["items"][0]["snippet"]
        return snippet
    else:
        return None

def get_youtube_transcript(url):
    video_id = extract_video_id(url)
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
    
def get_youtube_video_data(url, api_key, save_dir=None):
    video_id = extract_video_id(url)
    
    data = get_youtube_metadata(video_id, api_key)
    data.update({"transcript": get_youtube_transcript(url)})

    title = arrange_title(data)
    
    if save_dir and osp.exists(save_dir):
        import json 
        with open(osp.join(save_dir, title + '.json'), "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print(f"Saved video data at {osp.join(save_dir, title + '.json')}")

    return data

def extract_channel_id(url, api_key):
    channel_url_name = url.split("/@")[-1]
    API_URL = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=@{channel_url_name}&key={api_key}"

    response = requests.get(API_URL)
    data = response.json()
    if "items" in data and data["items"]:
        return data["items"][0]["id"]
    return None


def get_videos_from_channel(url, api_key, published_after=None):
    
    channel_id = extract_channel_id(url, api_key)
    if published_after is not None:
        API_URL = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=5&type=video&publishedAfter={published_after}"
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
        API_URL = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=1"

        video = get_latest_video(API_URL)
        if video is None:
            return []
        else:
            return [{'title': video[0], 'url': video[1]}]

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

def arrange_title(data):
    
    title = data['title'].split("#")[:3]
    title = [item.strip() for item in title]
    title = ("_").join(title)
    
    return title