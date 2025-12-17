import json
import os

from .rules.repetition_rules_v1 import REPETITION_RULES
from .preprocessing_logic.repeated_remover import _repeated_remover
from .preprocessing_logic.morpheme_tagger import _morpheme_tagger

from .comparing_logic.pos_filter import _pos_filter
from .comparing_logic.pos_filter import _negative_filter
from .comparing_logic.diary_dict_comparer import _diary_dict_comparer
from .comparing_logic.negative_processer import _negative_processer

from collections import Counter
from .scoring_logic.small_dataset_handler import _small_dataset_handler
from .scoring_logic.large_dataset_handler import _large_dataset_handler

#=====================================#

# 다이어리 호출

# with open("./diary1.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
    
# # extract context
# diary_text = data["context"]

#=====================================#

# 감정 사전 호출

# 현재 파일의 절대 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# .dict 폴더의 JSON 파일 경로
dict_path = os.path.join(current_dir, "dict", "sentiword_info_cleaned_v1"
".json")

# 파일 열기
with open(dict_path, 'r', encoding='utf-8') as f:
    sentiment_dic = json.load(f)
    
#=====================================#
    
def extract_mood_with_dict(sentences) -> dict:

    # =====================================#

    # 1. 일기 텍스트 전처리 (start : str)

    # 결과 리스트
    results_preprocess = []

    for index, sentence in enumerate(sentences) : 
        # 분리된 문장의 앞 뒤 공백 제거
        sentence = sentence.strip()

        # 2. [반복 문자 카운트, 이모지 리스트, 반복 문자 및 불필요한 특수 문자가 제거된 문장]
        repeated_items, emojis, remove_repeats = _repeated_remover(index, sentence, min_repeats=3, rules=REPETITION_RULES)

        # 3. 형태소 분석 + 품사 Tagging
        analyze_morpheme = _morpheme_tagger(index, remove_repeats)
        print(f"analyze_morpheme : {analyze_morpheme}")

        # 결과 리스트에 넣기
        results_preprocess.append(analyze_morpheme)  # list[list[tuple[str, str]]]

    #=====================================#   

    # 2. 일기 vs. 감성사전

    # 1) 원하는 품사만 추출하기

    # 감정어 후보군
    mood_target_pos = {"NNG","VV","VA","MAG","XR"} # 감성사전의 어근과 비교할 : 일반명사, 동사, 형용사, 부사, 어근
    mood_candidate = _pos_filter(results_preprocess, mood_target_pos)

    # 부정어 후보군
    NEGATIVE_WORDS = {('안', 'MAG'), ('못', 'MAG'), ('않', 'VX'), ('없', 'VA'), ('아니', 'MAG'), ('모르', 'VV'), ('다르', 'VA')} # 부정어 리스트 (set(tuple))
    negation_candidate = _negative_filter(results_preprocess, NEGATIVE_WORDS)

    # 2) 일기 word_root를 감성사전 word_root와 비교
    # {word_root, polarity, label, tag} 추출
    compared_mood = _diary_dict_comparer(mood_candidate, sentiment_dic)

    # 3) 부정어 처리
    negative_processing = _negative_processer(compared_mood, negation_candidate)

    # 4) 레이블 '' 삭제 처리
        # list comprehension : [<넣을_값> for <변수> in <반복_대상> if <조건>]
    results_mood = [item for item in negative_processing if not(item.get("label") == '' or item.get("tag") == '')]  # list[dict]


    #=====================================#  

    # 3. 감정 점수 추출

    # 1. 가중치
    small_threshold = 5 # 소량 데이터 가중치
    last_threshold = 2 # 마지막 감정어 가중치

    p_threshold_sa = -1 # small dataset polarity 분자 가중치
    p_threshold_sb = 3 # small dataset polarity 분모 가중치
    p_threshold_la = 0 # large dataset polarity 분자 가중치
    p_threshold_lb = 2 # large dataset polarity 분모 가중치

    min_count = 3 # 레이블 빈도 가중치
    top_label = 3 # 레이블 출력 개수
    top_tag = 3 # 태그 출력 개수

    neutral_threshold = 9 # 중립/기타 분기 가중치

    # 2. 레이블 개수 세기 (소량 데이터 판단)
    labels_list = [item["label"] for item in results_mood]
    labels_count = Counter(labels_list).most_common()

    # 3. 케이스 분기
    if not labels_count : # 1) 감정 결과 없음
        polarity_score = 0
        label_list = [{"label" : "중립/기타", "count" : 0, "percentage" : 100}]
        tag_list = ["#무난한"]

    elif labels_count[0][1] < small_threshold : # 2) 소량 데이터 : 최빈도 레이블 < small_threshold
        polarity_score, label_list, tag_list = _small_dataset_handler(results_mood, p_threshold_sa, p_threshold_sb, last_threshold, top_label)

    else : # 3) 일반 데이터 : 레이블 빈도수 >= min_count 존재할 때
        polarity_score, label_list, tag_list = _large_dataset_handler(results_mood, labels_count, p_threshold_la, p_threshold_lb, min_count, top_label, top_tag, neutral_threshold)

    # 4. 결과 도출
    results_score = {"polarity": polarity_score, "label": label_list, "tag": tag_list}
    
    return results_score


#=====================================#  


# if __name__ == "__main__" :

#     test1 = results_score

#     print(f"RESULT : {test1}, len : {len(mood_candidate)}")
    
    