# mozc-character-pad: 文字パレット / 手書き入力パレット

## (a) これは何か

Google 日本語入力 (mozc) にかつて同梱されていた 2 つの GUI ツール、

- **character_palette**（文字パレット）: Unicode / Shift-JIS(CP932) / JIS X 0201 / 0208 / 0212
  の各種文字表から文字を探して選択するツール
- **hand_writing**（手書き入力パレット）: マウス/タッチで手書きした文字を認識し、候補を選ぶツール
  （[zinnia](https://taku910.github.io/zinnia/) による手書き文字認識を使用）

を、mozc 変換エンジン本体（mozc_server）のビルドやインストールなしに、単体の Qt6 デスクトップ
アプリケーションとしてビルドできるように切り出したものです。

## (b) 何を元にしたか

- 元プロジェクト: [google/mozc](https://github.com/google/mozc)
- 元にしたソース時点: コミット `afb03ddfe72dde4cf2409863a3bfea160f7a66d8`（2018-02-26 時点）
- 対象ソース: `src/gui/character_pad/`, `src/handwriting/`, `src/gui/base/`（一部）,
  `src/gui/dictionary_tool/zero_width_splitter.*`, `src/base/`（一部）,
  `src/data/unicode/` の Unicode/JIS マッピングデータ
- これら 2 ツールは mozc 本体から 2020-08-22 のコミット
  `a1dcadabd3a1c604e8beff1e45830c1d9adfce84` で削除されました。本プロジェクトはその直前の
  ソースを元に、mozc 本体（mozc_server との IPC）への依存を切り離して復元したものです。

## (c) 元との違い（重要な設計変更）

1. **mozc_server への直接送信を廃止し、クリップボードコピーに変更**
   元のコードは `client::ClientFactory::NewClient()` で生成したクライアントの
   `SendCommand()` を使って、選択した文字や手書き認識結果を IME の入力として mozc_server に
   直接送信していました（`character_palette.cc`, `hand_writing.cc` 内）。
   本プロジェクトではこの機能を完全に削除し、代わりに文字/候補をクリックすると
   `QApplication::clipboard()->setText()` でクリップボードにコピーするだけの動作にしています
   （`gui/character_pad/selection_handler.cc` の `CopyToClipboardCallback`。元のソースの
   デフォルト動作がすでにクリップボードコピーだったため、この部分の実装自体は変更していません）。
   これにより `client/`, `protocol/commands.pb.h`, `protocol/config.pb.h`,
   `config/config_handler.h`, `config/stats_config_util.h` への依存を完全に無くしています。
   また、mozc converter への「使用状況統計(usage stats)」イベント送信も、mozc_server との
   通信を前提とする機能なのであわせて削除しました。
2. **クラウド手書き認識機能を削除**
   `hand_writing.cc` にあった `SetConfig`/`GetConfig`/`IsCloudHandwritingAllowed` や、
   クラウド手書き認識に切り替えるコンボボックス操作、`handwriting/cloud_handwriting.{cc,h}`
   は同梱・使用していません。手書き認識は zinnia によるローカル認識のみです
   （`ENABLE_CLOUD_HANDWRITING` マクロを定義しないことで、元のコードのその分岐自体は
   到達不能になりますが、コードの見通しのため `hand_writing.cc`/`.h` から明示的に除去して
   あります）。
3. **Windows 専用のキー入力送信コード（`windows_selection_handler.*`）は同梱しているものの、
   Linux 向けの CMake ビルドではコンパイル対象から除外**しています（中身は `#ifdef OS_WIN`
   で完全にガードされているため、他プラットフォームでは元々何もしません）。
4. ビルドシステムを元の GYP から CMake に置き換えています。Unicode/JIS データからヘッダを
   生成する Python スクリプト（`gen_cp932_map.py` など）は元は Python 2 で書かれていましたが、
   本プロジェクトでは Python 3 に移植したものを同梱しています（生成される内容は同一です）。

上記以外の UI・文字表示・手書きキャンバスの描画・zinnia 認識ロジックなどは、元のソースをほぼ
そのまま利用しています。

## (d) 依存パッケージとビルド手順

### 必要なパッケージ (Ubuntu/Debian系)

```
sudo apt-get install -y \
    build-essential cmake pkg-config python3 \
    qt6-base-dev qt6-base-dev-tools \
    libzinnia-dev
```

Ubuntu のバージョンによっては `uic`/`rcc` 等の開発ツールが `qt6-base-dev-tools` ではなく
`qt6-tools-dev-tools` に入っている場合があります。`qt6-base-dev` だけで `uic`/`moc`/`rcc` が
入っていないようであれば、上記のいずれかを追加でインストールしてください。

