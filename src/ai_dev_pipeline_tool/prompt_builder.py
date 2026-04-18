from __future__ import annotations


def build_prompt(task_type: str, spec_path: str) -> str:
    if task_type == "tests":
        return (
            f"対象の spec は {spec_path} です。\n"
            "spec を読んでください。\n"
            "テストのみ作成してください。\n"
            "pytest を使ってください。\n"
            "正常系 / 異常系 / 境界値を含めてください。\n"
            "実装コードは変更しないでください。\n"
            "不明点を最後に列挙してください。"
        )

    if task_type == "code":
        return (
            f"対象の spec は {spec_path} です。\n"
            "spec と既存テストを読んでください。\n"
            "実装のみを行ってください。\n"
            "テストを通すようにしてください。\n"
            "仕様外変更をしないでください。\n"
            "不明点を最後に列挙してください。"
        )

    raise ValueError(f"Unsupported task type: {task_type}")
