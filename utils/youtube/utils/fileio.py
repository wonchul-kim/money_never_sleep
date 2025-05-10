import yaml 

def read_yaml(yaml_file):
    with open(yaml_file, 'r') as yf:
        data = yaml.full_load(yf)
        
    return data

if __name__ == '__main__':
    data = read_yaml('/HDD/github/youtube/configs/google_drive.yaml')
    print(data)