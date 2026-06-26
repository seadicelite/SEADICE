個人事業をやっていると、毎日同じことを手動でやり続けるのは非常に非効率だ。X（Twitter）への投稿、YouTubeへの動画アップロード、ブログの更新——これらを全部手動でやっていたら、開発や営業に使う時間がなくなってしまう。

そこで活躍するのが**cron**だ。Macでもサーバーでも使える標準の定期実行ツールで、設定さえすれば毎日決まった時間にスクリプトを自動実行してくれる。この記事では、SEADICEでの実践例をもとにcronの使い方を詳しく解説する。

## cronとは何か

cronはUnix系OS（Mac・Linux）に標準搭載されているジョブスケジューラーだ。「毎日8時にこのスクリプトを実行する」「毎週月曜の朝にこの処理をする」といった定期実行を、サーバーもクラウドサービスも不要で実現できる。

Macを起動している間は常にcronデーモンが動いているため、設定した時間になると自動的にスクリプトが実行される。

## crontabの書き方

cronの設定は`crontab`というファイルで管理する。ターミナルで以下を実行すると編集できる。

```bash
crontab -e
```

設定の書き方はこうだ。

```
分 時 日 月 曜日 コマンド
```

具体例：

```bash
# 毎日8時にtweet.pyを実行
0 8 * * * /usr/bin/python3 /Users/username/x-auto/tweet.py

# 毎日12時と18時にも実行
0 12 * * * /usr/bin/python3 /Users/username/x-auto/tweet.py
0 18 * * * /usr/bin/python3 /Users/username/x-auto/tweet.py

# 毎朝7時にYouTube動画をアップロード
0 7 * * * cd /Users/username/youtube-auto && /usr/bin/python3 upload.py

# 毎晩23時にブログ記事を自動生成
0 23 * * * /usr/bin/python3 /Users/username/blog-auto/generate.py
```

`*`はワイルドカードで「毎回」を意味する。曜日は0が日曜、1が月曜……6が土曜だ。

## SEADICEでの実際のcron設定

現在SEADICEで動いているcronはこうなっている。

```bash
# YouTube自動投稿（毎朝7時）
0 7 * * * cd /Users/hidenori/Developer/youtube-auto && /usr/bin/python3 upload.py

# X自動投稿（8時・12時・18時）
0 8 * * * cd /Users/hidenori/Developer/x-auto && /usr/bin/python3 tweet.py
0 12 * * * cd /Users/hidenori/Developer/x-auto && /usr/bin/python3 tweet.py
0 18 * * * cd /Users/hidenori/Developer/x-auto && /usr/bin/python3 tweet.py

# ブログ自動生成（毎晩23時）
0 23 * * * /usr/bin/python3 /Users/hidenori/Developer/SEADICE/blog-admin/generate.py >> /Users/hidenori/Developer/SEADICE/blog-admin/generate.log 2>&1
```

これだけで毎日のSNS発信とブログ更新が全自動で回る。

## cronでハマりやすいポイント

### 1. Pythonのパスはフルパスで指定する

cronは通常のターミナルとは異なる環境で実行されるため、`python3`だけでは認識されないことがある。必ず`which python3`で確認したフルパスを使う。

```bash
which python3
# → /usr/bin/python3
```

### 2. カレントディレクトリが違う

cronで実行されるスクリプトは、カレントディレクトリが予期しない場所になっていることがある。スクリプト内でファイルを参照する場合は、絶対パスを使うか、`cd`でディレクトリを移動してから実行する。

```bash
# cdしてから実行する方法
0 8 * * * cd /Users/hidenori/Developer/x-auto && /usr/bin/python3 tweet.py
```

### 3. 環境変数が引き継がれない

`.env`ファイルや`~/.zshrc`で設定した環境変数はcronには引き継がれない。スクリプト内で明示的に読み込む必要がある。

Pythonの場合はこう書く。

```python
from pathlib import Path

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()
```

### 4. ログを必ず残す

cronが正常に動いているか確認するために、ログファイルに出力を残す。

```bash
0 23 * * * /usr/bin/python3 /path/to/script.py >> /path/to/script.log 2>&1
```

`>> log.log`で標準出力をログに追記、`2>&1`でエラー出力も同じファイルに書く。

### 5. Macのスリープ問題

Macがスリープ中はcronが実行されない。夜中にスリープするMacでcronを動かしたい場合は、**システム設定 → バッテリー → スケジュール**から自動起動の時間を設定するか、`pmset`コマンドを使う。

```bash
# 毎日22時55分に自動起動（cronの5分前）
sudo pmset repeat wakeorpoweron MTWRFSU 22:55:00
```

## ログの確認方法

cronが正常に動いているか確認するには、ログファイルを見るのが一番確実だ。

```bash
# ログをリアルタイムで確認
tail -f /Users/hidenori/Developer/SEADICE/blog-admin/generate.log

# 最新20行を確認
tail -20 /Users/hidenori/Developer/SEADICE/blog-admin/generate.log
```

システムのcronログはこちらで確認できる。

```bash
log show --predicate 'subsystem == "com.apple.xpc.launchd"' --last 1h | grep cron
```

## Macでcronが動かない場合の対処

macOS Catalina以降、cronがフルディスクアクセス権限を要求することがある。

**システム設定 → プライバシーとセキュリティ → フルディスクアクセス**に`cron`を追加すると解決することが多い。

また、`launchd`（MacのcronをラップするApple独自のサービス）を使う方法もある。こちらの方がMacでは信頼性が高い。

```bash
# launchdのplistファイルを作成
# ~/Library/LaunchAgents/com.seadice.blog.plist
```

## まとめ

cronは設定さえすれば完全に自動で動き続ける、個人事業主にとって最高のツールだ。

- **書き方**: `分 時 日 月 曜日 コマンド`
- **注意点**: フルパス・絶対パス・環境変数の手動読み込み
- **確認方法**: ログファイルを残す
- **Mac固有の問題**: スリープ対策とフルディスクアクセス権限

SEADICEではX投稿・YouTube投稿・ブログ生成の3つをcronで自動化している。これにより、発信にかかる時間をほぼゼロにしながら毎日の更新を維持できている。

自動化の初期投資（設定の時間）は数時間だが、その後は何もしなくても動き続ける。個人事業で時間を作りたいなら、まずcronから始めることをおすすめする。
