# AI Dev Pipeline Tool

## 概要

このプロジェクトは、AIを活用した開発を段階的に管理するCLIツールです。

開発フロー：

```
spec → test → code
```

各フェーズは必ず人間の承認を経てから次へ進みます。

---

## 目的

* AIが勝手に開発を進めることを防ぐ
* テストファースト開発を強制する
* 仕様の明確化を促進する

---

## 機能

* フェーズ管理（spec / test / code）
* 承認フロー
* 状態のファイル管理
* CLIによる操作

---

## フォルダ構成

```
src/ai_dev_pipeline_tool/
    cli.py
    state.py
    workflow.py

tests/
    test_state.py
    test_workflow.py

docs/specs/
    pipeline/spec.md

workspace/current/
    state.json
```

---

## セットアップ

### 1. 仮想環境作成

```
python -m venv .venv
```

### 2. 有効化

```
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\Activate.ps1  # Windows
```

### 3. 依存関
