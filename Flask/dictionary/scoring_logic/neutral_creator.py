def _neutral_creator(pct_labels, min_display_pct):
    result = []
    removed_sum = 0

    for item in pct_labels:
        if item["percentage"] >= min_display_pct:
            result.append(item)
        else:
            removed_sum += item["percentage"] # 제거된 값의 총합

    # 제거된 percentage가 있으면 중립/기타 추가
    if removed_sum > 0:
        result.append({
            "label" : "중립/기타",
            "percentage" : removed_sum
        })

    return result