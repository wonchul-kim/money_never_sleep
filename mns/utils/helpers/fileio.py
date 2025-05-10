import yaml 
import requests

def read_yaml(yaml_file):
    with open(yaml_file, 'r') as yf:
        data = yaml.full_load(yf)
        
    return data

def get_image_url(client_id, image_filename):
    headers = {'Authorization': f'Client-ID {client_id}'}
    with open(image_filename, 'rb') as img:
        response = requests.post('https://api.imgur.com/3/image', headers=headers, files={'image': img})
        image_url = response.json()['data']['link']

    return image_url

if __name__ == '__main__':
    data = read_yaml('/HDD/github/youtube/configs/google_drive.yaml')
    print(data)