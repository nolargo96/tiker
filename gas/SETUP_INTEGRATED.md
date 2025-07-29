# GAS統合版セットアップガイド

## 📋 セットアップ手順

### 1. 既存のCode.gsを置き換え

1. GASエディタを開く
2. 既存のCode.gsの内容をバックアップ（念のため）
3. `Code_integrated.gs`の内容をすべてコピー
4. 既存のCode.gsに貼り付けて保存

### 2. フォルダIDの設定

`upload_to_drive.py`実行後に表示されたフォルダIDを設定：

```javascript
const CONFIG = {
  // Google DriveのフォルダID（upload_to_drive.py実行後に設定）
  DRIVE_FOLDER_ID: 'ここにフォルダIDを入力', // 例: '1ABC123...'
  ...
}
```

### 3. 初期設定の実行

GASエディタで以下の関数を実行：

```javascript
setupInitial()
```

これにより：
- Drive権限の確認
- ログシートの作成
- 日次更新トリガーの設定

### 4. 再デプロイ

1. 「デプロイ」→「デプロイを管理」
2. 既存のデプロイを選択
3. 「編集」→「バージョン」→「新バージョン」
4. 説明: "統合版 - ログ機能とDrive連携（1日1回更新）"
5. 「デプロイ」

## 📊 使い方

### 通常のダッシュボード
```
https://script.google.com/.../exec
```

### ログビューア
```
https://script.google.com/.../exec?page=logs
```

### 手動でデータ更新
```
https://script.google.com/.../exec?page=api&action=refreshData
```

## ⚙️ 設定確認

### キャッシュ期間
- 24時間（86400秒）に設定済み
- 毎日午前6時に自動更新

### ログ機能
- アクセスログ自動記録
- 深夜警告は無効化
- 短時間大量アクセス（50回/時）のみ警告

### 自動更新
- 毎日午前6時に実行
- `dailyUpdate()`関数でキャッシュクリア＆データ再取得

## 🔧 カスタマイズ

### 自動更新時刻の変更

```javascript
function setupDailyTrigger() {
  // ...
  ScriptApp.newTrigger('dailyUpdate')
    .timeBased()
    .everyDays(1)
    .atHour(6)  // ここを変更（0-23）
    .create();
}
```

### アクセス制限を有効化

```javascript
function validateAccess() {
  const user = Session.getActiveUser().getEmail();
  
  // コメントアウトを解除して、許可するメールアドレスを設定
  const allowedUsers = ['your-email@gmail.com'];
  if (!allowedUsers.includes(user)) {
    logAccess('アクセス拒否', `不正なユーザー: ${user}`);
    throw new Error('アクセス権限がありません');
  }
  
  return true;
}
```

## トラブルシューティング

### Drive連携エラー
1. `CONFIG.DRIVE_FOLDER_ID`が正しく設定されているか確認
2. フォルダへのアクセス権限があるか確認
3. `setupInitial()`を再実行

### ログが記録されない
1. 「ポートフォリオ_アクセスログ」シートが作成されているか確認
2. Google Sheetsへのアクセス権限を確認

### データが更新されない
1. キャッシュをクリア: `?page=api&action=refreshData`
2. 手動で`dailyUpdate()`を実行
3. エラーログを確認