import json

input_file = "original/sentiword_info_split_exception.json"   # 원본 JSON
output_file = "original/sentiword_info_filtered.json"  # 결과 저장 파일

# JSON 불러오기
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)  # data: list[dict]

# 1단계: 기본 필터링
#  - word_root 공백이 1개 이상인 항목 제외#  - polarity = "0" 항목 제외
filtered_data = [
    item for item in data
    if item.get("word_root", "").count(" ") < 1
       and str(item.get("polarity", "")).strip() != "0"
]

# 2단계: 공백이 1개 이상인 word_root 중에 같은 root가 있으면 첫 번째만 남기고 제거
seen = set()
result = []
for item in filtered_data:
    root = item.get("word_root", "")
    if root not in seen:
        result.append(item)
        seen.add(root)
    # 이미 같은 root가 있으면 skip

print(f"원본 항목 수: {len(data)} → 1차 필터 후: {len(filtered_data)} → 중복 제거 후: {len(result)}")

# 3단계: 저장
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print(f"{output_file} 저장 완료")
