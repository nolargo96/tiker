# GAS プロジェクト ファイル構成ガイド

## 📋 推奨ファイル構成

GASプロジェクトに以下の3つのファイルを作成してください：

### 1. Code.gs (メインファイル)
メインのエントリーポイントと基本機能

### 2. Logging.gs (ログ機能)
アクセスログと監視機能

### 3. DriveIntegration.gs (Drive連携)
Google Driveからのレポート読み込み

### 4. index.html (既存)
Webインターフェース

## 🚀 セットアップ手順

### ステップ1: GASエディタでファイルを整理

1. GASエディタを開く
2. 既存のCode.gsファイルをバックアップ（別名で保存）
3. 新しいファイルを作成：
   - 「ファイル」→「新規作成」→「スクリプト」
   - ファイル名: `Logging`
   - 同様に`DriveIntegration`も作成

### ステップ2: 各ファイルに機能を分割

#### Code.gs の内容：
```javascript
// メイン設定
const CONFIG = {
  DRIVE_FOLDER_ID: '', // ここにフォルダIDを設定
  CACHE_DURATION: 3600,
  PORTFOLIO: {
    "TSLA": {"weight": 20, "name": "Tesla", "sector": "EV・自動運転"},
    "FSLR": {"weight": 20, "name": "First Solar", "sector": "ソーラーパネル"},
    "RKLB": {"weight": 10, "name": "Rocket Lab", "sector": "小型ロケット"},
    "ASTS": {"weight": 10, "name": "AST SpaceMobile", "sector": "衛星通信"},
    "OKLO": {"weight": 10, "name": "Oklo", "sector": "SMR原子炉"},
    "JOBY": {"weight": 10, "name": "Joby Aviation", "sector": "eVTOL"},
    "OII": {"weight": 10, "name": "Oceaneering", "sector": "海洋エンジニアリング"},
    "LUNR": {"weight": 5, "name": "Intuitive Machines", "sector": "月面探査"},
    "RDW": {"weight": 5, "name": "Redwire", "sector": "宇宙製造"}
  }
};

// メインエントリーポイント
function doGet(e) {
  const startTime = new Date();
  const page = e.parameter.page || 'dashboard';
  
  try {
    // ログ記録（Logging.gsの関数を使用）
    logAccess('ページアクセス', `ページ: ${page}`);
    
    // セキュリティチェック
    validateAccess();
    
    if (page === 'api') {
      return handleApi(e);
    } else if (page === 'logs') {
      // ログビューア（Logging.gsの関数を使用）
      return HtmlService
        .createHtmlOutput(getLogViewerHtml())
        .setTitle('アクセスログ')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1');
    }
    
    // 通常のダッシュボード
    return HtmlService
      .createTemplateFromFile('index')
      .evaluate()
      .setTitle('ポートフォリオダッシュボード')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
      
  } catch (error) {
    logAccess('エラー', error.toString());
    throw error;
  }
}

// APIハンドラー
function handleApi(e) {
  const action = e.parameter.action;
  
  try {
    logAccess('API呼び出し', `アクション: ${action}`);
    
    let result = {};
    switch(action) {
      case 'getPortfolio':
        // DriveIntegration.gsの関数を使用
        result = getIntegratedPortfolioData();
        break;
      case 'getLatestReport':
        // DriveIntegration.gsの関数を使用
        result = getLatestReportFromDrive();
        break;
      case 'refreshData':
        CacheService.getScriptCache().remove('integrated_portfolio_data');
        result = getIntegratedPortfolioData();
        break;
      case 'getLogStats':
        // Logging.gsの関数を使用
        result = getLogStatistics();
        break;
      default:
        result = { error: 'Unknown action' };
    }
    
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(error) {
    logAccess('APIエラー', `${action}: ${error.toString()}`);
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// セキュリティチェック
function validateAccess() {
  const user = Session.getActiveUser().getEmail();
  
  // 必要に応じて特定のメールアドレスのみ許可
  // const allowedUsers = ['your-email@gmail.com'];
  // if (!allowedUsers.includes(user)) {
  //   logAccess('アクセス拒否', `不正なユーザー: ${user}`);
  //   throw new Error('アクセス権限がありません');
  // }
  
  return true;
}

// Yahoo Financeデータ取得（既存の関数）
function fetchStockData(ticker) {
  // 既存のコードをそのまま使用
}

// その他の既存関数...
```

### ステップ3: 機能の統合確認

1. **テスト実行**：
   ```javascript
   function testIntegration() {
     // ログ機能テスト
     logAccess('テスト', '統合機能の動作確認');
     
     // Drive連携テスト
     const folderTest = testDriveAccess();
     console.log('Drive連携:', folderTest);
     
     // 統計取得テスト
     const stats = getLogStatistics();
     console.log('ログ統計:', stats);
   }
   ```

2. **権限の確認**：
   - 初回実行時に必要な権限を付与
   - Drive API、Sheets APIへのアクセス許可

### ステップ4: デプロイ設定

1. **appsscript.json**の確認（既に設定済み）
2. **Webアプリとして再デプロイ**：
   - 「デプロイ」→「新しいデプロイ」
   - 説明: "統合版 - ログ機能とDrive連携"
   - アクセス権: "自分のみ"

## 📊 機能の使い分け

### 通常のダッシュボード
```
https://script.google.com/.../exec
```

### ログビューア
```
https://script.google.com/.../exec?page=logs
```

### API呼び出し
```
https://script.google.com/.../exec?page=api&action=getPortfolio
```

## 🔒 セキュリティ設定

1. **フォルダIDの設定**：
   - `upload_to_drive.py`実行後に表示されるフォルダIDを設定
   - Code.gsの`CONFIG.DRIVE_FOLDER_ID`に設定

2. **アクセス制限**：
   - 必要に応じて`validateAccess()`関数で特定ユーザーのみ許可

3. **ログ監視**：
   - 定期的にログビューアで不審なアクセスを確認
   - 必要に応じてアラート設定

## トラブルシューティング

### 問題1: ファイルが見つからないエラー
- 解決: 各ファイル名が正しいか確認（Logging.gs、DriveIntegration.gs）

### 問題2: 権限エラー
- 解決: 再度認証を実行し、必要な権限を付与

### 問題3: キャッシュの問題
- 解決: `?page=api&action=refreshData`でキャッシュクリア

## 次のステップ

1. **定期実行の設定**：
   - トリガーで日次レポート生成を自動化
   
2. **通知設定**：
   - 不審なアクセス検知時のメール通知
   
3. **バックアップ**：
   - 定期的なログのエクスポート