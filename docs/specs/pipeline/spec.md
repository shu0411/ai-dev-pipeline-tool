# Feature Spec: AI Dev Pipeline Tool 外部リポジトリ連携対応

---

## 1. 背景

AIを活用した開発において、以下の課題がある：

- 仕様が曖昧なまま実装が進む
- テストが後付けになり品質が安定しない
- AIが勝手に次工程まで進んでしまう
- 人間の承認を挟む仕組みが弱い

既存のツールはフェーズ管理（spec → test → code）を提供しているが、
AIの実行は手動で行う必要があった。

本機能では、以下を追加し、ツールを AI 開発のオーケストレーターとして拡張する。

- 別リポジトリを対象に初期化できること
- CLI から Codex CLI を呼び出してテスト・実装を実行できること
- 対象リポジトリ内の状態ファイルで現在状態を確認できること

---

## 2. スコープ

### In Scope

- 外部リポジトリの指定と初期化
- 対象リポジトリが Git リポジトリであることの検証
- 状態ファイルを対象リポジトリ内に作成
- Codex CLI の呼び出し
- テスト生成・実装生成のコマンド提供
- フェーズ制御（spec → test → code）
- プロンプト生成責務と Codex 実行責務の分離

### Out of Scope

- Web UI / GUI
- DB
- マルチユーザー対応
- CI/CD統合
- 自動承認
- PR作成
- 実行履歴の永続化
- Codex CLI 以外の AI 実行基盤対応

---

## 3. ユーザーストーリー

- ユーザーとして、別アプリのリポジトリを対象に開発を管理したい
- ユーザーとして、CLI コマンドで AI にテストや実装を依頼したい
- ユーザーとして、フェーズを強制しながら安全に AI 開発を進めたい
- ユーザーとして、Codex 呼び出し部分だけを差し替え可能にしてテストしやすくしたい

---

## 4. 機能要件

1. 対象リポジトリを指定して初期化できる
2. 対象リポジトリが Git リポジトリであることを検証する
3. 状態ファイルを対象リポジトリ内に作成する
4. フェーズ状態を管理する
5. フェーズ承認を行える
6. Codex CLI を呼び出せる
7. テスト生成コマンドを提供する
8. 実装生成コマンドを提供する
9. spec ファイルの存在をチェックする
10. CLI から AI 実行をトリガーできる
11. プロンプト生成処理を Codex 実行処理から分離する
12. Codex 実行処理はテスト時にスタブ可能な構造にする

---

## 5. 非機能要件

- Python 3.11+
- CLI のみ
- ファイルベース状態管理
- subprocess による外部コマンド実行
- Codex CLI がインストールされている前提
- テスト容易性を重視した責務分離
- 実装詳細に引っ張られにくいテストが書けること

---

## 6. フェーズ制御

```text
spec → test → code
````

- spec 未承認 → `run tests` 禁止
- tests 未承認 → `run code` 禁止
- フェーズスキップ禁止
- `run tests` / `run code` 実行後も phase は更新しない
- phase の更新は承認コマンド実行時のみ行う

---

## 7. 状態管理

### 保存場所

```text
<target_repo>/.ai-dev-pipeline/state.json
```

### state.json

```json
{
  "feature_name": "todo-app",
  "spec_path": "docs/specs/todo-app/spec.md",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

### 状態管理方針

- 状態ファイルはフェーズ管理のみに使用する
- 実行結果や履歴は保存しない
- `spec_path` は相対パスで保存する
- 入力としては絶対パス / 相対パスの両方を許可する

---

## 8. CLI仕様

### 初期化

```bash
init --repo <path> --feature <name> --spec <path>
```

### 状態確認

```bash
show-status --repo <path>
```

### 承認

```bash
approve spec --repo <path>
approve tests --repo <path>
```

### AI実行

```bash
run tests --repo <path>
run code --repo <path>
```

---

## 9. モジュール責務

### `cli.py`

責務：

- 引数解釈
- 状態判定
- フェーズ制御の適用
- 対象リポジトリや spec ファイルの事前チェック
- `prompt_builder.py` / `codex_runner.py` の呼び出し

### `prompt_builder.py`

責務：

- task_type と spec_path から Codex に渡すプロンプト文字列を生成する

### `codex_runner.py`

責務：

- Codex CLI の実行のみを担当する
- subprocess 呼び出しをラップする
- 成功時は `RunResult` を返し、失敗時は `RuntimeError` を送出する

### `state.py`

責務：

- 状態ファイルの読み書き

### `workflow.py`

責務：

- フェーズ遷移と承認ロジック

---

## 10. prompt_builder 設計

### 公開API(build_prompt)

```python
build_prompt(task_type: str, spec_path: str) -> str
```

### 要件

- 純粋関数として実装する
- 外部コマンド実行やファイル書き込みを行わない
- `task_type` に応じてテスト生成用 / 実装生成用のプロンプトを返す
- spec_path をプロンプト内に明示する

### 想定 task_type

- `tests`
- `code`

---

## 11. codex_runner 設計

### 公開API(run_codex)

```python
run_codex(
    task_type: str,
    repo_path: Path,
    prompt: str,
    executor: Callable[..., CompletedProcessLike] | None = None
) -> RunResult
```

### RunResult

```python
@dataclass(frozen=True)
class RunResult:
    task_type: str
    stdout: str
```

### 方針

- 成功時のみ `RunResult` を返す
- 非0終了は戻り値で表現せず例外に統一する
- `executor` はテスト時にスタブ注入できるようにする
- `executor` 未指定時はデフォルト実装を使う

### エラー契約

- Codex CLI が見つからない → `RuntimeError`
- 終了コード != 0 → `RuntimeError`
- spec 未存在 → `cli.py` で事前エラー

---

## 12. Codex CLI 実行契約

### subprocess仕様

- 実行ファイル: `codex`
- プロンプト: 引数で渡す
- `cwd`: 対象リポジトリ
- `check`: `False`
- 標準出力は取得する
- 非0終了は `RuntimeError` に変換する

### 想定実装

```python
subprocess.run(
    ["codex", prompt],
    cwd=repo_path,
    capture_output=True,
    text=True,
    check=False
)
```

### エラー処理

```python
if completed.returncode != 0:
    raise RuntimeError("Codex CLI execution failed")
```

---

## 13. プロンプト生成仕様

### `run tests`

以下を含むこと：

- spec を読むこと
- テストのみ作成すること
- pytest を使うこと
- 正常系 / 異常系 / 境界値を含めること
- 実装コードは変更しないこと
- 不明点を最後に列挙すること

### `run code`

以下を含むこと：

- spec と既存テストを読むこと
- 実装のみを行うこと
- テストを通すこと
- 仕様外変更をしないこと
- 不明点を最後に列挙すること

---

## 14. フォルダ構成

### 本ツール側

```text
ai-dev-pipeline-tool/
  src/
    ai_dev_pipeline_tool/
      cli.py
      state.py
      workflow.py
      prompt_builder.py
      codex_runner.py
      paths.py
  tests/
    test_state.py
    test_workflow.py
    test_prompt_builder.py
    test_codex_runner.py
    test_cli.py
  docs/
    specs/
      pipeline/
        spec.md
```

### 対象リポジトリ側

```text
target-app/
  docs/
    specs/
      <feature-name>/
        spec.md
  .ai-dev-pipeline/
    state.json
```

---

## 15. テスト観点

### 正常系

- 対象リポジトリを指定して初期化できる
- 対象リポジトリが Git リポジトリであることを検証できる
- `build_prompt()` が task_type に応じた文面を返す
- `run_codex()` が Codex CLI を正しく呼ぶ
- `cwd` が対象リポジトリになる
- `run tests` / `run code` が適切なフェーズでのみ実行できる

### 異常系

- spec 未承認で `run tests`
- tests 未承認で `run code`
- 対象リポジトリが存在しない
- 対象が Git リポジトリでない
- spec ファイルが存在しない
- Codex CLI が見つからない
- Codex CLI が非0終了する

### 境界値

- state.json 欠損
- state.json 不正
- spec_path が相対パス
- spec_path 入力が絶対パス

### テスト容易性

- `prompt_builder.py` は subprocess を意識せず単独でテストできる
- `codex_runner.py` は executor をスタブ注入してテストできる
- `cli.py` は AI 実行詳細ではなく責務境界中心にテストできる

---

## 16. 制約

- CLI のみ
- DB 禁止
- GUI 禁止
- spec ファイル自体は変更しない
- state は対象リポジトリ内のみ
- Codex CLI のインストールはツール側で行わない

---

## 17. 完了条件

- 外部リポジトリを初期化できる
- Git リポジトリ検証が機能する
- フェーズ管理が機能する
- `prompt_builder.py` と `codex_runner.py` の責務が分離されている
- Codex CLI を呼び出せる
- テスト生成・実装生成が実行できる
- 不正操作が適切にエラーになる
- 実装詳細に依存しすぎないテストを書ける
