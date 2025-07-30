// デバッグ用テスト関数

function debugTestSingleStock() {
  console.log('=== Testing TSLA ===');
  const result = fetchStockData('TSLA');
  console.log('Result:', JSON.stringify(result, null, 2));
  
  // 各値を個別に確認
  console.log('RSI:', result.rsi);
  console.log('Stochastic:', result.stochastic);
  console.log('MACD:', result.macd);
  console.log('Volume:', result.volume);
  console.log('Volatility:', result.volatility);
}

function debugTestCalculations() {
  // テスト用データ
  const testCloses = [100, 102, 101, 103, 104, 102, 105, 107, 106, 108, 110, 109, 111, 113, 112, 114, 116, 115, 117, 119];
  const testHighs = [101, 103, 102, 104, 105, 103, 106, 108, 107, 109, 111, 110, 112, 114, 113, 115, 117, 116, 118, 120];
  const testLows = [99, 101, 100, 102, 103, 101, 104, 106, 105, 107, 109, 108, 110, 112, 111, 113, 115, 114, 116, 118];
  
  console.log('=== Testing Calculations ===');
  console.log('Test data length:', testCloses.length);
  
  const rsi = calculateRSI(testCloses);
  console.log('RSI:', rsi);
  
  const stoch = calculateStochastic(testHighs, testLows, testCloses);
  console.log('Stochastic:', stoch);
  
  const macd = calculateMACD(testCloses);
  console.log('MACD:', macd);
  
  const vol = calculateVolatility(testCloses);
  console.log('Volatility:', vol);
}

function debugCheckYahooData() {
  console.log('=== Checking Yahoo Finance Response ===');
  
  try {
    const url = 'https://query2.finance.yahoo.com/v8/finance/chart/TSLA';
    const response = UrlFetchApp.fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      muteHttpExceptions: true
    });
    
    const data = JSON.parse(response.getContentText());
    console.log('Response code:', response.getResponseCode());
    
    if (data.chart && data.chart.result && data.chart.result[0]) {
      const result = data.chart.result[0];
      console.log('Meta data exists:', !!result.meta);
      console.log('Quote data exists:', !!result.indicators?.quote?.[0]);
      
      if (result.indicators?.quote?.[0]) {
        const quote = result.indicators.quote[0];
        console.log('Close data length:', quote.close ? quote.close.length : 0);
        console.log('High data length:', quote.high ? quote.high.length : 0);
        console.log('Low data length:', quote.low ? quote.low.length : 0);
        console.log('Volume data length:', quote.volume ? quote.volume.length : 0);
        
        // 最後の10個のデータを確認
        if (quote.close && quote.close.length > 10) {
          console.log('Last 10 close prices:', quote.close.slice(-10));
        }
      }
    }
  } catch (e) {
    console.error('Error:', e);
  }
}

// 全体的なデバッグ
function debugFullTest() {
  console.log('=== FULL DEBUG TEST ===');
  
  // Yahoo Financeの生データ確認
  debugCheckYahooData();
  
  console.log('\n');
  
  // 計算関数のテスト
  debugTestCalculations();
  
  console.log('\n');
  
  // 実際の株価データでテスト
  debugTestSingleStock();
}