# SDD: BMI 計算器 Streamlit Web App

- 版本：v1.0
- 狀態：已完成（Phase 1 BDD/SDD 產出）
- 對應 Task：T006
- 建立日期：2026-05-14

---

## 1. 系統範圍

### 包含

- BMI 數值計算（公式：`weight_kg / height_m ** 2`，四捨五入至小數點後 2 位）
- WHO 四分類判斷：偏瘦 / 正常 / 過重 / 肥胖
- Streamlit web UI：使用者填入體重、身高後點擊按鈕，頁面顯示 BMI 和分類
- 輸入驗證：偵測負數、零值、非數字，並在頁面顯示繁中錯誤訊息
- 部署至 Streamlit Cloud（https://share.streamlit.io）

### 不包含

- CLI 介面（那是 bmi_cli 專案）
- 持久化（DB、檔案讀寫、session 歷史紀錄）
- 網路請求（Webhook、API 呼叫）
- OAuth / 登入 / 使用者管理
- 英制單位（lb、inch）
- 多語言 i18n（只支援繁體中文）
- 打包安裝檔（.exe / wheel）

### 部署目標

- **Streamlit Cloud**（https://share.streamlit.io）
- 首次部署需負責人手動在 share.streamlit.io 連結 GitHub repo（詳見 §4 互動流程 → 部署流程）
- 後續 push 到 `main` 分支自動觸發重新部署

---

## 2. 架構

### 檔案結構（扁平結構，bmi_streamlit/ 即 git repo 根）

```
bmi_streamlit/                    ← git repo 根
├── streamlit_app.py              ← Streamlit Cloud 預設入口（必須在根目錄）
├── src/
│   ├── __init__.py               ← 空檔，讓 src 成為 Python package
│   └── bmi_core.py               ← 純函式計算層：calculate_bmi() + classify_bmi()
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_bmi_core.py      ← 單元測試（覆蓋 bmi_core.py 所有分支 + 邊界）
│   └── bdd/
│       ├── __init__.py
│       ├── conftest.py           ← pytest-bdd fixture（含 AppTest 初始化）
│       └── step_defs/
│           └── test_bmi_streamlit_steps.py  ← BDD step definitions
├── requirements.txt              ← production deps：streamlit（僅此一個）
├── requirements-dev.txt          ← dev deps：pytest, pytest-bdd, mutmut, streamlit
└── 01_specs/
    ├── bmi_streamlit.feature     ← BDD 規格（本目錄已入 git）
    └── sdd.md                    ← 本文件
```

> **重要：不要建立 03_development/ 資料夾。** 扁平結構：所有程式碼在 repo 根目錄下的 `src/` 和 `tests/`。

### 模組依賴關係（DAG，由下往上）

```
streamlit_app.py
  └── src.bmi_core   （純函式，零外部依賴）
  └── streamlit      （UI framework）
```

### 外部依賴

**Production dependencies（requirements.txt）：**

```
streamlit>=1.28.0
```

> 只允許 streamlit。BMI 計算純用 stdlib（`round()` 內建）。

**Development dependencies（requirements-dev.txt）：**

```
pytest>=7.4
pytest-bdd>=7.0
mutmut>=2.4
streamlit>=1.28.0
```

> Streamlit 在 dev 也需要，因為 AppTest（`streamlit.testing.v1`）內建於 streamlit 套件。

---

## 3. UI 元件

### 3.1 元件清單

| 元件 | Streamlit API | key（AppTest 索引用） | 說明 |
|---|---|---|---|
| 頁面標題 | `st.title("BMI 計算器")` | — | 固定文字 |
| 體重輸入框 | `st.text_input(...)` | `"weight_input"` | 標籤：「體重（公斤）」 |
| 身高輸入框 | `st.text_input(...)` | `"height_input"` | 標籤：「身高（公尺）」 |
| 計算按鈕 | `st.button(...)` | `"calc_button"` | 標籤：「計算 BMI」 |
| BMI 數值顯示 | `st.metric(...)` | — | 標籤：「BMI 指數」，value 格式：`f"{bmi:.2f}"` |
| 健康分類顯示 | `st.metric(...)` | — | 標籤：「健康分類」，value：`category`（偏瘦/正常/過重/肥胖） |
| 錯誤訊息 | `st.error(...)` | — | 輸入驗證失敗時顯示 |

### 3.2 顯示條件

| 元件 | 顯示條件 | 隱藏條件 |
|---|---|---|
| BMI 指數 metric | 計算成功後 | 尚未計算 / 發生錯誤 |
| 健康分類 metric | 計算成功後 | 尚未計算 / 發生錯誤 |
| 錯誤訊息 | 驗證失敗後 | 尚未計算 / 計算成功 |

> **AppTest 測試關鍵：** 錯誤狀態下 `len(at.metric) == 0`；成功狀態下 `len(at.metric) == 2` 且 `len(at.error) == 0`。

---

## 4. 互動流程

### 4.1 使用者操作流程

```
[使用者開啟頁面]
       ↓
[看到：標題 + 體重輸入框 + 身高輸入框 + 計算 BMI 按鈕]
（無 metric、無 error）
       ↓
[使用者填入體重和身高]
       ↓
[點擊「計算 BMI」按鈕]
       ↓
[Streamlit 重新執行 streamlit_app.py]
       ↓
        ├─── 轉換失敗（非數字）
        │         ↓
        │    [顯示 st.error("錯誤：請輸入有效的數字")]
        │    [不顯示任何 metric]
        │
        ├─── 轉換成功，但值 ≤ 0
        │         ↓
        │    [顯示 st.error("錯誤：體重必須為正數（大於 0）")
        │     或  st.error("錯誤：身高必須為正數（大於 0）")]
        │    [不顯示任何 metric]
        │
        └─── 驗證通過
                  ↓
             [calculate_bmi(weight, height) → bmi]
             [classify_bmi(bmi) → category]
                  ↓
             [顯示 st.metric("BMI 指數", f"{bmi:.2f}")]
             [顯示 st.metric("健康分類", category)]
             [不顯示任何 error]
```

### 4.2 精確錯誤訊息規格

> 訊息必須完全按照下表，字元不得差異（QA Agent 的 step defs 會做字串包含比對）。

| 情境 | `st.error()` 訊息 | 包含關鍵字 |
|---|---|---|
| weight 或 height 為非數字 | `"錯誤：請輸入有效的數字"` | `"數字"` |
| weight ≤ 0 | `"錯誤：體重必須為正數（大於 0）"` | `"體重"` |
| height ≤ 0 | `"錯誤：身高必須為正數（大於 0）"` | `"身高"` |

> 注意：`calculate_bmi()` 會 raise `ValueError`，訊息本身已含「體重」或「身高」。`streamlit_app.py` 捕捉 ValueError 後直接 `st.error(f"錯誤：{e}")` 即可確保關鍵字一致。

### 4.3 部署流程（首次需負責人手動授權）

```
[Coding Agent 完成實作]
       ↓
[Coding Agent commit + push 到 GitHub main 分支]
       ↓
[Coding Agent 在 T006_result 或通知檔中寫明：「請負責人到 share.streamlit.io 完成 repo 連結」]
       ↓
[Orchestrator 通知負責人：
 「請到 https://share.streamlit.io 點 New app → 連結 GitHub repo bmi_streamlit
   → 選 streamlit_app.py 為入口 → Deploy」]
       ↓
[負責人完成手動操作，取得 live URL（格式：https://<name>.streamlit.app）]
       ↓
[負責人將 live URL 告知 Orchestrator]
       ↓
[Orchestrator 記錄 live URL 到 project_status.md，結案]
```

> **後續重新部署：** 只要 push 到 main 分支，Streamlit Cloud 自動重新部署。無需負責人再次介入。

---

## 5. 函式簽章

### 5.1 `src/bmi_core.py`

> 此模組是**獨立新實作**，不得複製 bmi_cli/src/core.py 的程式碼。邏輯相同、公式相同、分類門檻相同，但需重新撰寫。

```python
# -*- coding: utf-8 -*-
"""BMI 計算純函式層（無 IO 副作用）。"""


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    計算 BMI 值。

    Args:
        weight_kg: 體重（公斤），必須 > 0
        height_m:  身高（公尺），必須 > 0

    Returns:
        BMI 值，四捨五入至小數點後 2 位（Python round()）
        例：70 / (1.75 ** 2) → round(22.857..., 2) → 22.86

    Raises:
        ValueError: weight_kg <= 0 時，訊息固定為 "體重必須為正數（大於 0）"
        ValueError: height_m  <= 0 時，訊息固定為 "身高必須為正數（大於 0）"

    副作用：無
    """


def classify_bmi(bmi: float) -> str:
    """
    依 WHO 標準將 BMI 值對應到健康分類。

    Args:
        bmi: BMI 數值，必須是 calculate_bmi() 回傳的已四捨五入值
             （確保邊界 18.5 / 25.0 / 30.0 行為唯一）

    Returns:
        "偏瘦"  if bmi < 18.5
        "正常"  if 18.5 <= bmi < 25.0
        "過重"  if 25.0 <= bmi < 30.0
        "肥胖"  if bmi >= 30.0

    副作用：無

    不變條件：
        只接收 calculate_bmi() 的回傳值（已 round）。
        streamlit_app.py 不得分別計算 raw bmi 再獨立呼叫 classify_bmi()。
    """
```

### 5.2 `streamlit_app.py`（根目錄）

```python
# -*- coding: utf-8 -*-
"""Streamlit BMI 計算器 — 入口（Streamlit Cloud 預設讀這個）。"""
import streamlit as st
from src.bmi_core import calculate_bmi, classify_bmi


def main() -> None:
    """
    Streamlit app 主流程。每次 widget 變動都重新執行整個 main()。

    流程：
    1. 渲染標題和輸入 widget（text_input × 2、button × 1）
    2. 若按鈕被點擊：
       a. 嘗試 float() 轉換 weight 和 height
          - 失敗 → st.error("錯誤：請輸入有效的數字")；return（不繼續）
       b. 呼叫 calculate_bmi(weight, height)
          - ValueError → st.error(f"錯誤：{e}")；return（不繼續）
       c. 呼叫 classify_bmi(bmi)
       d. st.metric("BMI 指數", f"{bmi:.2f}")
       e. st.metric("健康分類", category)
    3. 未點按鈕 → 不顯示 metric / error

    重要：
    - 按鈕 key="calc_button"（AppTest 用此 key 識別）
    - weight_input key="weight_input"
    - height_input key="height_input"
    - metric 順序固定：index 0 = BMI 指數，index 1 = 健康分類
    """


if __name__ == "__main__":
    main()
```

> Streamlit Cloud 呼叫 `streamlit run streamlit_app.py`，不需要 `if __name__ == "__main__"` 下的 main()，但保留作本地開發用。

---

## 6. 非功能需求

| 項目 | 需求 |
|---|---|
| 效能 | 無特殊需求；純本地計算，BMI 運算 < 1ms |
| 安全 | 不接觸網路（計算層）；不讀寫本地檔案；無使用者資料儲存；無認證機制 |
| 可用性 | 依 Streamlit Cloud 免費方案 SLA（無保證，已知 cold start 約 30–60 秒） |
| 可測試性 | `bmi_core.py` 純函式，100% 可獨立單元測試；`streamlit_app.py` 用 `streamlit.testing.v1.AppTest` 做 BDD 測試 |
| 可移植性 | Python 3.10+；Windows / macOS / Linux 均可本地執行 |
| 編碼 | 所有 .py 用 UTF-8；本地 Windows 執行需 `PYTHONUTF8=1` |
| Cold start | Streamlit Cloud 免費方案閒置後 app 會休眠，首次開啟需等約 30–60 秒。已知限制，MVP 接受 |

---

## 7. 技術棧

| 項目 | 選擇 | 理由 |
|---|---|---|
| 語言 | Python 3.10+ | 系統預設語言（OPERATIONS.md §3） |
| Web UI framework | Streamlit 1.28+ | Constraint 指定；含內建 AppTest |
| BMI 計算 | 純 Python stdlib（`round()` 內建） | Constraint 禁止第三方計算 library |
| 測試 runner | `pytest` + `pytest-bdd` | 系統 BDD 標準工具 |
| BDD UI 測試 | `streamlit.testing.v1.AppTest` | Streamlit 1.28+ 內建，無需額外套件 |
| Mutation testing | `mutmut` | 系統標準工具（CLAUDE.md BDD 執行程序） |
| 部署平台 | Streamlit Cloud（share.streamlit.io） | Constraint 指定 |
| 版本控制 | GitHub（與 bmi_cli 同 organization） | 現有基礎設施 |

---

## 8. 風險與假設

### 已知風險

| 風險 | 說明 | 緩解方式 |
|---|---|---|
| AppTest API 相容性 | `streamlit.testing.v1` 在 1.28 才穩定，1.27 以下不可用 | requirements.txt / requirements-dev.txt 鎖定 `streamlit>=1.28.0` |
| 浮點數邊界精度 | `round(47.36/2.56, 2)` 在 Python 中為 18.5，`classify_bmi` 接收此值為 `正常`。若 Coding Agent 不遵守「只傳 rounded bmi 給 classify」的不變條件，邊界行為將不確定 | §5.2 明文要求；unit tests + BDD scenario 5/6 專門驗收 |
| Streamlit Cloud cold start | 免費方案閒置 30 分鐘後休眠，首次開啟需等 30–60 秒 | §6 已記錄為已知限制，MVP 接受 |
| 首次部署需手動操作 | Coding Agent 無法自行完成 share.streamlit.io 的 repo 連結（需登入 GitHub OAuth） | §4.3 已明文寫出流程，Orchestrator 負責通知負責人 |
| Windows 中文編碼 | Windows cmd 預設 cp950，中文訊息可能亂碼 | 本地開發時設 `PYTHONUTF8=1`；Streamlit Cloud 為 Linux，無此問題 |

### 採用的假設

- BMI 公式：`weight_kg / (height_m ** 2)`（與 bmi_cli 相同，業主確認過）
- WHO 分類門檻：< 18.5 偏瘦、18.5–24.99 正常、25.0–29.99 過重、≥ 30.0 肥胖
- 邊界歸屬：18.5 → 正常；25.0 → 過重；30.0 → 肥胖（`>=` 邊界歸較高那級）
- BMI 顯示格式：固定 2 位小數（`f"{bmi:.2f}"`），業主未指定，採業界常見值
- classify_bmi() 只接收 calculate_bmi() 回傳的 rounded bmi（不變條件）
- Streamlit 版本：1.28+（AppTest 需要）
- 部署平台：Streamlit Cloud 免費方案（業主未說要付費方案）
- 首次部署後的 live URL 格式：`https://<repo-or-custom-name>.streamlit.app`
- 重置按鈕：MVP 不實作（task 標為 optional，複雜度不值得增加）

---

## 9. Authorized Scope

```yaml
authorized_scope:
  allowed_changes:
    - "建立 src/bmi_core.py，獨立實作 calculate_bmi() 和 classify_bmi() 純函式"
    - "建立 src/__init__.py（空檔）"
    - "建立 streamlit_app.py（根目錄），實作 main() UI 流程"
    - "建立 tests/unit/test_bmi_core.py，新增 unit tests 覆蓋 bmi_core.py 所有分支 + 3 個邊界值"
    - "建立 tests/bdd/conftest.py，設定 pytest-bdd fixture 和 AppTest 初始化"
    - "建立 tests/bdd/step_defs/test_bmi_streamlit_steps.py，實作 01_specs/bmi_streamlit.feature 的所有 step definitions"
    - "建立 tests/__init__.py、tests/unit/__init__.py、tests/bdd/__init__.py（空檔）"
    - "建立 requirements.txt（內容：streamlit>=1.28.0）"
    - "建立 requirements-dev.txt（內容：pytest>=7.4, pytest-bdd>=7.0, mutmut>=2.4, streamlit>=1.28.0）"
    - "建立或更新 README.md（說明本地執行和 Streamlit Cloud 部署方式）"
    - "git commit 到 feature branch T006-bmi-streamlit，push 到 GitHub，開 PR"

  forbidden_changes:
    - "不得複製 bmi_cli/src/core.py 的程式碼（要獨立重新實作）"
    - "不得加入任何超出 streamlit 的 production dependency"
    - "不得加入 OAuth / 登入 / 使用者管理"
    - "不得加入 DB / 檔案讀寫 / 持久化"
    - "不得加入網路請求（HTTP、WebSocket、Telegram 等）"
    - "不得使用第三方計算 BMI 的 library"
    - "不得支援英制單位（lb、inch）"
    - "不得修改 01_specs/bmi_streamlit.feature 的 scenario 內容"
    - "不得建立 03_development/ 資料夾（扁平結構，程式碼在 src/）"
    - "不得在 Streamlit Cloud 執行任何 deployment 操作（需負責人手動授權）"

  requires_owner_approval:
    - "首次 Streamlit Cloud 部署：Coding Agent push 完後，需負責人到 share.streamlit.io 手動連結 GitHub repo → 選 streamlit_app.py 為入口 → 點 Deploy → 拿到 live URL"
    - "新增任何 PyPI 套件到 requirements.txt（production deps）"
    - "將 GitHub repo 改為公開（預設私有）"
    - "修改 WHO 分類門檻或 BMI 公式"
    - "加入英制單位支援"
    - "新增業主可見的 UI 元件或行為（如重置按鈕、歷史紀錄、分享功能）"
    - "自訂 Streamlit Cloud app domain 或設定自訂網域"

  assumptions:
    - "Streamlit 1.28+（AppTest 需要）；若 Streamlit Cloud 環境版本不符，需升級"
    - "BMI 公式與分類門檻與 bmi_cli 完全相同（業主未要求改）"
    - "邊界歸屬：18.5 → 正常；25.0 → 過重；30.0 → 肥胖"
    - "重置按鈕不實作（task 標為 optional，MVP 跳過）"
    - "Streamlit Cloud 免費方案（cold start 已知限制，MVP 接受）"
    - "首次 deployment 需負責人手動介入（AI Team 無法代勞）"
    - "classify_bmi() 只接收 calculate_bmi() 回傳的 rounded bmi，不得分別計算"

  open_questions: []
  # 所有關鍵決策已在 assumptions 決定完畢。
  # 唯一需要後續確認的是首次部署後的 live URL，
  # 但那是執行時產生的，不是規格問題。
```

---

## 附：AppTest 測試模式速查（給 QA Agent）

> 這是提示而非規格，QA Agent 可依實際 AppTest API 調整。

```python
from streamlit.testing.v1 import AppTest

def test_normal_input():
    at = AppTest.from_file("streamlit_app.py").run()
    at.text_input(key="weight_input").set_value("70").run()
    at.text_input(key="height_input").set_value("1.75").run()
    at.button(key="calc_button").click().run()
    assert at.metric[0].value == "22.86"
    assert at.metric[1].value == "正常"
    assert len(at.error) == 0

def test_error_negative_weight():
    at = AppTest.from_file("streamlit_app.py").run()
    at.text_input(key="weight_input").set_value("-5").run()
    at.text_input(key="height_input").set_value("1.70").run()
    at.button(key="calc_button").click().run()
    assert len(at.metric) == 0
    assert len(at.error) == 1
    assert "體重" in at.error[0].value
```

> 注意：AppTest 的 `.value` 屬性在不同 Streamlit 版本可能是 `.body` 或 `.value`。QA Agent 應以執行時的實際 API 為準，不必完全照抄上面的屬性名。
