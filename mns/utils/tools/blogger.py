import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery
import os.path as osp
import os
from dotenv import load_dotenv    

from mns.utils.helpers.fileio import get_image_url

from pathlib import Path 
ROOT = Path(__file__).resolve()
FILE = ROOT.parents[2]


class Blogger:
    def __init__(self, env_filename=osp.join(FILE, 'configs/.env'),
                 client_secret_filename=osp.join(FILE, 'configs/client_secret.json'),
                 verbose=True):
        
        assert osp.exists(env_filename), RuntimeError(f'There is no such file: {env_filename}')
        
        if not load_dotenv(env_filename):
            raise RuntimeError(f"CANNOT load env file: {env_filename}")
        
        self._blogger_id = os.getenv("BLOGGER_ID")

        self._service = None
        self.verbose = verbose
        self.set_blogger_service(client_secret_filename)

    @property
    def blogger_id(self):
        return self._blogger_id

    @property
    def service(self):
        return self._service

    def set_blogger_service(self, client_secret_filename):
        
        def authorize_credentials(client_secret_filename):
            SCOPE = 'https://www.googleapis.com/auth/blogger'
            STORAGE = Storage(osp.join(FILE, 'configs/credentials.storage'))
            credentials = STORAGE.get()
            if credentials is None or credentials.invalid:
                if self.verbose:
                    print(f"There is no valid credential, so need to get it from client_secret")
                flow = flow_from_clientsecrets(client_secret_filename, scope=SCOPE)
                http = httplib2.Http()
                credentials = run_flow(flow, STORAGE, http=http)
        
            return credentials

        credentials = authorize_credentials(client_secret_filename)
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://blogger.googleapis.com/$discovery/rest?version=v3')
        self._service = discovery.build('blogger', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
        if self.verbose:
            print(f"READY 'service' to bost into blog!")
        
    def post(self, body, is_draft=False):
        if self._service is None:
            self.set_blogger_service()
            
        post = self._service.posts()
        insert = post.insert(blogId=self._blogger_id, body=body, isDraft=is_draft).execute()
        print("Done post!")
        return insert


    def test(self):

        image_url = get_image_url(client_id="b5fc22a1c8f7873", 
                                  image_filename="/HDD/test/dog.jpg")

        title = "Testing post" 
        content = f"""
                    <h1> h1: This is test to post by python </h1>
                    <h2> h2: This is test to post by python </h2>
                    
                    <p> p: This is test to post by python </p>
                    <img src="{image_url}" alt="sample image" width="400">
                    
                   """

        customMetaData = "This is meta data"
        body = {
                "title": title,
                "content": content,
                'labels': ['label1','label2'],
                'customMetaData': customMetaData
            }
        
        self.post(body)
        
if __name__ == '__main__':
        
    blogger = Blogger()
    blogger.test()
    
