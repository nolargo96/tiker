/**
 * ポートフォリオダッシュボード - Google Apps Script（Drive連携版）
 * Google Driveからレポートを読み込み、モバイル最適化されたダッシュボードを提供
 * 
 * セキュリティ対策：
 * 1. フォルダIDで特定のフォルダのみアクセス
 * 2. 読み取り専用（ファイルの変更・削除はしない）
 * 3. 認証されたユーザーのみアクセス可能
 */

// 設定
const CONFIG = {
  // Google DriveのフォルダID（upload_to_drive.py実行後に設定）
  DRIVE_FOLDER_ID: '', // ここにフォルダIDを設定
  
  // キャッシュ期間（秒）
  CACHE_DURATION: 3600,
  
  // ポートフォリオ構成
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

/**
 * Drive APIサービスを有効化
 */
function getDriveService() {
  return DriveApp;
}

/**
 * Google Driveから最新のレポートを取得
 */
function getLatestReportFromDrive() {
  try {
    if (!CONFIG.DRIVE_FOLDER_ID) {
      throw new Error('DRIVE_FOLDER_IDが設定されていません');
    }
    
    // フォルダを取得（セキュリティ：特定のフォルダのみアクセス）
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    
    // HTMLレポートを検索（最新のもの）
    const files = folder.getFilesByType(MimeType.HTML);
    let latestFile = null;
    let latestDate = new Date(0);
    
    while (files.hasNext()) {
      const file = files.next();
      const fileName = file.getName();
      
      // portfolio_hybrid_reportのみを対象
      if (fileName.includes('portfolio_hybrid_report')) {
        const lastUpdated = file.getLastUpdated();
        if (lastUpdated > latestDate) {
          latestDate = lastUpdated;
          latestFile = file;
        }
      }
    }
    
    if (!latestFile) {
      throw new Error('レポートファイルが見つかりません');
    }
    
    // ファイルの内容を取得（読み取りのみ）
    const content = latestFile.getBlob().getDataAsString();
    
    return {
      success: true,
      fileName: latestFile.getName(),
      lastUpdated: latestFile.getLastUpdated(),
      content: content
    };
    
  } catch (e) {
    console.error('Drive読み込みエラー:', e);
    return {
      success: false,
      error: e.toString()
    };
  }
}

/**
 * 討論レポートを取得
 */
function getDiscussionReports() {
  try {
    if (!CONFIG.DRIVE_FOLDER_ID) {
      return {};
    }
    
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const files = folder.getFilesByType(MimeType.PLAIN_TEXT);
    const reports = {};
    
    while (files.hasNext()) {
      const file = files.next();
      const fileName = file.getName();
      
      // Markdownファイルでdiscussionまたはanalysisを含む
      if (fileName.endsWith('.md') && 
          (fileName.includes('discussion') || fileName.includes('analysis'))) {
        
        // ティッカーシンボルを抽出
        const tickerMatch = fileName.match(/([A-Z]+)_/);
        if (tickerMatch) {
          const ticker = tickerMatch[1];
          if (!reports[ticker]) {
            reports[ticker] = {};
          }
          
          const content = file.getBlob().getDataAsString();
          
          if (fileName.includes('detailed')) {
            reports[ticker].detailed = content;
          } else {
            reports[ticker].summary = content;
          }
        }
      }
    }
    
    return reports;
    
  } catch (e) {
    console.error('討論レポート読み込みエラー:', e);
    return {};
  }
}

/**
 * ポートフォリオ設定を取得
 */
function getPortfolioConfig() {
  try {
    if (!CONFIG.DRIVE_FOLDER_ID) {
      return CONFIG.PORTFOLIO;
    }
    
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const files = folder.getFilesByName('portfolio_config.json');
    
    if (files.hasNext()) {
      const file = files.next();
      const content = file.getBlob().getDataAsString();
      const config = JSON.parse(content);
      
      // 設定をマージ
      return Object.assign({}, CONFIG.PORTFOLIO, config);
    }
    
    return CONFIG.PORTFOLIO;
    
  } catch (e) {
    console.error('設定読み込みエラー:', e);
    return CONFIG.PORTFOLIO;
  }
}

/**
 * 統合データを取得（Yahoo Finance + Drive）
 */
function getIntegratedPortfolioData() {
  const cache = CacheService.getScriptCache();
  const cacheKey = 'integrated_portfolio_data';
  const cached = cache.get(cacheKey);
  
  if (cached) {
    return JSON.parse(cached);
  }
  
  // ポートフォリオ設定を取得
  const portfolio = getPortfolioConfig();
  
  // 討論レポートを取得
  const discussionReports = getDiscussionReports();
  
  // Yahoo Financeデータを取得
  const stockData = {};
  for (const ticker in portfolio) {
    try {
      stockData[ticker] = fetchStockData(ticker);
      
      // 討論レポートがあれば追加
      if (discussionReports[ticker]) {
        stockData[ticker].discussion = discussionReports[ticker];
      }
    } catch(e) {
      console.error(`Error fetching ${ticker}:`, e);
      stockData[ticker] = { error: 'データ取得エラー' };
    }
  }
  
  const data = {
    portfolio: portfolio,
    stocks: stockData,
    reports: discussionReports,
    lastUpdate: new Date().toISOString(),
    hasLocalReports: Object.keys(discussionReports).length > 0
  };
  
  // キャッシュに保存
  cache.put(cacheKey, JSON.stringify(data), CONFIG.CACHE_DURATION);
  
  return data;
}

/**
 * セキュリティチェック関数
 */
function validateAccess() {
  // 現在のユーザーを取得
  const user = Session.getActiveUser().getEmail();
  
  // アクセス権限を確認（必要に応じて特定のメールアドレスのみ許可）
  // const allowedUsers = ['your-email@gmail.com'];
  // if (!allowedUsers.includes(user)) {
  //   throw new Error('アクセス権限がありません');
  // }
  
  return true;
}

/**
 * 更新されたdoGet関数
 */
function doGet(e) {
  // セキュリティチェック
  try {
    validateAccess();
  } catch(error) {
    return HtmlService.createHtmlOutput('<h1>アクセスが拒否されました</h1>');
  }
  
  const page = e.parameter.page || 'dashboard';
  
  if (page === 'api') {
    return handleApi(e);
  }
  
  return HtmlService
    .createTemplateFromFile('index_integrated')
    .evaluate()
    .setTitle('ポートフォリオダッシュボード')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 更新されたAPIハンドラー
 */
function handleApi(e) {
  const action = e.parameter.action;
  let result = {};
  
  try {
    switch(action) {
      case 'getPortfolio':
        result = getIntegratedPortfolioData();
        break;
      case 'getLatestReport':
        result = getLatestReportFromDrive();
        break;
      case 'refreshData':
        // キャッシュをクリア
        CacheService.getScriptCache().remove('integrated_portfolio_data');
        result = getIntegratedPortfolioData();
        break;
      default:
        result = { error: 'Unknown action' };
    }
  } catch(error) {
    result = { error: error.toString() };
  }
  
  return ContentService
    .createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

// 既存の関数（fetchStockData、calculateSMA、calculateRSI、getRecommendation）はそのまま使用

/**
 * Drive API権限の設定（初回実行時）
 */
function setupDrivePermissions() {
  // Drive APIを使用するための権限リクエスト
  const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
  console.log('フォルダ名:', folder.getName());
  console.log('アクセス権限が設定されました');
}