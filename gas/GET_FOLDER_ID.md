# Google DriveフォルダIDの取得方法

## 方法1: Google Driveから直接取得

### 1. Google Driveにアクセス
1. [Google Drive](https://drive.google.com)を開く
2. レポートを保存したいフォルダを作成または選択

### 2. フォルダIDを取得
1. フォルダを開く
2. URLを確認：
   ```
   https://drive.google.com/drive/folders/【ここがフォルダID】
   ```
   例：
   ```
   https://drive.google.com/drive/folders/1ABC123DEF456GHI789JKL
   ```
   この場合、フォルダIDは：`1ABC123DEF456GHI789JKL`

### 3. 新規フォルダを作成する場合
1. Google Driveで「新規」→「フォルダ」
2. フォルダ名：`ポートフォリオレポート`
3. フォルダを開いてURLからIDをコピー

## 方法2: GASから手動でフォルダを作成

### 1. GASエディタで以下のコードを実行

```javascript
function createReportFolder() {
  // フォルダを作成
  const folderName = 'ポートフォリオレポート';
  
  // 既存のフォルダを検索
  const folders = DriveApp.getFoldersByName(folderName);
  
  let folder;
  if (folders.hasNext()) {
    folder = folders.next();
    console.log('既存のフォルダを使用:', folderName);
  } else {
    folder = DriveApp.createFolder(folderName);
    console.log('新しいフォルダを作成:', folderName);
  }
  
  // フォルダIDを表示
  const folderId = folder.getId();
  console.log('フォルダID:', folderId);
  console.log('フォルダURL:', folder.getUrl());
  
  // 共有設定（任意）
  // folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  return folderId;
}
```

### 2. 実行結果からフォルダIDをコピー

## GASにフォルダIDを設定

### Code.gsの設定を更新

```javascript
const CONFIG = {
  // Google DriveのフォルダID（ここに取得したIDを設定）
  DRIVE_FOLDER_ID: '取得したフォルダIDをここに貼り付け',
  // 例：
  // DRIVE_FOLDER_ID: '1ABC123DEF456GHI789JKL',
  
  // ... 他の設定
};
```

## 設定後の確認

### テスト関数を実行

```javascript
function testDriveAccess() {
  if (!CONFIG.DRIVE_FOLDER_ID) {
    console.log('❌ DRIVE_FOLDER_IDが設定されていません');
    return;
  }
  
  try {
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    console.log('✅ フォルダアクセス成功');
    console.log('フォルダ名:', folder.getName());
    console.log('フォルダURL:', folder.getUrl());
    
    // テストファイルを作成
    const testContent = 'テストファイル - ' + new Date();
    const file = folder.createFile('test.txt', testContent);
    console.log('✅ テストファイル作成成功');
    
    // テストファイルを削除
    file.setTrashed(true);
    console.log('✅ テストファイル削除成功');
    
  } catch(e) {
    console.log('❌ エラー:', e.toString());
  }
}
```

## トラブルシューティング

### エラー: "ファイルが見つかりません"
- フォルダIDが正しいか確認
- フォルダが削除されていないか確認
- アクセス権限があるか確認

### エラー: "権限がありません"
- フォルダの共有設定を確認
- GASを実行しているアカウントがフォルダへのアクセス権を持っているか確認

## 推奨手順

1. **方法2（GAS）を使用することを推奨**
   - GASから直接フォルダを作成
   - 権限問題を回避できる
   - フォルダIDが自動的に取得できる

2. **createReportFolder()を実行**
   - 実行ログからフォルダIDをコピー
   - Code.gsのCONFIG.DRIVE_FOLDER_IDに設定

3. **testDriveAccess()でテスト**
   - 正しく設定されているか確認