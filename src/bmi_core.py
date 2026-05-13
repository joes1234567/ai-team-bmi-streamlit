# -*- coding: utf-8 -*-
"""BMI 計算純函式層（無 IO 副作用）。"""


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """計算 BMI，回傳四捨五入至小數點後 2 位。

    Args:
        weight_kg: 體重（公斤），必須 > 0
        height_m:  身高（公尺），必須 > 0

    Returns:
        BMI 值（round 到 2 位）

    Raises:
        ValueError: weight_kg <= 0，訊息為「體重必須為正數（大於 0）」
        ValueError: height_m  <= 0，訊息為「身高必須為正數（大於 0）」
    """
    if weight_kg <= 0:
        raise ValueError("體重必須為正數（大於 0）")
    if height_m <= 0:
        raise ValueError("身高必須為正數（大於 0）")
    bmi_raw = weight_kg / (height_m ** 2)
    return round(bmi_raw, 2)


def classify_bmi(bmi: float) -> str:
    """依 WHO 標準將 BMI 分類為偏瘦/正常/過重/肥胖。

    不變條件：bmi 必須是 calculate_bmi() 的回傳值（已 round 至 2 位），
    以確保 18.5 / 25.0 / 30.0 邊界行為唯一。
    """
    if bmi < 18.5:
        return "偏瘦"
    if bmi < 25.0:
        return "正常"
    if bmi < 30.0:
        return "過重"
    return "肥胖"
