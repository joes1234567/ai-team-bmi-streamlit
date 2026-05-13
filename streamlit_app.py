# -*- coding: utf-8 -*-
"""Streamlit BMI 計算器 — 入口（Streamlit Cloud 預設讀這個）。"""
import streamlit as st

from src.bmi_core import calculate_bmi, classify_bmi


def main() -> None:
    """Streamlit app 主流程。每次 widget 變動都重新執行整個 main()。"""
    st.title("BMI 計算器")

    weight_raw = st.text_input("體重（公斤）", key="weight_input")
    height_raw = st.text_input("身高（公尺）", key="height_input")
    clicked = st.button("計算 BMI", key="calc_button")

    if not clicked:
        return

    # 1. 嘗試 float 轉換
    try:
        weight = float(weight_raw)
        height = float(height_raw)
    except (ValueError, TypeError):
        st.error("錯誤：請輸入有效的數字")
        return

    # 2. 計算 BMI（內部驗證正數）
    try:
        bmi = calculate_bmi(weight, height)
    except ValueError as e:
        st.error(f"錯誤：{e}")
        return

    # 3. 分類（傳入已 round 的 bmi，遵守不變條件）
    category = classify_bmi(bmi)

    st.metric("BMI 指數", f"{bmi:.2f}")
    st.metric("健康分類", category)


if __name__ == "__main__":
    main()
