# -*- coding: utf-8 -*-
"""Unit tests for src.bmi_core — 覆蓋所有分支 + 邊界 + ValueError 路徑。"""
import pytest

from src.bmi_core import calculate_bmi, classify_bmi


# ──────────────────────────────────────────────
# calculate_bmi：正常案例
# ──────────────────────────────────────────────

def test_calculate_bmi_normal_case():
    # 70 / (1.75 ** 2) = 22.857... → 22.86
    assert calculate_bmi(70, 1.75) == 22.86


def test_calculate_bmi_rounds_to_two_decimals():
    # 確認回傳值至多 2 位小數（防止有人改成 round(x, 3)）
    result = calculate_bmi(80, 1.70)
    assert result == 27.68


def test_calculate_bmi_returns_float():
    assert isinstance(calculate_bmi(60, 1.70), float)


# ──────────────────────────────────────────────
# calculate_bmi：ValueError 路徑（4 個必殺）
# ──────────────────────────────────────────────

def test_calculate_bmi_negative_weight_raises():
    with pytest.raises(ValueError, match="體重"):
        calculate_bmi(-5, 1.70)


def test_calculate_bmi_zero_weight_raises():
    with pytest.raises(ValueError, match="體重"):
        calculate_bmi(0, 1.70)


def test_calculate_bmi_negative_height_raises():
    with pytest.raises(ValueError, match="身高"):
        calculate_bmi(70, -1.0)


def test_calculate_bmi_zero_height_raises():
    with pytest.raises(ValueError, match="身高"):
        calculate_bmi(70, 0)


def test_calculate_bmi_error_message_weight_exact():
    with pytest.raises(ValueError) as exc:
        calculate_bmi(-1, 1.70)
    assert str(exc.value) == "體重必須為正數（大於 0）"


def test_calculate_bmi_error_message_height_exact():
    with pytest.raises(ValueError) as exc:
        calculate_bmi(70, -1)
    assert str(exc.value) == "身高必須為正數（大於 0）"


# ──────────────────────────────────────────────
# classify_bmi：四分類各一例
# ──────────────────────────────────────────────

def test_classify_underweight():
    assert classify_bmi(15.57) == "偏瘦"


def test_classify_normal():
    assert classify_bmi(22.86) == "正常"


def test_classify_overweight():
    assert classify_bmi(27.68) == "過重"


def test_classify_obese():
    assert classify_bmi(34.60) == "肥胖"


# ──────────────────────────────────────────────
# classify_bmi：邊界值（18.5 / 25.0 / 30.0）
# ──────────────────────────────────────────────

def test_classify_boundary_18_5_is_normal():
    """18.5 → 正常（不是偏瘦）。抓 >= 改 > 的 mutation。"""
    assert classify_bmi(18.5) == "正常"


def test_classify_just_below_18_5_is_underweight():
    """18.49 → 偏瘦。抓 < 改 <= 的 mutation。"""
    assert classify_bmi(18.49) == "偏瘦"


def test_classify_boundary_25_is_overweight():
    """25.0 → 過重（不是正常）。"""
    assert classify_bmi(25.0) == "過重"


def test_classify_just_below_25_is_normal():
    assert classify_bmi(24.99) == "正常"


def test_classify_boundary_30_is_obese():
    """30.0 → 肥胖（不是過重）。"""
    assert classify_bmi(30.0) == "肥胖"


def test_classify_just_below_30_is_overweight():
    assert classify_bmi(29.99) == "過重"


# ──────────────────────────────────────────────
# classify_bmi：(0, 1) 區間（避免 T002 GAP-001）
# ──────────────────────────────────────────────
# 確保極小 BMI 仍正確歸為「偏瘦」，不會被 mutation 改成其他分類
# 也避免有人寫成 if 0 < bmi < 18.5 之類的錯誤

def test_classify_very_small_positive_bmi_is_underweight():
    assert classify_bmi(0.01) == "偏瘦"


def test_classify_half_bmi_is_underweight():
    assert classify_bmi(0.5) == "偏瘦"


def test_classify_one_bmi_is_underweight():
    assert classify_bmi(1.0) == "偏瘦"


# ──────────────────────────────────────────────
# 整合：calculate_bmi + classify_bmi 串接（不變條件範例）
# ──────────────────────────────────────────────

def test_pipeline_47_36_kg_1_60_m_is_normal():
    """SDD 邊界案例：47.36 / 2.56 = 18.5 → 正常。"""
    bmi = calculate_bmi(47.36, 1.60)
    assert bmi == 18.50
    assert classify_bmi(bmi) == "正常"


def test_pipeline_72_25_kg_1_70_m_is_overweight():
    """SDD 邊界案例：72.25 / 2.89 = 25.0 → 過重。"""
    bmi = calculate_bmi(72.25, 1.70)
    assert bmi == 25.00
    assert classify_bmi(bmi) == "過重"
