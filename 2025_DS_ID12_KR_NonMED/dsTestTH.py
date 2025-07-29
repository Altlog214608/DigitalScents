th_time_count = 0

th_test_index = 0 # 역치검사 현재 번호
th_test_max_sequence = 3 # 역치검사 한회에서 수행하는 최대 순서
th_test_total_number = 100 # 역치검사 마지막 횟수

th_test_current_level = 1 # 역치검사 현재 농도 단계
th_is_last_correct = -1 # 지난 검사 결과 (-1:초기상태, 0:지난회 오답, 1: 지난회 정답)
th_node_num = 0 # 변곡점 번호
th_scent_offset = 0 # 카트리지 번호 시작점 (17번이 최저 농도이면, offset = 16)
th_scent_none = 13 # 무향이 나온느 카트리지 번호
th_temp_response = 0

# 역치검사 결과 데이터
th_results_title = ['회차', '역치', '향 농도', '정답', '선택', '정답여부', '변곡점여부', '변곡점번호']
th_results = []

T_score = 0

# 역치검사 문항 데이터 (PEA향이 나오는 순서, 이 순서를 맞춰야 정답)
th_test_data = [{'scent_squence': 2},  # 실제 부탄올 향이 나오는 순서: 이 순서를 맞춰야 정답
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 2},
                {'scent_squence': 1},
                {'scent_squence': 3},
                {'scent_squence': 2}]