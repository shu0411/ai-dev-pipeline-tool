# Feature Spec: AI開発パイプラインCLI（Spec→Test→Code）

---

## 1. 背景

AIを活用した開発において、以下の課題がある：

* 仕様が曖昧なまま実装が進む
* テストが後付けになり品質が安定しない
* AIが勝手に次工程まで進んでしまう
* 人間の承認を挟む仕組みが弱い

そのため、
「仕様 → テスト → 実装」を段階的に進め、
各フェーズで人間の承認を必須とするCLIツールを開発する。

---

## 2. スコープ

### In Scope

* CLIベースの開発パイプライン管理
* フェーズ管理（spec / test / code）
* 各フェーズの承認機能
* 状態の永続化（ファイルベース）
* フェーズごとの成果物管理

### Out of Scope

* Web UI / GUI
* マルチユーザー対応
* データベース
* CI/CD統合
* AIの自動実行（Codex呼び出しは手動）

---

## 3. ユーザーストーリー

* ユーザーとして、仕様を確認・承認したい
  なぜならAIが勝手に進むのを防ぎたいから

* ユーザーとして、テストを先に確認したい
  なぜなら品質を担保したいから

* ユーザーとして、段階的に開発を進めたい
  なぜなら思考を整理したいから

---

## 4. 機能要件

1. 現在のフェーズを管理できる
2. フェーズごとに承認操作ができる
3. 承認後のみ次フェーズに進める
4. フェーズ状態を永続化できる
5. 現在の状態を確認できる
6. 初期化処理ができる

---

## 5. 非機能要件

* ローカル環境で動作する
* Python 3.11以上で動作
* シンプルなCLI操作
* 外部依存は最小限（pytestのみ）
* 再現性のある状態管理

---

## 6. 入出力仕様

### 入力

* CLIコマンド
* 承認操作（ユーザー）

### 出力

* 現在のフェーズ
* 承認状態
* CLI上のメッセージ

---

## 7. 業務ルール / バリデーション

* specが承認されていない場合、testフェーズに進めない

* testが承認されていない場合、codeフェーズに進めない

* フェーズは以下の順序でのみ進行可能：

  spec → test → code

* フェーズのスキップは禁止

* 承認前に次フェーズへ進もうとした場合はエラー

---

## 8. 受け入れ条件

* [ ] 初期状態でフェーズが spec である
* [ ] spec承認後に test フェーズに進む
* [ ] test承認後に code フェーズに進む
* [ ] 現在のフェーズを確認できる
* [ ] 状態が state.json に保存される
* [ ] 不正な遷移がブロックされる

---

## 9. エッジケース

* state.json が存在しない
* state.json が壊れている
* すでに承認済みのフェーズを再承認
* フェーズ外のコマンド実行
* 初期化前に操作

---

## 10. テスト観点

### 正常系

* spec → test → code の順に進む
* 各フェーズで承認が機能する

### 異常系

* 未承認で次フェーズに進もうとする
* 不正なフェーズ指定

### 境界値

* state.json が空
* state.json のキー欠損

### 状態管理

* フェーズが正しく更新される
* ファイルに反映される

---

## 11. 実装仕様

### 技術スタック

* Python 3.11+
* pytest
* CLI（標準ライブラリ）

### フォルダ構成

```text
ai-dev-pipeline-tool/
  src/
    ai_dev_pipeline_tool/
      cli.py
      state.py
      workflow.py
  tests/
    test_state.py
    test_workflow.py
  docs/
    specs/
      pipeline/
        spec.md
  workspace/
    current/
      state.json
```

### state.json の形式

```text
{
  "feature_name": "pipeline",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

---

## 12. CLI仕様

### コマンド一覧

#### 初期化

```text
init
```

#### 状態確認

```text
show-status
```

#### 承認

```text
approve spec
approve tests
```

approve spec は spec 承認後に test へ進む、approve tests は test 承認後に code へ進む

---

## 13. 制約

* DBは禁止（ファイル管理のみ）
* CLI以外のUIは禁止
* spec.mdは読み取り専用（ツールから変更しない）
* workspace配下のみ状態を書き込む

---

## 14. 未解決事項

なし
