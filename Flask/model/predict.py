#  감정 분석 코드 파일
from sympy import Integer

from model.ai_name import tokenizer_6, model_6, device, tokenizer_2C, model_2C
from model.utils import label2mood_6
import torch
import numpy as np

def predict_polarity(text):

    # 인풋딕셔너리에 토크나이저_2C로 토큰화한 데이터를 넣음
    # 텍스트를 받은 후
        # 파이토치로 텐서화(return_tensors="pt")
        # 길면 자름 (truncation=True)
        # 모자라면 공백으로 채움 (padding=True)
    inputs = tokenizer_2C(text, return_tensors="pt", truncation=True, padding=True)

    # 인풋에 담겨진 목록의 키와 밸류값을 디바이스에 옮겨 담기
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        # 모델에 넘겨서 분석결과 받기
        logits = model_2C(**inputs).logits

    # 분석결과의 1차원인 열 부분을 대상으로 계산하여 확률로 변환
        # 스퀴즈로 의미없는 1차원을 제거하여
        # cpu로 담아서 넘파이 배열로 변경
    probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    print(f"로짓로짓: {logits}")
    print(f"프롭프롭: {probs}")
    
    pos_prob, neg_prob = probs[1], probs[0]

    # 3개 확률 합
    # total = pos_prob + neg_prob + neutral_prob

    # # 정규화
    # pos_prob_norm = pos_prob / total
    # neg_prob_norm = neg_prob / total
    # neutral_prob_norm = neutral_prob / total
    # 각 값을 토탈으로 나눠 총합이 1이 되도록 계산

    polarity_probs = {
        "긍정": float(pos_prob),
        "부정": float(neg_prob),
    }
    
    print(f"pos_prob: {pos_prob}, neg_prob: {neg_prob}")
    if pos_prob > neg_prob:
        print("긍정 판단")
        return "긍정", polarity_probs, pos_prob, neg_prob
    else:
        print("부정 판단")
        return "부정", polarity_probs, pos_prob, neg_prob

# 감정종류 라벨 6
def predict_6_moods(text, threshold = 0.05):
    inputs = tokenizer_6(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model_6(**inputs).logits
    print(f"model_6(**inputs).logits:{model_6(**inputs).logits}")
    array_probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    # threshold 적용
    filtered_probs = np.where(array_probs >= threshold, array_probs, 0)

    # labels mapping with probs (tuple)
    mood_probs = [(label2mood_6[idx], round(float(filtered_probs[idx]), 2)) for idx in range(len(filtered_probs))]

    return mood_probs, array_probs

# 긍정/부정 & 감정종류 라벨
def two_stage_mood_classification(text):
    # polarity, polarity_probs = predict_polarity(text)

    polarity, polarity_probs, pos_prob, neg_prob = predict_polarity(text)
    print(f"predict.py :: polarity: {polarity}, polarity_probs: {polarity_probs}")
    mood_probs, array_probs = predict_6_moods(text)
    print(f"predict.py ::mood_probs: {mood_probs}")
    polarity_result = int(round((pos_prob - neg_prob)*100, 0))
    
        # 여기 mood_probs는 numpy.ndarray임
    return {
            "stage": 1,
            "polarity": polarity,
            # "pos_prob": float(pos_prob),
            # "neg_prob": float(neg_prob),
            "polarity_probs": {
                "pos_prob": float(pos_prob),
                "neg_prob": float(neg_prob)
            },
            "polarity_result" : polarity_result,
            "labels": mood_probs, # tuple (label, probs)
            "probs": array_probs
        }



# if __name__ == "__main__":
#     text = input("분석할 문장을 입력하세요: ")
#     result = two_stage_mood_classification(text)
#     print("분석 결과:", result)