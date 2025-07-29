/**
 * アクセスログ機能
 * Google Sheetsにアクセス履歴を自動記録
 */

// ログ設定
const LOG_CONFIG = {
  SHEET_NAME: 'ポートフォリオ_アクセスログ',
  MAX_ROWS: 10000, // 最大保存行数
  COLUMNS: ['タイムスタンプ', 'ユーザー', 'アクション', 'IPアドレス', 'ユーザーエージェント', '詳細']
};

/**
 * ログ用スプレッドシートを作成または取得
 */
function getOrCreateLogSheet() {
  const cache = CacheService.getScriptCache();
  const cacheKey = 'log_sheet_id';
  let sheetId = cache.get(cacheKey);
  
  if (sheetId) {
    try {
      return SpreadsheetApp.openById(sheetId);
    } catch (e) {
      // キャッシュが無効な場合は再作成
    }
  }
  
  // 既存のシートを検索
  const files = DriveApp.getFilesByName(LOG_CONFIG.SHEET_NAME);
  if (files.hasNext()) {
    const sheet = SpreadsheetApp.open(files.next());
    cache.put(cacheKey, sheet.getId(), 3600);
    return sheet;
  }
  
  // 新規作成
  const sheet = SpreadsheetApp.create(LOG_CONFIG.SHEET_NAME);
  const ws = sheet.getActiveSheet();
  
  // ヘッダー設定
  ws.getRange(1, 1, 1, LOG_CONFIG.COLUMNS.length).setValues([LOG_CONFIG.COLUMNS]);
  ws.getRange(1, 1, 1, LOG_CONFIG.COLUMNS.length)
    .setBackground('#1e3a8a')
    .setFontColor('#ffffff')
    .setFontWeight('bold');
  
  // 列幅調整
  ws.setColumnWidth(1, 180); // タイムスタンプ
  ws.setColumnWidth(2, 200); // ユーザー
  ws.setColumnWidth(3, 120); // アクション
  ws.setColumnWidth(4, 150); // IPアドレス
  ws.setColumnWidth(5, 300); // ユーザーエージェント
  ws.setColumnWidth(6, 400); // 詳細
  
  // フィルター追加
  ws.getRange(1, 1, 1, LOG_CONFIG.COLUMNS.length).createFilter();
  
  cache.put(cacheKey, sheet.getId(), 3600);
  return sheet;
}

/**
 * アクセスログを記録
 */
function logAccess(action, details = '') {
  try {
    const sheet = getOrCreateLogSheet();
    const ws = sheet.getActiveSheet();
    
    // 現在のユーザー情報
    const user = Session.getActiveUser().getEmail() || 'Unknown';
    const timestamp = new Date();
    
    // リクエスト情報（利用可能な場合）
    let ipAddress = 'N/A';
    let userAgent = 'N/A';
    
    // HtmlServiceのコンテキストから情報を取得（可能な場合）
    try {
      // GASでは直接IPアドレスは取得できないが、将来の拡張用に準備
      ipAddress = 'GAS Internal';
      userAgent = 'GAS Web App';
    } catch (e) {
      // エラーは無視
    }
    
    // ログデータ
    const logData = [
      timestamp,
      user,
      action,
      ipAddress,
      userAgent,
      details
    ];
    
    // 最終行に追加
    ws.appendRow(logData);
    
    // 古いログを削除（MAX_ROWSを超えた場合）
    const lastRow = ws.getLastRow();
    if (lastRow > LOG_CONFIG.MAX_ROWS + 1) { // +1 for header
      ws.deleteRows(2, lastRow - LOG_CONFIG.MAX_ROWS - 1);
    }
    
    return true;
  } catch (e) {
    console.error('ログ記録エラー:', e);
    return false;
  }
}

/**
 * ログ統計を取得
 */
function getLogStatistics() {
  try {
    const sheet = getOrCreateLogSheet();
    const ws = sheet.getActiveSheet();
    const lastRow = ws.getLastRow();
    
    if (lastRow <= 1) {
      return {
        totalAccess: 0,
        uniqueUsers: 0,
        todayAccess: 0,
        lastAccess: null
      };
    }
    
    // データ範囲を取得
    const data = ws.getRange(2, 1, lastRow - 1, LOG_CONFIG.COLUMNS.length).getValues();
    
    // 統計計算
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    let todayCount = 0;
    const uniqueUsers = new Set();
    let lastAccessTime = null;
    
    data.forEach(row => {
      const timestamp = new Date(row[0]);
      const user = row[1];
      
      uniqueUsers.add(user);
      
      if (timestamp >= today) {
        todayCount++;
      }
      
      if (!lastAccessTime || timestamp > lastAccessTime) {
        lastAccessTime = timestamp;
      }
    });
    
    return {
      totalAccess: data.length,
      uniqueUsers: uniqueUsers.size,
      todayAccess: todayCount,
      lastAccess: lastAccessTime,
      recentLogs: data.slice(-10).reverse() // 最新10件
    };
    
  } catch (e) {
    console.error('統計取得エラー:', e);
    return null;
  }
}

/**
 * 不審なアクセスを検知
 */
function detectSuspiciousAccess() {
  try {
    const sheet = getOrCreateLogSheet();
    const ws = sheet.getActiveSheet();
    const lastRow = ws.getLastRow();
    
    if (lastRow <= 1) return [];
    
    // 過去1時間のデータを取得
    const oneHourAgo = new Date(Date.now() - 3600000);
    const data = ws.getRange(2, 1, lastRow - 1, LOG_CONFIG.COLUMNS.length).getValues();
    
    const userAccessCount = {};
    const suspiciousActivities = [];
    
    data.forEach(row => {
      const timestamp = new Date(row[0]);
      const user = row[1];
      const action = row[2];
      
      if (timestamp >= oneHourAgo) {
        userAccessCount[user] = (userAccessCount[user] || 0) + 1;
        
        // 短時間での大量アクセスを検知
        if (userAccessCount[user] > 50) {
          suspiciousActivities.push({
            user: user,
            count: userAccessCount[user],
            type: '短時間での大量アクセス'
          });
        }
      }
      
      // 深夜のアクセスを検知
      const hour = timestamp.getHours();
      if (hour >= 2 && hour <= 5) {
        suspiciousActivities.push({
          user: user,
          time: timestamp,
          type: '深夜アクセス'
        });
      }
    });
    
    return suspiciousActivities;
    
  } catch (e) {
    console.error('不審アクセス検知エラー:', e);
    return [];
  }
}

/**
 * ログビューアHTML
 */
function getLogViewerHtml() {
  return `
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h2>📊 アクセスログ統計</h2>
      <div id="logStats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
        <div style="background: #f0f4ff; padding: 15px; border-radius: 8px;">
          <div style="color: #666; font-size: 0.9em;">総アクセス数</div>
          <div style="font-size: 1.5em; font-weight: bold; color: #1e3a8a;" id="totalAccess">-</div>
        </div>
        <div style="background: #f0f4ff; padding: 15px; border-radius: 8px;">
          <div style="color: #666; font-size: 0.9em;">ユニークユーザー</div>
          <div style="font-size: 1.5em; font-weight: bold; color: #1e3a8a;" id="uniqueUsers">-</div>
        </div>
        <div style="background: #f0f4ff; padding: 15px; border-radius: 8px;">
          <div style="color: #666; font-size: 0.9em;">本日のアクセス</div>
          <div style="font-size: 1.5em; font-weight: bold; color: #1e3a8a;" id="todayAccess">-</div>
        </div>
        <div style="background: #f0f4ff; padding: 15px; border-radius: 8px;">
          <div style="color: #666; font-size: 0.9em;">最終アクセス</div>
          <div style="font-size: 0.9em; color: #1e3a8a;" id="lastAccess">-</div>
        </div>
      </div>
      
      <h3>📜 最近のアクセスログ</h3>
      <div id="recentLogs" style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; padding: 10px;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background: #f5f5f5;">
              <th style="padding: 8px; text-align: left;">時刻</th>
              <th style="padding: 8px; text-align: left;">ユーザー</th>
              <th style="padding: 8px; text-align: left;">アクション</th>
              <th style="padding: 8px; text-align: left;">詳細</th>
            </tr>
          </thead>
          <tbody id="logTableBody">
          </tbody>
        </table>
      </div>
      
      <div id="suspiciousAlert" style="margin-top: 20px; display: none;">
        <h3 style="color: #dc2626;">⚠️ 不審なアクセス</h3>
        <div id="suspiciousContent" style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 15px;">
        </div>
      </div>
    </div>
    
    <script>
      function loadLogStats() {
        google.script.run
          .withSuccessHandler(displayLogStats)
          .withFailureHandler(console.error)
          .getLogStatistics();
          
        google.script.run
          .withSuccessHandler(displaySuspicious)
          .withFailureHandler(console.error)
          .detectSuspiciousAccess();
      }
      
      function displayLogStats(stats) {
        if (!stats) return;
        
        document.getElementById('totalAccess').textContent = stats.totalAccess;
        document.getElementById('uniqueUsers').textContent = stats.uniqueUsers;
        document.getElementById('todayAccess').textContent = stats.todayAccess;
        document.getElementById('lastAccess').textContent = 
          stats.lastAccess ? new Date(stats.lastAccess).toLocaleString('ja-JP') : 'なし';
        
        // 最近のログ表示
        const tbody = document.getElementById('logTableBody');
        tbody.innerHTML = '';
        
        if (stats.recentLogs) {
          stats.recentLogs.forEach(log => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = new Date(log[0]).toLocaleString('ja-JP');
            row.insertCell(1).textContent = log[1];
            row.insertCell(2).textContent = log[2];
            row.insertCell(3).textContent = log[5] || '-';
          });
        }
      }
      
      function displaySuspicious(activities) {
        if (!activities || activities.length === 0) return;
        
        const alert = document.getElementById('suspiciousAlert');
        const content = document.getElementById('suspiciousContent');
        
        alert.style.display = 'block';
        content.innerHTML = activities.map(a => 
          '<div style="margin-bottom: 8px;">• ' + a.type + ': ' + a.user + '</div>'
        ).join('');
      }
      
      // 初回読み込み
      loadLogStats();
      
      // 30秒ごとに更新
      setInterval(loadLogStats, 30000);
    </script>
  `;
}

/**
 * 更新版doGet - ログ記録付き
 */
function doGetWithLogging(e) {
  const startTime = new Date();
  const page = e.parameter.page || 'dashboard';
  
  try {
    // アクセスログ記録
    logAccess('ページアクセス', `ページ: ${page}`);
    
    // セキュリティチェック
    validateAccess();
    
    if (page === 'api') {
      return handleApiWithLogging(e);
    } else if (page === 'logs') {
      // ログビューア
      return HtmlService
        .createHtmlOutput(getLogViewerHtml())
        .setTitle('アクセスログ')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1');
    }
    
    return HtmlService
      .createTemplateFromFile('index_integrated')
      .evaluate()
      .setTitle('ポートフォリオダッシュボード')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
      
  } catch (error) {
    logAccess('エラー', error.toString());
    throw error;
  }
}

/**
 * 更新版APIハンドラー - ログ記録付き
 */
function handleApiWithLogging(e) {
  const action = e.parameter.action;
  
  try {
    logAccess('API呼び出し', `アクション: ${action}`);
    
    let result = {};
    switch(action) {
      case 'getPortfolio':
        result = getIntegratedPortfolioData();
        break;
      case 'getLatestReport':
        result = getLatestReportFromDrive();
        break;
      case 'refreshData':
        CacheService.getScriptCache().remove('integrated_portfolio_data');
        result = getIntegratedPortfolioData();
        break;
      case 'getLogStats':
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

/**
 * ログのエクスポート機能
 */
function exportLogs() {
  try {
    const sheet = getOrCreateLogSheet();
    const url = sheet.getUrl();
    
    // CSVとしてダウンロード可能なリンクを生成
    const csvUrl = url.replace(/\/edit.*$/, '/export?format=csv');
    
    return {
      sheetUrl: url,
      csvUrl: csvUrl
    };
  } catch (e) {
    console.error('ログエクスポートエラー:', e);
    return null;
  }
}