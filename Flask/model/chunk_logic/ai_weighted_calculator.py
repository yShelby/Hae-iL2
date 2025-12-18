from model.predict import two_stage_mood_classification # 분석 모델
from dictionary.scoring_logic.percentage_calculator import _percentage_calculator # percentage 계산
from dictionary.scoring_logic.neutral_creator import _neutral_creator # percentage 계산

def _ai_weighted_calculator(chunks, tokens, total_token, top_k = 3, min_display_pct = 10) :
    weighted_polarity_sum = 0
    weighted_labels_sum = {} # dict 형태

    for chunk, token in zip(chunks, tokens):
        chunk_result = two_stage_mood_classification(chunk)  # AI LLM을 이용한 감정점수, 세부감정 라벨 추출

        # 1. polarity 점수 계산
        weighted_polarity_sum += chunk_result.get("polarity_result", 0) * token # 토큰 수를 가중치로 둔 polarity 점수 계산
                                                                               # 토큰 먼저 곱 : 소수점 뒷자리 오차 누적을 방지
        # 2. label별 probs 계산
        for label, prob in chunk_result.get("labels", []): # tuple 형태 (label, prob)
            # 가중치 적용 (dict 형태)
                # label을 키값으로 만듦
                    # 기존값 : weighted_labels_sum에 동일한 label 키가 있으면 그 값을 부름. 없다면 0으로 설정
                    # 새로운 가중치 값 : prob * token
            weighted_labels_sum[label] = weighted_labels_sum.get(label, 0) + prob * token # { 기쁨/행복 : 0.6, 슬픔/우울: 0.3, ...}

    # 1-2. 가중 평균 polarity 계산
    polarity_result = round(weighted_polarity_sum / total_token) if total_token and total_token > 0 else 0 # total_token이 null이거나 0일 때는 0으로 반환

    # 2-2. 가중 평균 probability of labels 계산
    weighted_labels = {label: prob_sum / total_token for label, prob_sum in weighted_labels_sum.items()} # dictionary comprehension

    # 2-3. Top_k 선택 (label을 빈도수로 정렬 후 top_k)
    sorted_probs = sorted(weighted_labels.items(), key=lambda x: x[1], reverse=True)[:top_k]  # [(기쁨/행복, 0.6), (슬픔/우울, 0.3)...]

    # 2-4. Percentage 계산
    total_probs = sum(prob for _, prob in sorted_probs) # probabilities 총합
    pct_labels = _percentage_calculator(sorted_probs, total_probs)

    # 2-5. 중립/기타 처리 (min_display_pct = 10%)
    label_results = _neutral_creator(pct_labels, min_display_pct)

    return {
        "polarity_result" : polarity_result,
        "labels" : [{"mood_type": item["label"], "percentage": item["percentage"]} for item in label_results]
    }
