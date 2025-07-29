# Tiker 設定ガイド

## 通信エラー解決済み設定

### 1. 仮想環境のセットアップ（初回のみ）

```bash
# 1. 仮想環境作成
uv venv venv

# 2. 依存関係インストール
source venv/bin/activate
uv pip install -r requirements.txt
```

### 2. レポート生成の実行方法

```bash
# 環境アクティベート + レポート生成
source venv/bin/activate
PYTHONPATH=. python src/portfolio/portfolio_master_report_hybrid.py
```

### 3. 便利スクリプト

- `activate.sh`: 仮想環境を簡単にアクティベート
- `run_with_venv.sh`: 仮想環境内でコマンド実行

### 4. よくある問題と解決策

**問題**: `ModuleNotFoundError: No module named 'yfinance'`  
**解決**: 仮想環境をアクティベートして依存関係を再インストール

**問題**: `ModuleNotFoundError: No module named 'src'`  
**解決**: `PYTHONPATH=.` を付けて実行

**問題**: 毎回依存関係がリセットされる  
**解決**: 作成した `venv/` フォルダを使用（永続化済み）

### 5. 生成されるファイル

- チャート: `charts/{TICKER}_chart_{DATE}.png`  
- HTMLレポート: `reports/html/portfolio_hybrid_report_{DATE}.html`  
- 討論レポート: `reports/{TICKER}_discussion_{DATE}.md`

### 6. MCP設定（必要に応じて）

Claude Code の設定を永続化する場合：
```bash
# cctx ツールで設定管理
cctx save tiker-project
cctx use tiker-project
```