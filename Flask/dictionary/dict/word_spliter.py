import json
import math
import os

# 원본 JSON 파일 경로
input_file = "original/sentiword_info_added_label_tag.json"  # 전체 데이터가 들어있는 파일
output_dir = "split_json2"
chunk_size = 10  # 10개씩 끊어서 저장

# 출력 폴더 생성
os.makedirs(output_dir, exist_ok=True)

# 원본 JSON 파일 읽기
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 전체 데이터 개수
total_items = len(data)
total_files = math.ceil(total_items / chunk_size)

print(f"총 {total_items}개 항목 → {total_files}개 파일 생성 예정")

# 데이터 10개씩 잘라서 저장
for i in range(total_files):
    start_index = i * chunk_size
    end_index = start_index + chunk_size
    chunk = data[start_index:end_index]

    output_path = os.path.join(output_dir, f"output_{i + 1}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunk, f, ensure_ascii=False, indent=4)

    print(f"{output_path} 저장 완료 ({len(chunk)}개 항목)")

print("모든 파일 저장 완료.")
