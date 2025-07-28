// タブ切り替え機能
function showSection(sectionId) {
    // すべてのセクションを非表示
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // すべてのタブを非アクティブ
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // 選択されたセクションを表示
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // 選択されたタブをアクティブ
    event.target.classList.add('active');
}

// 画像フルスクリーン機能
function toggleFullscreen(img) {
    if (document.fullscreenElement) {
        document.exitFullscreen();
        img.classList.remove("fullscreen");
    } else {
        var div = document.createElement("div");
        div.className = "fullscreen";
        div.onclick = function() {
            document.body.removeChild(div);
        };
        var newImg = img.cloneNode(true);
        newImg.onclick = function(e) {
            e.stopPropagation();
        };
        div.appendChild(newImg);
        document.body.appendChild(div);
    }
}

// スムーズスクロール
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// レスポンシブナビゲーション
function toggleMobileNav() {
    const navTabs = document.querySelector('.nav-tabs');
    navTabs.classList.toggle('mobile-open');
}

// 検索機能
function searchStocks(query) {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        const tabText = tab.textContent.toLowerCase();
        if (tabText.includes(query.toLowerCase()) || query === '') {
            tab.style.display = 'block';
        } else {
            tab.style.display = 'none';
        }
    });
}

// 討論セクション切り替え
function showDiscussionSection(ticker, expertType) {
    // すべての討論コンテンツを非表示
    const discussionContents = document.querySelectorAll(`#${ticker}-discussion .discussion-content`);
    discussionContents.forEach(content => content.classList.remove('active'));
    
    // すべての討論タブを非アクティブ
    const discussionTabs = document.querySelectorAll(`#${ticker}-discussion .discussion-tab`);
    discussionTabs.forEach(tab => tab.classList.remove('active'));
    
    // 選択されたコンテンツを表示
    const targetContent = document.getElementById(`${ticker}-discussion-${expertType}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // 選択されたタブをアクティブ
    event.target.classList.add('active');
}

// アニメーション効果
function animateValue(element, start, end, duration = 1000) {
    const startTimestamp = performance.now();
    
    function updateValue(timestamp) {
        const elapsed = timestamp - startTimestamp;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * progress;
        element.textContent = current.toFixed(2);
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// データ更新通知
function showUpdateNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// パフォーマンス監視
function measurePerformance() {
    if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        console.log(`ページ読み込み時間: ${loadTime}ms`);
    }
}

// エラーハンドリング
function handleError(error) {
    console.error('エラーが発生しました:', error);
    showUpdateNotification('データの取得に失敗しました。しばらく後にお試しください。');
}

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('ハイブリッドレポート読み込み完了');
    measurePerformance();
    
    // キーボードショートカット
    document.addEventListener('keydown', function(e) {
        if (e.altKey) {
            const keyMap = {
                '1': 'overview',
                '2': 'optimization',
                '3': 'tsla',
                '4': 'fslr',
                '5': 'rklb',
                '6': 'asts',
                '7': 'oklo',
                '8': 'joby',
                '9': 'oii'
            };
            
            if (keyMap[e.key]) {
                e.preventDefault();
                showSection(keyMap[e.key]);
            }
        }
    });
    
    // レスポンシブデザイン対応
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    function handleMediaQuery(e) {
        if (e.matches) {
            // モバイル表示の調整
            document.body.classList.add('mobile-view');
        } else {
            document.body.classList.remove('mobile-view');
        }
    }
    
    mediaQuery.addListener(handleMediaQuery);
    handleMediaQuery(mediaQuery);
});