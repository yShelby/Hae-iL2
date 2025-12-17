import re

from ..rules.emojis import face_emojis

def _repeated_remover(sen_index : int, sentence : str, min_repeats: int, rules : list[dict]) -> tuple[list[dict],list[dict],str]:
    """
    문장 하나에서 반복 탐지 + 제거를 한 번에 처리하는 함수

    Args:
        sen_index: 현재 문장의 인덱스
        sentence: 처리할 문장
        min_repeats: 최소 반복 횟수
        rules: 반복 규칙 딕셔너리
        
    Returns:
        dict: {
            "cleaned_sentence": 정제된 문장,
            "repeated_items": 탐지된 반복 정보 리스트
        }
    """
     
    # 1-1. 반복 탐지
    pattern = re.compile(rf"(\w)\1{{{min_repeats - 1},}}"
                         rf"|([!?.,])\2{{{min_repeats - 1},}}"
                         rf"|([\u3131-\u318E])\3{{{min_repeats - 1},}}")
    matches = pattern.finditer(sentence) # 탐지

    # 1-2. 이모지 추출
    emojis_pattern = re.compile(f"[{face_emojis}]")
    emojis = emojis_pattern.findall(sentence) # 추출

     # 1-2. 제거에서 제외할 특수 문자 패턴
    special_char_pattern = re.compile(rf"[^A-Za-z0-9가-힣\u3131-\u318E\s!?.,{face_emojis}]")
    
    # 2. 반복 문자 리스트 수집
    repeated_items = [] # 탐지된 반복들을 리스트에 수집

    for match in matches:
        # unit 추출
        if match.group(1):  # 일반 단어 그룹
            unit = match.group(1)
        elif match.group(2):  # 특수문자 그룹
            unit = match.group(2)
        elif match.group(3):  # 한글 자음/모음 그룹
            unit = match.group(3)
            
        full = match.group()
        repeated_count = len(full) // len(unit)
        
        # 단어가 rules에 있으면 해당 단어 임계값으로 필터링
        if unit in rules:
            threshold = rules[unit].get("threshold", min_repeats)
            if repeated_count < threshold:
                continue
        
        # 반복 정보 저장
        repeated_items.append({
            "sentence_index": sen_index,
            "base_unit_candidate": unit,
            "matched_text": full,
            "repeat_count": repeated_count,
            "start": match.start(),
            "end": match.end(),
            "text": sentence
        })

    # 3. 수집된 반복 데이터들을 이용해서 해당 문장의 반복 문자 제거
    cleaned_sentence = sentence
    for item in repeated_items:
        cleaned_sentence = cleaned_sentence.replace(item["matched_text"], item["base_unit_candidate"])

    # 4. 특수문자 제거
    cleaned_sentence = special_char_pattern.sub('', cleaned_sentence)
    
    return repeated_items, emojis, cleaned_sentence