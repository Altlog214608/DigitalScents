import dsText

dc_time_count = 0

dc_test_index = 0 # 식별검사 현재 번호
dc_temp_response = 0

# 식별검사 결과 데이터
dc_results_title = ['문항', '향1번호', '향2번호', '향3번호', '정답', '선택', '정답여부']
dc_results = []

D_score = 0

# 식별검사 문항 데이터
dc_test_data = [{'scent_no1': 17,
                 'scent_no2': 18,
                 'scent_no3': 18,
                 'answer': 1,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 20,
                 'scent_no2': 20,
                 'scent_no3': 19,
                 'answer': 3,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 22,
                 'scent_no2': 22,
                 'scent_no3': 21,
                 'answer': 3,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 23,
                 'scent_no2': 24,
                 'scent_no3': 24,
                 'answer': 1,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                  'outlet_no': 2},
                {'scent_no1': 26,
                 'scent_no2': 25,
                 'scent_no3': 26,
                 'answer': 2,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 28,
                 'scent_no2': 28,
                 'scent_no3': 27,
                 'answer': 3,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 30,
                 'scent_no2': 29,
                 'scent_no3': 30,
                 'answer': 2,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 31,
                 'scent_no2': 32,
                 'scent_no3': 32,
                 'answer': 1,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 34,
                 'scent_no2': 34,
                 'scent_no3': 33,
                 'answer': 3,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 36,
                 'scent_no2': 35,
                 'scent_no3': 36,
                 'answer': 2,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 38,
                 'scent_no2': 38,
                 'scent_no3': 37,
                 'answer': 3,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2},
                {'scent_no1': 39,
                 'scent_no2': 40,
                 'scent_no3': 40,
                 'answer': 1,  # 실제 향이 나오는 순서: 이 순서를 맞춰야 정답
                 'outlet_no': 2}]