#!/usr/bin/env python3
"""
Google Driveへのレポート自動アップロードスクリプト
ローカルで生成したレポートをGoogle Driveに自動アップロード
"""

import os
import json
import glob
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveUploader:
    def __init__(self):
        self.creds = None
        self.service = None
        self.folder_id = None
        
    def authenticate(self):
        """Google Drive APIの認証"""
        # token.pickleファイルに保存された認証情報を読み込み
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 認証情報がない、または期限切れの場合
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # credentials.jsonが必要（Google Cloud Consoleから取得）
                if not os.path.exists('credentials.json'):
                    print("❌ credentials.jsonが見つかりません")
                    print("Google Cloud Consoleから認証情報をダウンロードしてください")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
        return True
    
    def create_or_get_folder(self, folder_name='ポートフォリオレポート'):
        """Google Driveにフォルダを作成または取得"""
        try:
            # 既存のフォルダを検索
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])
            
            if items:
                self.folder_id = items[0]['id']
                print(f"✅ 既存のフォルダを使用: {folder_name} (ID: {self.folder_id})")
            else:
                # フォルダを作成
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                self.folder_id = folder.get('id')
                print(f"✅ フォルダを作成: {folder_name} (ID: {self.folder_id})")
                
            return self.folder_id
            
        except Exception as e:
            print(f"❌ フォルダ作成エラー: {e}")
            return None
    
    def upload_file(self, file_path, mime_type='text/html'):
        """ファイルをGoogle Driveにアップロード"""
        try:
            file_name = os.path.basename(file_path)
            
            # 同名ファイルが存在するか確認
            query = f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id)").execute()
            items = results.get('files', [])
            
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            if items:
                # 既存ファイルを更新
                file_id = items[0]['id']
                file = self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    fields='id,name,webViewLink'
                ).execute()
                print(f"✅ 更新: {file_name}")
            else:
                # 新規アップロード
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,webViewLink'
                ).execute()
                print(f"✅ アップロード: {file_name}")
            
            # 共有リンクを取得
            web_link = file.get('webViewLink')
            print(f"   📎 リンク: {web_link}")
            
            return file.get('id'), web_link
            
        except Exception as e:
            print(f"❌ アップロードエラー ({file_name}): {e}")
            return None, None
    
    def upload_portfolio_reports(self):
        """ポートフォリオレポートをアップロード"""
        print("\n📤 ポートフォリオレポートのアップロード開始...")
        
        # アップロードするファイルのパターン
        upload_patterns = [
            ('reports/html/portfolio_hybrid_report_*.html', 'text/html'),
            ('reports/*_discussion_*.md', 'text/markdown'),
            ('reports/detailed_discussions/*_detailed_analysis_*.md', 'text/markdown'),
            ('src/portfolio/portfolio_config.json', 'application/json')
        ]
        
        uploaded_files = []
        
        for pattern, mime_type in upload_patterns:
            files = glob.glob(pattern)
            
            # 最新のファイルのみアップロード（HTMLレポートの場合）
            if 'portfolio_hybrid_report' in pattern and files:
                files = [max(files, key=os.path.getmtime)]
            
            for file_path in files:
                file_id, web_link = self.upload_file(file_path, mime_type)
                if file_id:
                    uploaded_files.append({
                        'file': file_path,
                        'id': file_id,
                        'link': web_link
                    })
        
        # アップロード情報を保存
        self.save_upload_info(uploaded_files)
        
        return uploaded_files
    
    def save_upload_info(self, uploaded_files):
        """アップロード情報をJSONに保存"""
        upload_info = {
            'last_update': datetime.now().isoformat(),
            'folder_id': self.folder_id,
            'files': uploaded_files
        }
        
        with open('drive_upload_info.json', 'w', encoding='utf-8') as f:
            json.dump(upload_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ アップロード完了: {len(uploaded_files)}ファイル")
        print(f"📁 フォルダID: {self.folder_id}")


def main():
    """メイン実行関数"""
    print("🚀 Google Drive アップローダー")
    print("="*50)
    
    uploader = DriveUploader()
    
    # 認証
    if not uploader.authenticate():
        print("認証に失敗しました")
        return
    
    # フォルダ作成/取得
    if not uploader.create_or_get_folder():
        print("フォルダの作成に失敗しました")
        return
    
    # レポートアップロード
    uploaded_files = uploader.upload_portfolio_reports()
    
    if uploaded_files:
        print("\n🎉 アップロード成功！")
        print("GASからアクセスする際は、以下のフォルダIDを使用してください：")
        print(f"フォルダID: {uploader.folder_id}")
    else:
        print("\n❌ アップロードするファイルがありませんでした")
    
    # 実行後の指示
    print("\n📋 次のステップ:")
    print("1. GASのCode.gsにフォルダIDを設定")
    print("2. GASでDrive APIを有効化")
    print("3. 定期実行を設定")


if __name__ == '__main__':
    main()