import dsText

id_time_count = 0

id_test_index = 0 # 인지검사 현재 번호
id_temp_response = ""

# 인지검사 결과 데이터
id_results_title = ['문항', '정답', '선택', '정답여부', '응답(주관식)', '정답여부(주관식)']
# id_results_title = ['Question', 'Correct answer', 'Your selection', 'O/X', '응답(주관식)', '정답여부(주관식)']
id_results = []

I_score = 0

# 인지검사 문항 데이터

id_test_data = [{'choice1': '땅콩',
                 'choice2': '케챱',
                 'choice3': '장미',
                 'choice4': '양파',
                 'answer': '장미',
                 'scent_no': 1,
                 'outlet_no': 1},
                
                {'choice1': '마늘',
                 'choice2': '초콜릿',
                 'choice3': '오이',
                 'choice4': '레몬',
                 'answer': '초콜릿',
                 'scent_no': 2,
                 'outlet_no': 1},

                {'choice1': '생강',
                 'choice2': '솜사탕',
                 'choice3': '사과',
                 'choice4': '당근',
                 'answer': '생강',
                 'scent_no': 3,
                 'outlet_no': 1},

                {'choice1': '빵',
                 'choice2': '겨자',
                 'choice3': '오징어',
                 'choice4': '멜론',
                 'answer': '멜론',
                 'scent_no': 4,
                 'outlet_no': 1},

                {'choice1': '쌀',
                 'choice2': '사과',
                 'choice3': '소나무',
                 'choice4': '고구마',
                 'answer': '소나무',
                 'scent_no': 5,
                 'outlet_no': 1},

                {'choice1': '생선',
                 'choice2': '베이비파우더',
                 'choice3': '카레',
                 'choice4': '키위',
                 'answer': '베이비파우더',
                 'scent_no': 6,
                 'outlet_no': 1},

                {'choice1': '녹차',
                 'choice2': '마늘',
                 'choice3': '간장',
                 'choice4': '쇠',
                 'answer': '녹차',
                 'scent_no': 7,
                 'outlet_no': 1},

                {'choice1': '후추',
                 'choice2': '딸기',
                 'choice3': '계란',
                 'choice4': '홍삼',
                 'answer': '홍삼',
                 'scent_no': 8,
                 'outlet_no': 1},
                 
                {'choice1': '나무',
                 'choice2': '가죽',
                 'choice3': '복숭아',
                 'choice4': '김치',
                 'answer': '복숭아',
                 'scent_no': 9,
                 'outlet_no': 1},
                 
                {'choice1': '재/연기',
                 'choice2': '옥수수',
                 'choice3': '바나나',
                 'choice4': '잔디',
                 'answer': '재/연기',
                 'scent_no': 10,
                 'outlet_no': 1},

                {'choice1': '꿀',
                 'choice2': '버섯',
                 'choice3': '페퍼민트',
                 'choice4': '담배',
                 'answer': '페퍼민트',
                 'scent_no': 11,
                 'outlet_no': 1},

                {'choice1': '청포도',
                 'choice2': '비누',
                 'choice3': '국수',
                 'choice4': '고무',
                 'answer': '비누',
                 'scent_no': 12,
                 'outlet_no': 1}
                 ]