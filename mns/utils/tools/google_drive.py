import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload


class GoogleDrive:
    def __init__(self, service_account_file, 
                 scopes=["https://www.googleapis.com/auth/drive.metadata.readonly",
                         "https://www.googleapis.com/auth/drive.file"]):
        
        creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        self.gdrive = build("drive", "v3", credentials=creds)
            
    def get_folder_id(self, folder_name, parent_folder_id=None):
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"

        # print(f"📌 Query: {query}")  # 쿼리 출력해서 확인!

        results = self.gdrive.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            print(f"✅ 폴더 찾음: {folders[0]}")
            return folders[0]['id']
        else:
            print(f"❌ 폴더 '{folder_name}'를 찾을 수 없음")
            return None

    def delete_file_id(self, file_id):
        try:
            self.gdrive.files().delete(fileId=file_id).execute()
            print(f"File {file_id} has been deleted.")
        except Exception as error:
            print(f"An error occurred: {error}")
            
    def delete_file(self, name):
        try:
            while True:
                id = self.get_folder_id(name)
                if id is None:
                    break
                self.gdrive.files().delete(fileId=id).execute()
                print(f"File {name} has been deleted.")
        except Exception as error:
            raise RuntimeError(f"An error occurred when deleting {name} : {error}")

        
    def create_folder(self, folder_name, parent_folder_id=None):
        
        if len(folder_name.split("/")) > 1:
            self.create_multiple_folders(folder_name, parent_folder_id)
 
        folder_id = self.get_folder_id(folder_name, parent_folder_id=parent_folder_id)
        
        if folder_id:
            print(f"📂 폴더 '{folder_name}'가 이미 존재합니다. (ID: {folder_id})")
        else:
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_folder_id:
                file_metadata["parents"] = [parent_folder_id]

            folder = self.gdrive.files().create(body=file_metadata, fields="id").execute()
            folder_id = folder.get("id")
            print(f"✅ 폴더 '{folder_name}'를 생성했습니다. (ID: {folder_id})")

        return folder_id

    def create_multiple_folders(self, folder_path, parent_folder_id=None):
        dirs = folder_path.split("/")
        for idx, _dir in enumerate(dirs):
            folder_id = self.get_folder_id(_dir)
            if folder_id is None:
                if idx != 0:
                    self.create_folder(_dir, self.get_folder_id(dirs[idx - 1]))
                else:
                    self.create_folder(_dir, parent_folder_id=parent_folder_id)
    
    def upload(self, filename, content, folder_id):
        
        if isinstance(content, str):
            file_stream = io.BytesIO(content.encode("utf-8"))
        elif isinstance(content, dict):
            import json
            file_stream = io.BytesIO(json.dumps(content, indent=4, ensure_ascii=False).encode("utf-8"))
            if 'json' not in filename:
                filename += '.json'
        else:
            raise NotImplementedError(f"NOT yet implement for {type(content)} type content")

        media = MediaIoBaseUpload(file_stream, mimetype="text/plain", resumable=True)
        file_metadata = {
            "name": filename,
            "parents": [folder_id] 
        }

        uploaded_file = self.gdrive.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"✅ File({filename}) is SUCCESFULLY uploaded to Google Drive") 
        
        return True
