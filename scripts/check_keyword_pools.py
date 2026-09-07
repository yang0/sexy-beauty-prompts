"""Static checks for the composable prompt keyword pools."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "## 人物基础池",
    "## 肤色底调池",
    "## 皮肤质感池",
    "## 脸型结构池",
    "## 五官焦点池",
    "## 妆容与发型池",
    "## 人物池抽取规则",
    "## 体型风格池",
    "## 身体轮廓池",
    "## 服装结构池",
    "## 轻薄衬衫逆光分支",
    "## 显身材剪裁池",
    "## 显身材配色池",
    "## 服装选择规则",
    "## 服装材质池",
    "## 服装颜色与细节池",
    "## 姿势与神态池",
    "## 专业相机镜头池",
    "## 手机抓拍镜头池",
    "## 光线与质感池",
)
FORBIDDEN_TEMPLATE_TERMS = ("唯一固定模板", "只能使用以下", "必须照抄")


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "references" / "keyword-pools.md"
    if not path.is_file():
        print(f"FAIL: missing {path}")
        return 1
    text = path.read_text(encoding="utf-8")
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    if missing:
        print("FAIL: missing headings: " + ", ".join(missing))
        return 1
    if any(term in text for term in FORBIDDEN_TEMPLATE_TERMS):
        print("FAIL: pool contains fixed-template wording")
        return 1
    if "东亚女性" not in text or "毛孔" not in text or "皮肤" not in text:
        print("FAIL: person pool lacks East Asian and skin-texture anchors")
        return 1
    required_anchors = {
        "肤色底调池": ("象牙", "肤色"),
        "皮肤质感池": ("毛孔", "绒毛"),
        "脸型结构池": ("鹅蛋脸", "下颌"),
        "五官焦点池": ("杏仁眼", "鼻梁", "唇"),
        "妆容与发型池": ("底妆", "发丝"),
        "显身材剪裁池": ("深 V", "收腰", "短裙"),
        "显身材配色池": ("深色上装", "明暗", "缎料"),
    }
    for pool, anchors in required_anchors.items():
        if not all(anchor in text for anchor in anchors):
            print(f"FAIL: {pool} lacks required anchors: {', '.join(anchors)}")
            return 1
    entries = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "1. ", "2. ", "3. ", "4. ", "5. ")):
            entries.append(stripped)
        elif stripped.startswith("|") and "---" not in stripped and not stripped.startswith("| 维度") and not stripped.startswith("| 视觉重点") and not stripped.startswith("| 类别") and not stripped.startswith("| 模式"):
            entries.append(stripped)
    normalized = [re.sub(r"\s+", " ", line).lower() for line in entries]
    duplicates = sorted({item for item in normalized if normalized.count(item) > 1})
    if duplicates:
        print("FAIL: duplicate pool entries: " + "; ".join(duplicates[:5]))
        return 1
    if len(entries) < 20:
        print("FAIL: keyword pools are too small")
        return 1
    print(f"PASS: {len(REQUIRED_HEADINGS)} pools, {len(entries)} non-empty entries, no fixed-template markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
