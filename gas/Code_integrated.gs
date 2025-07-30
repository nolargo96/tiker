/**
 * ポートフォリオダッシュボード統合版
 * - Yahoo Financeからのリアルタイムデータ取得
 * - Google Driveからのローカルレポート読み込み
 * - アクセスログ記録（深夜警告なし）
 * - 1日1回の自動更新
 */

// ========== 設定 ==========
const CONFIG = {
  // Google DriveのフォルダID（upload_to_drive.py実行後に設定）
  DRIVE_FOLDER_ID: '1JpP1WBK-DG7SYBNXP-QTCQW8uUzVZwwr', // ここにフォルダIDを設定
  
  // キャッシュ期間（24時間 = 1日1回更新）
  CACHE_DURATION: 86400, // 24時間（秒）
  
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

// ログ設定
const LOG_CONFIG = {
  SHEET_NAME: 'ポートフォリオ_アクセスログ',
  MAX_ROWS: 10000, // 最大保存行数
  COLUMNS: ['タイムスタンプ', 'ユーザー', 'アクション', 'IPアドレス', 'ユーザーエージェント', '詳細']
};

// ========== メインエントリーポイント ==========
function doGet(e) {
  const startTime = new Date();
  const page = (e && e.parameter && e.parameter.page) ? e.parameter.page : 'dashboard';
  
  try {
    // アクセスログ記録
    logAccess('ページアクセス', `ページ: ${page}`);
    
    // セキュリティチェック
    validateAccess();
    
    if (page === 'api') {
      return handleApi(e);
    } else if (page === 'logs') {
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
    logAccess('エラー', error.toString());
    throw error;
  }
}

// ========== APIハンドラー ==========
function handleApi(e) {
  const action = (e && e.parameter && e.parameter.action) ? e.parameter.action : 'getPortfolio';
  
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

// ========== ログ機能 ==========
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

function logAccess(action, details = '') {
  try {
    const sheet = getOrCreateLogSheet();
    const ws = sheet.getActiveSheet();
    
    // 現在のユーザー情報
    const user = Session.getActiveUser().getEmail() || 'Unknown';
    const timestamp = new Date();
    
    // リクエスト情報
    const ipAddress = 'GAS Internal';
    const userAgent = 'GAS Web App';
    
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
    if (lastRow > LOG_CONFIG.MAX_ROWS + 1) {
      ws.deleteRows(2, lastRow - LOG_CONFIG.MAX_ROWS - 1);
    }
    
    return true;
  } catch (e) {
    console.error('ログ記録エラー:', e);
    return false;
  }
}

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

// 不審なアクセス検知（簡略版：深夜警告を削除）
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
      
      if (timestamp >= oneHourAgo) {
        userAccessCount[user] = (userAccessCount[user] || 0) + 1;
        
        // 短時間での大量アクセスのみ検知（50回以上）
        if (userAccessCount[user] > 50) {
          const existing = suspiciousActivities.find(a => a.user === user && a.type === '短時間での大量アクセス');
          if (!existing) {
            suspiciousActivities.push({
              user: user,
              count: userAccessCount[user],
              type: '短時間での大量アクセス'
            });
          }
        }
      }
    });
    
    return suspiciousActivities;
    
  } catch (e) {
    console.error('不審アクセス検知エラー:', e);
    return [];
  }
}

// ========== Drive連携機能 ==========
function getLatestReportFromDrive() {
  try {
    if (!CONFIG.DRIVE_FOLDER_ID) {
      throw new Error('DRIVE_FOLDER_IDが設定されていません');
    }
    
    // フォルダを取得
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
    
    // ファイルの内容を取得
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

function getIntegratedPortfolioData() {
  console.log('getIntegratedPortfolioData called'); // デバッグログ
  const cache = CacheService.getScriptCache();
  const cacheKey = 'integrated_portfolio_data';
  const cached = cache.get(cacheKey);
  
  if (cached) {
    console.log('Returning cached data'); // デバッグログ
    return JSON.parse(cached);
  }
  
  // Yahoo Financeデータを取得
  const stockData = {};
  for (const ticker in CONFIG.PORTFOLIO) {
    console.log(`Processing ticker: ${ticker}`); // デバッグログ
    if (CONFIG.PORTFOLIO.hasOwnProperty(ticker)) {
      try {
        stockData[ticker] = fetchStockData(ticker);
      } catch(e) {
        console.error(`Error fetching ${ticker}:`, e);
        stockData[ticker] = { error: 'データ取得エラー' };
      }
    }
  }
  
  const data = {
    portfolio: CONFIG.PORTFOLIO,
    stocks: stockData,
    lastUpdate: new Date().toISOString()
  };
  
  // キャッシュに保存（24時間）
  cache.put(cacheKey, JSON.stringify(data), CONFIG.CACHE_DURATION);
  
  return data;
}

// ========== Yahoo Finance関連 ==========
function fetchStockData(ticker) {
  // ティッカーシンボルの検証
  if (!ticker || ticker === 'undefined' || ticker === undefined) {
    console.log('fetchStockData called with invalid ticker:', ticker);
    return {
      ticker: 'UNKNOWN',
      name: 'Unknown',
      sector: 'Unknown',
      currentPrice: 0,
      change: 0,
      changePercent: 0,
      volume: 0,
      error: '無効なティッカーシンボル'
    };
  }
  
  const cache = CacheService.getScriptCache();
  const cacheKey = `stock_${ticker}`;
  const cached = cache.get(cacheKey);
  
  if (cached) {
    return JSON.parse(cached);
  }
  
  try {
    const url = `https://query2.finance.yahoo.com/v8/finance/chart/${ticker}`;
    const response = UrlFetchApp.fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      muteHttpExceptions: true
    });
    
    // レスポンスステータスチェック
    if (response.getResponseCode() !== 200) {
      console.error(`Failed to fetch data for ${ticker}: ${response.getResponseCode()}`);
      return {
        ticker: ticker,
        error: 'データ取得エラー'
      };
    }
    
    const data = JSON.parse(response.getContentText());
    
    // データ検証
    if (!data.chart || !data.chart.result || data.chart.result.length === 0) {
      console.error(`Invalid data structure for ${ticker}`);
      return {
        ticker: ticker,
        error: 'データ形式エラー'
      };
    }
    
    const result = data.chart.result[0];
    
    if (!result.meta || !result.indicators || !result.indicators.quote) {
      console.error(`Missing required data for ${ticker}`);
      return {
        ticker: ticker,
        error: 'データ不足'
      };
    }
    
    const meta = result.meta;
    const quote = result.indicators.quote[0];
    const timestamps = result.timestamp;
    
    // 最新データ
    const lastIndex = timestamps.length - 1;
    const currentPrice = meta.regularMarketPrice;
    const previousClose = meta.previousClose;
    const change = currentPrice - previousClose;
    const changePercent = (change / previousClose) * 100;
    const currentVolume = meta.regularMarketVolume || (quote.volume ? quote.volume[lastIndex] : 0);
    
    // テクニカル指標計算
    const closes = quote.close ? quote.close.filter(val => val !== null) : [];
    const highs = quote.high ? quote.high.filter(val => val !== null) : [];
    const lows = quote.low ? quote.low.filter(val => val !== null) : [];
    
    const sma50 = calculateSMA(closes, 50);
    const rsi = calculateRSI(closes);
    const stochastic = calculateStochastic(highs, lows, closes);
    const macd = calculateMACD(closes);
    const volatility = calculateVolatility(closes);
    
    // デバッグ用ログ
    console.log(`${ticker} - Closes: ${closes.length}, RSI: ${rsi}, Stoch: ${JSON.stringify(stochastic)}, MACD: ${JSON.stringify(macd)}, Vol: ${volatility}`);
    
    const stockData = {
      ticker: ticker,
      name: CONFIG.PORTFOLIO[ticker].name,
      sector: CONFIG.PORTFOLIO[ticker].sector,
      currentPrice: currentPrice,
      change: change,
      changePercent: changePercent,
      volume: currentVolume,
      previousClose: previousClose,
      dayLow: meta.regularMarketDayLow,
      sma50: sma50,
      rsi: rsi,
      stochastic: stochastic,
      macd: macd,
      volatility: volatility,
      recommendation: getAdvancedRecommendation(currentPrice, sma50, rsi, stochastic, macd, volatility)
    };
    
    // キャッシュに保存（1時間）
    cache.put(cacheKey, JSON.stringify(stockData), 3600);
    
    return stockData;
    
  } catch(e) {
    console.error(`Error fetching ${ticker}:`, e);
    return {
      ticker: ticker,
      error: 'データ取得エラー'
    };
  }
}

function calculateSMA(values, period) {
  if (values.length < period) return null;
  const relevantValues = values.slice(-period);
  return relevantValues.reduce((a, b) => a + b, 0) / period;
}

function calculateRSI(values, period = 14) {
  if (values.length < period + 1) return null;
  
  let gains = 0;
  let losses = 0;
  
  for (let i = values.length - period; i < values.length; i++) {
    const change = values[i] - values[i - 1];
    if (change > 0) {
      gains += change;
    } else {
      losses -= change;
    }
  }
  
  const avgGain = gains / period;
  const avgLoss = losses / period;
  
  if (avgLoss === 0) return 100;
  
  const rs = avgGain / avgLoss;
  return 100 - (100 / (1 + rs));
}

function calculateStochastic(highs, lows, closes, period = 14) {
  if (highs.length < period || lows.length < period || closes.length < period) return null;
  
  const recentHighs = highs.slice(-period);
  const recentLows = lows.slice(-period);
  const currentClose = closes[closes.length - 1];
  
  const highestHigh = Math.max(...recentHighs);
  const lowestLow = Math.min(...recentLows);
  
  if (highestHigh === lowestLow) return { k: 50, d: 50 };
  
  const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
  
  return {
    k: k,
    d: k // 簡略化のため、%Dは%Kと同じ値を使用
  };
}

function calculateMACD(values) {
  if (values.length < 26) return null;
  
  const ema12 = calculateEMA(values, 12);
  const ema26 = calculateEMA(values, 26);
  
  if (!ema12 || !ema26) return null;
  
  const macdLine = ema12 - ema26;
  const signal = macdLine; // 簡略化のため、シグナルラインはMACDラインと同じ値を使用
  
  return {
    macd: macdLine,
    signal: signal,
    histogram: 0
  };
}

function calculateEMA(values, period) {
  if (values.length < period) return null;
  
  const k = 2 / (period + 1);
  let ema = values.slice(0, period).reduce((a, b) => a + b, 0) / period;
  
  for (let i = period; i < values.length; i++) {
    ema = values[i] * k + ema * (1 - k);
  }
  
  return ema;
}

function calculateVolatility(values, period = 20) {
  if (values.length < period) return null;
  
  const recentValues = values.slice(-period);
  const returns = [];
  
  for (let i = 1; i < recentValues.length; i++) {
    returns.push((recentValues[i] - recentValues[i-1]) / recentValues[i-1]);
  }
  
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
  const volatility = Math.sqrt(variance) * Math.sqrt(252) * 100; // 年率換算
  
  return volatility;
}

function getAdvancedRecommendation(price, sma50, rsi, stochastic, macd, volatility) {
  let signals = [];
  let marketType = 'normal'; // normal, high_volatility, low_volatility, trend, range
  
  // ボラティリティに基づく市場タイプの判定
  if (volatility > 40) {
    marketType = 'high_volatility';
  } else if (volatility < 15) {
    marketType = 'low_volatility';
  }
  
  // トレンド/レンジの判定
  if (macd && Math.abs(macd.macd) > 0.5) {
    marketType = marketType === 'high_volatility' ? 'high_volatility' : 'trend';
  } else if (volatility < 20 && stochastic) {
    marketType = 'range';
  }
  
  // 重み付けの動的調整
  let weights = {
    rsi: 0.40,
    stochastic: 0.35,
    macd: 0.20,
    sma: 0.05
  };
  
  // 市場タイプに応じた重み調整
  if (marketType === 'high_volatility') {
    weights.rsi = 0.50;
    weights.stochastic = 0.30;
    weights.macd = 0.15;
    weights.sma = 0.05;
  } else if (marketType === 'trend') {
    weights.rsi = 0.30;
    weights.stochastic = 0.25;
    weights.macd = 0.35;
    weights.sma = 0.10;
  } else if (marketType === 'range') {
    weights.rsi = 0.25;
    weights.stochastic = 0.50;
    weights.macd = 0.15;
    weights.sma = 0.10;
  }
  
  // RSI閾値の動的調整
  let rsiBuyThreshold = 30;
  let rsiSellThreshold = 70;
  
  if (marketType === 'high_volatility') {
    rsiBuyThreshold = 20;
    rsiSellThreshold = 80;
  } else if (marketType === 'low_volatility') {
    rsiBuyThreshold = 35;
    rsiSellThreshold = 65;
  }
  
  // スコア計算
  let totalScore = 0;
  
  // RSIスコア
  if (rsi) {
    let rsiScore = 0;
    if (rsi < rsiBuyThreshold) {
      rsiScore = 1.0;
      signals.push(`RSI売られすぎ(${rsi.toFixed(1)})`);
    } else if (rsi < 40) {
      rsiScore = 0.7;
    } else if (rsi < 60) {
      rsiScore = 0.5;
    } else if (rsi < rsiSellThreshold) {
      rsiScore = 0.3;
    } else {
      rsiScore = 0;
      signals.push(`RSI買われすぎ(${rsi.toFixed(1)})`);
    }
    totalScore += rsiScore * weights.rsi;
  }
  
  // ストキャスティクススコア
  if (stochastic) {
    let stochasticScore = 0;
    if (stochastic.k < 20) {
      stochasticScore = 1.0;
      signals.push(`Stoch売られすぎ(${stochastic.k.toFixed(1)})`);
    } else if (stochastic.k < 40) {
      stochasticScore = 0.7;
    } else if (stochastic.k < 60) {
      stochasticScore = 0.5;
    } else if (stochastic.k < 80) {
      stochasticScore = 0.3;
    } else {
      stochasticScore = 0;
      signals.push(`Stoch買われすぎ(${stochastic.k.toFixed(1)})`);
    }
    totalScore += stochasticScore * weights.stochastic;
  }
  
  // MACDスコア
  if (macd) {
    let macdScore = 0;
    if (macd.macd > 0 && macd.histogram >= 0) {
      macdScore = 1.0;
      signals.push('MACD上昇トレンド');
    } else if (macd.macd > 0) {
      macdScore = 0.7;
    } else if (macd.macd < 0 && macd.histogram >= 0) {
      macdScore = 0.5;
    } else {
      macdScore = 0.2;
    }
    totalScore += macdScore * weights.macd;
  }
  
  // SMA50スコア
  if (sma50 && price) {
    let smaScore = price > sma50 ? 1.0 : 0.3;
    if (price > sma50) {
      signals.push('50日線上');
    }
    totalScore += smaScore * weights.sma;
  }
  
  // 推奨判定
  let recommendation;
  if (totalScore >= 0.75) {
    recommendation = '強い買い';
  } else if (totalScore >= 0.60) {
    recommendation = '買い';
  } else if (totalScore >= 0.40) {
    recommendation = '様子見';
  } else if (totalScore >= 0.25) {
    recommendation = '売り検討';
  } else {
    recommendation = '売り';
  }
  
  // 市場タイプを信号に追加
  if (marketType !== 'normal') {
    signals.push(`市場: ${marketType === 'high_volatility' ? '高ボラティリティ' : 
                        marketType === 'low_volatility' ? '低ボラティリティ' :
                        marketType === 'trend' ? 'トレンド相場' : 'レンジ相場'}`);
  }
  
  return {
    score: totalScore,
    recommendation: recommendation,
    signals: signals,
    marketType: marketType,
    weights: weights
  };
}

// ========== ユーティリティ関数 ==========
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

// ========== ログビューアHTML ==========
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
          '<div style="margin-bottom: 8px;">• ' + a.type + ': ' + a.user + ' (' + a.count + '回)</div>'
        ).join('');
      }
      
      // 初回読み込み
      loadLogStats();
      
      // 30秒ごとに更新
      setInterval(loadLogStats, 30000);
    </script>
  `;
}

// ========== 自動更新トリガー設定 ==========
function setupDailyTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'dailyUpdate') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 新しいトリガーを設定（毎日午前6時）
  ScriptApp.newTrigger('dailyUpdate')
    .timeBased()
    .everyDays(1)
    .atHour(6)
    .create();
    
  console.log('日次更新トリガーを設定しました（毎日午前6時）');
}

function dailyUpdate() {
  // キャッシュをクリア
  const cache = CacheService.getScriptCache();
  cache.remove('integrated_portfolio_data');
  
  // データを再取得
  getIntegratedPortfolioData();
  
  // ログに記録
  logAccess('自動更新', '日次データ更新を実行');
  
  console.log('日次更新が完了しました:', new Date());
}

// ========== 初期設定 ==========
function setupInitial() {
  // Drive権限の確認
  if (CONFIG.DRIVE_FOLDER_ID) {
    try {
      const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
      console.log('Driveフォルダ確認OK:', folder.getName());
    } catch(e) {
      console.error('Driveフォルダアクセスエラー:', e);
    }
  }
  
  // ログシートの作成
  getOrCreateLogSheet();
  console.log('ログシート確認OK');
  
  // 日次更新トリガーの設定
  setupDailyTrigger();
  
  console.log('初期設定が完了しました');
}

// ========== テスト関数 ==========
function testFetchStockData() {
  // 特定のティッカーでテスト
  const result = fetchStockData('TSLA');
  console.log('Test result for TSLA:', JSON.stringify(result));
}

function testGetPortfolioData() {
  // ポートフォリオデータ取得のテスト
  const result = getIntegratedPortfolioData();
  console.log('Portfolio data:', JSON.stringify(result));
}

function clearAllCache() {
  // 全キャッシュをクリア
  const cache = CacheService.getScriptCache();
  cache.removeAll(['integrated_portfolio_data']);
  
  // 個別銘柄のキャッシュもクリア
  for (const ticker in CONFIG.PORTFOLIO) {
    cache.remove(`stock_${ticker}`);
  }
  
  console.log('All cache cleared successfully');
}