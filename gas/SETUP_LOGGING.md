# GAS ログ機能セットアップガイド

## 📋 ファイル構成

### 現在のGASプロジェクトに以下のファイルが必要：

1. **Code.gs** - メイン機能（既存）
2. **Logging.gs** - ログ機能（新規作成）
3. **index.html** - Webインターフェース（既存）

## 🚀 セットアップ手順

### ステップ1: Logging.gsを作成

1. GASエディタで「ファイル」→「新規作成」→「スクリプト」
2. ファイル名を`Logging`に設定
3. 以下のセクションから必要な関数をコピー

### ステップ2: Code.gsを更新

既存の`doGet`関数を以下に置き換え：

```javascript
// メインのエントリーポイント
function doGet(e) {
  const startTime = new Date();
  const page = e.parameter.page || 'dashboard';
  
  try {
    // ログ機能が利用可能な場合は記録
    if (typeof logAccess === 'function') {
      logAccess('ページアクセス', `ページ: ${page}`);
    }
    
    // ページに応じて処理
    if (page === 'api') {
      return handleApi(e);
    } else if (page === 'logs' && typeof getLogViewerHtml === 'function') {
      // ログビューア
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
    if (typeof logAccess === 'function') {
      logAccess('エラー', error.toString());
    }
    throw error;
  }
}

// APIハンドラーも更新
function handleApi(e) {
  const action = e.parameter.action;
  
  try {
    // ログ記録
    if (typeof logAccess === 'function') {
      logAccess('API呼び出し', `アクション: ${action}`);
    }
    
    let result = {};
    switch(action) {
      case 'getPortfolio':
        result = getPortfolioData();
        break;
      case 'refreshData':
        result = refreshAllData();
        break;
      case 'getLogStats':
        // ログ統計（利用可能な場合）
        if (typeof getLogStatistics === 'function') {
          result = getLogStatistics();
        } else {
          result = { error: 'ログ機能が有効ではありません' };
        }
        break;
      default:
        result = { error: 'Unknown action' };
    }
    
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(error) {
    if (typeof logAccess === 'function') {
      logAccess('APIエラー', `${action}: ${error.toString()}`);
    }
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

### ステップ3: 権限の確認

初回実行時に以下を実行：

```javascript
function testLogging() {
  // ログ機能のテスト
  logAccess('テスト', 'ログ機能の動作確認');
  
  // 統計の確認
  const stats = getLogStatistics();
  console.log('ログ統計:', stats);
}
```

### ステップ4: ログビューアへのアクセス

デプロイ後、以下のURLでログを確認：
```
[あなたのGAS URL]?page=logs
```

## 📊 ログの確認方法

### 1. Webインターフェース
- ログビューアページで統計と最近のログを確認
- リアルタイムで更新（30秒ごと）

### 2. Google Sheets
- 「ポートフォリオ_アクセスログ」シートが自動作成
- フィルター機能で詳細分析可能
- CSVエクスポート可能

### 3. 不審アクセスアラート
必要に応じて以下を設定：

```javascript
function setupAlerts() {
  // 1時間ごとにチェック
  ScriptApp.newTrigger('checkSuspiciousActivity')
    .timeBased()
    .everyHours(1)
    .create();
}

function checkSuspiciousActivity() {
  const suspicious = detectSuspiciousAccess();
  if (suspicious.length > 0) {
    // メール通知やSlack通知など
    console.log('不審なアクセス検知:', suspicious);
  }
}
```

## 🔒 セキュリティ設定

### アクセス制限を強化する場合：

```javascript
// Code.gsに追加
function validateAccess() {
  const user = Session.getActiveUser().getEmail();
  const allowedUsers = [
    'your-email@gmail.com',
    // 他の許可ユーザー
  ];
  
  if (!allowedUsers.includes(user)) {
    if (typeof logAccess === 'function') {
      logAccess('アクセス拒否', `不正なユーザー: ${user}`);
    }
    throw new Error('アクセス権限がありません');
  }
  
  return true;
}
```

## 📈 活用例

1. **アクセス頻度の分析**
   - どの時間帯によくアクセスするか
   - どの機能がよく使われるか

2. **パフォーマンス監視**
   - API呼び出しの頻度
   - エラーの発生状況

3. **セキュリティ監査**
   - 不正アクセスの早期発見
   - アクセスパターンの異常検知

## トラブルシューティング

### ログが記録されない
1. Logging.gsが正しく作成されているか確認
2. 関数名が正しいか確認（logAccess, getLogStatistics等）
3. 権限エラーがないか確認

### シートが作成されない
1. Drive APIの権限を確認
2. 初回は`testLogging()`を実行して権限を付与

### ログビューアが表示されない
1. URLに`?page=logs`を正しく付けているか確認
2. getLogViewerHtml関数が存在するか確認