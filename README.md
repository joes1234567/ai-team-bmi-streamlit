# BMI Calculator (Streamlit Web App)

A web-based BMI calculator built with Streamlit. The second MVP demo of the AI Team system — validates the new deployment URL workflow.

## Try it online

🚀 **Live demo**: _(部署 URL 待負責人到 [share.streamlit.io](https://share.streamlit.io) 完成首次連結後補上)_

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Windows 使用者建議先設定 UTF-8 環境變數：

```bash
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
streamlit run streamlit_app.py
```

## Run tests

```bash
pip install -r requirements-dev.txt

# Unit tests
pytest tests/unit -v

# BDD tests（用 streamlit.testing.v1.AppTest）
pytest tests/bdd -v
```

## Project structure

```
bmi_streamlit/
├── streamlit_app.py          # Streamlit Cloud 入口（必須在根目錄）
├── src/
│   └── bmi_core.py           # 純函式：calculate_bmi / classify_bmi
├── tests/
│   ├── unit/                 # 單元測試（覆蓋 bmi_core 所有分支 + 邊界）
│   └── bdd/                  # BDD 測試（用 AppTest 驅動 UI 流程）
├── requirements.txt          # production deps（只有 streamlit）
├── requirements-dev.txt      # dev deps（pytest, pytest-bdd, mutmut, streamlit）
└── 01_specs/                 # BDD .feature + SDD
```

## Deployment（首次需負責人手動）

1. 到 <https://share.streamlit.io> 點 **New app**
2. 連結 GitHub repo：`joes1234567/ai-team-bmi-streamlit`
3. 選 `streamlit_app.py` 為入口
4. 點 **Deploy** → 取得 live URL（格式：`https://<name>.streamlit.app`）
5. 之後 push 到 `main` 分支會自動重新部署

## Status

✅ Phase 2/3：實作完成，待 QA + 首次部署。
