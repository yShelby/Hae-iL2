import json

file1_path = "original/sentiword_info_added_label_tag.json"
file2_path = "original/sentiword_info_exception.json"
output_path = "sentiword_info_cleaned_v2.json"

###
# file 정제 순서
# 1. 사전 내 이모지 제거 -> 단일 어근만 추출 -> 어근 중복 제거 -> 신조어, 초성을 exception file로 분리
# 2. 표준어 기준 사전 어근, kiwi 어근 불일치 수정
# 3. 빈도가 낮은 태그 -> 유사 태그로 대체
# 4. 사전에 직접 반영된 "오탈자"에 해당하는 글자 제거
###

# 파일 로드
with open(file1_path, "r", encoding="utf-8") as f:
    file1 = json.load(f)

with open(file2_path, "r", encoding="utf-8") as f:
    file2 = json.load(f)

# file2에서 index 제거
for item in file2:
    item.pop("index", None)

# word → dict 매핑 (file2 우선)
merged_dict = {item["word"]: item for item in file2}
for item in file1:
    if item["word"] not in merged_dict:
        merged_dict[item["word"]] = item

# file1 / file2 단어 목록
file1_words = [item["word"] for item in file1]
file2_words = [item["word"] for item in file2]

# 결과 리스트
result = []

# 1) file2 순서대로 우선 추가
for w in file2_words:
    result.append(merged_dict[w])

# 2) file1에만 있는 word 뒤에 추가
for w in file1_words:
    if w not in file2_words:
        result.append(merged_dict[w])

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print(f"병합 완료 (file2 순서 → file1 나머지 순서) → {output_path} (총 {len(result)}개)")
