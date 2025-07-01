# 【保存版】新しいPCでの開発環境構築手順書

新しいPCで、快適な開発環境を再現するための手順書です。

---

### フェーズ1：基礎システムの準備 (Windows & WSL)

1.  **Windows Updateの実行**
    -   何よりもまず、新しいPCのWindows Updateを最新の状態になるまで実行します。セキュリティと安定性のための基本です。

2.  **WSLとUbuntuのインストール (1コマンドで完了)**
    -   Windowsのスタートメニューから「**PowerShell**」または「**ターミナル**」を探し、**右クリックして「管理者として実行」** を選択します。
    -   開いた黒い画面で、以下の魔法のコマンドを1行入力してEnterキーを押します。

        ```powershell
        wsl --install -d Ubuntu-22.04
        ```
    -   **解説:** この1コマンドだけで、Windowsが必要とする仮想化機能を有効にし、WSLをインストールし、さらにMicrosoft Storeから `Ubuntu-22.04` をダウンロードしてインストールする、という全工程を自動で行ってくれます。
    -   完了後、PCの再起動を求められたら、指示に従って再起動してください。

---

### フェーズ2：Ubuntuの初期設定

1.  **Ubuntuの初回起動とユーザー作成**
    -   再起動後、Windowsのスタートメニューから「**Ubuntu 22.04 LTS**」を起動します。
    -   初回起動時に自動でセットアップが走り、**UNIXユーザー名とパスワードの作成**を求められます。指示に従って設定してください。

2.  **システム全体のアップデート**
    -   `username@...:~$` というプロンプトが表示されたら、まず以下のコマンドでUbuntuのシステム全体を最新の状態にします。これは新しい環境を作った際の「お作法」のようなものです。

        ```bash
        sudo apt update && sudo apt upgrade -y
        ```
    -   パスワードを求められたら、先ほど作成したものを入力します。

---

### フェーズ3：開発ツールのインストール

ここからの作業は、すべて **Ubuntuのターミナル内** で行います。

1.  **基本ツールのインストール**
    -   `nvm`のインストーラーや、その他多くのツールで必要となる基本的なツールを先にインストールしておきます。

        ```bash
        sudo apt install -y curl build-essential git
        ```

2.  **`nvm` と `Node.js` のインストール**
    -   `nvm`（Node Version Manager）をインストールし、それを使ってNode.jsをインストールします。

        ```bash
        # nvmのインストール
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

        # nvmを有効化
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

        # 最新のLTS版Node.jsをインストール
        nvm install --lts
        ```

3.  **`claude-code` のインストール**
    -   最後に、目的の `claude-code` をグローバルインストールします。（`nvm`で入れたので `sudo` は不要です。）

        ```bash
        npm install -g @anthropic-ai/claude-code
        ```

---

### フェーズ4：Cursorとの連携

1.  **Cursorのインストール**
    -   Webブラウザで [Cursorの公式サイト](https://cursor.sh/) にアクセスし、インストーラーをダウンロードしてWindowsにインストールします。

2.  **Cursorのターミナル設定**
    -   Cursorを起動し、`Ctrl` + `,` で設定を開きます。
    -   検索窓に `terminal.integrated.defaultProfile.windows` と入力します。
    -   ドロップダウンメニューから **`Ubuntu-22.04`** を選択します。
    -   `Ctrl` + `@` で新しいターミナルを開き、プロンプトがUbuntuのものになっていることを確認します。
    -   `claude` と入力して、正常に起動すれば**すべての設定が完了**です！ 