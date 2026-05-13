# -*- coding: utf-8 -*-
"""BDD step definitions for bmi_streamlit.feature。"""
import os

from pytest_bdd import given, parsers, scenarios, then, when

FEATURE_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..",
        "01_specs", "bmi_streamlit.feature",
    )
)
scenarios(FEATURE_FILE)


# ──────────────────────────────────────────────
# Given
# ──────────────────────────────────────────────

@given("Streamlit app 已啟動並完成初始渲染")
def app_started(app):
    # AppTest.run() 已在 fixture 完成
    assert app is not None


@given(parsers.parse('使用者在體重欄輸入 "{value}"'))
def input_weight(app, value):
    app.text_input(key="weight_input").set_value(value)


@given(parsers.parse('使用者在身高欄輸入 "{value}"'))
def input_height(app, value):
    app.text_input(key="height_input").set_value(value)


# ──────────────────────────────────────────────
# When
# ──────────────────────────────────────────────

@when("使用者點擊「計算 BMI」按鈕")
def click_calc(app):
    app.button(key="calc_button").click().run()


# ──────────────────────────────────────────────
# Then
# ──────────────────────────────────────────────

def _metric_value(m):
    """AppTest metric 值在不同 streamlit 版本可能是 .value 或 .body。"""
    return getattr(m, "value", None) or getattr(m, "body", None)


def _error_text(e):
    return getattr(e, "value", None) or getattr(e, "body", None)


@then(parsers.parse('頁面顯示 BMI 指數為 "{expected}"'))
def assert_bmi_metric(app, expected):
    assert len(app.metric) >= 1, "預期至少 1 個 metric（BMI 指數）"
    assert _metric_value(app.metric[0]) == expected


@then(parsers.parse('頁面顯示健康分類為 "{expected}"'))
def assert_category_metric(app, expected):
    assert len(app.metric) >= 2, "預期至少 2 個 metric（含健康分類）"
    assert _metric_value(app.metric[1]) == expected


@then("頁面不顯示任何錯誤訊息")
def assert_no_error(app):
    assert len(app.error) == 0


@then(parsers.parse('頁面顯示含有「{keyword}」的錯誤訊息'))
def assert_error_contains(app, keyword):
    assert len(app.error) >= 1, "預期至少 1 個 error 訊息"
    assert keyword in _error_text(app.error[0])


@then("頁面不顯示任何 BMI 指數區塊")
def assert_no_bmi_metric(app):
    assert len(app.metric) == 0


@then("頁面不顯示任何健康分類區塊")
def assert_no_category_metric(app):
    # 同上：error 狀態下 metric 全部為 0
    assert len(app.metric) == 0
