# AI Dev Pipeline Tool

`AI Dev Pipeline Tool` は、AI を使った開発を次の順序で段階管理する CLI ツールです。

```text
spec -> test -> code
```

各フェーズは人間の承認がない限り先へ進めません。  
AI が勝手に次工程へ進むことを防ぎながら、仕様確認、テスト確認、実装を順番に進めるための最小構成のツールです。

## できること

* 現在のフェーズを `state.json` で管理する
* `init` で作業状態を初期化する
* `show-status` で現在の状態を確認する
* `approve spec` で `spec` を承認し、`test` に進める
* `approve tests` で `test` を承認し、`code` に進める
* 不正なフェーズ遷移をブロックする

## プロジェクト構成

```text
src/ai_dev_pipeline_tool/
    cli.py
    state.py
    workflow.py

tests/
    test_state.py
    test_workflow.py
    test_cli.py

docs/specs/
    pipeline/spec.md

workspace/current/
    state.json
```

## 利用例

このツールは、このリポジトリ自身の開発だけでなく、別のアプリ開発リポジトリで「仕様 -> テスト -> 実装」を管理する用途を想定しています。

たとえば、別リポジトリに次のような仕様書があるとします。

```text
docs/specs/todo-app/spec.md
```

この仕様をもとに AI と一緒にアプリを開発する場合、流れは次のようになります。

### 1. 仕様を用意し、人が内容を確認する

まず人が仕様書を確認し、今回の作業対象を明確にします。  
この段階では、まだテスト作成や実装には進みません。

### 2. ツールを初期化する

`init` を実行して状態を初期化します。  
初期フェーズは `spec` です。

### 3. AI に仕様を渡し、まずテストだけ作らせる

仕様が固まっている前提で、AI にはまずテストだけを作らせます。  
ここでは実装コードを書かせないのがポイントです。

依頼の例:

```text
docs/specs/todo-app/spec.md を読んでください。
今回は pytest のテストのみを作成してください。
実装コードは変更しないでください。
```

### 4. 人がテスト方針を確認し、問題なければ `spec` を承認する

人が「この仕様理解でテスト作成へ進んでよい」と判断したら、`approve spec` を実行します。  
これによりフェーズは `test` に進みます。

### 5. AI に実装を依頼する

テストが揃ったあと、AI に「既存テストを満たす実装」を依頼します。  
この段階で初めて実装作業に入ります。

依頼の例:

```text
既存の pytest テストをすべて通すように実装してください。
仕様に書かれていない機能は追加しないでください。
```

### 6. 人が実装結果を確認し、問題なければ `tests` を承認する

人がテスト内容と実装結果を確認し、実装へ進めてよいと判断したら `approve tests` を実行します。  
これによりフェーズは `code` に進みます。

### 7. 状態を見ながら進行管理する

途中で `show-status` を使えば、現在どのフェーズにいるかを確認できます。  
これにより、AI に次に何を依頼してよいかを明確に保てます。

## CLI の使い方

### 初期化

作業状態を初期化し、`workspace/current/state.json` を作成します。

```powershell
python -m ai_dev_pipeline_tool.cli init
```

初期状態は次のとおりです。

```json
{
  "feature_name": "pipeline",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

### 現在状態の確認

現在のフェーズと承認状態を表示します。

```powershell
python -m ai_dev_pipeline_tool.cli show-status
```

### `spec` の承認

`spec` フェーズを承認し、次の `test` フェーズへ進めます。

```powershell
python -m ai_dev_pipeline_tool.cli approve spec
```

### `test` の承認

`test` フェーズを承認し、次の `code` フェーズへ進めます。

```powershell
python -m ai_dev_pipeline_tool.cli approve tests
```

## フェーズ遷移ルール

フェーズは必ず次の順序で進みます。

```text
spec -> test -> code
```

次の操作はエラーになります。

* `spec` 未承認のまま `approve tests` を実行する
* 定義されていないフェーズを承認しようとする
* すでに通過したフェーズを再承認しようとする
* `spec` から `code` へスキップしようとする
* 初期化前に状態依存コマンドを実行する

## 状態ファイル

状態は次のファイルに保存されます。

```text
workspace/current/state.json
```

想定している形式は次のとおりです。

```json
{
  "feature_name": "pipeline",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

`state.json` が存在しない場合、壊れている場合、必須キーが欠けている場合はエラーとして扱います。

## 実装上の公開 API

現在の実装とテストでは、次の API を前提にしています。

```python
# state.py
initialize_state(state_path)
load_state(state_path)
save_state(state_path, state_data)

# workflow.py
approve_phase(current_state, phase_name)

# cli.py
main(argv=None)
```

## テスト実行

```powershell
.\.env\Scripts\pytest.exe tests
```

## 制約

* CLI ベースのみを対象とする
* データベースは導入しない
* Web UI は導入しない
* ワークフロー状態は `workspace/current/` 配下のみに保存する
* `docs/specs/pipeline/spec.md` は実装作業から変更しない
