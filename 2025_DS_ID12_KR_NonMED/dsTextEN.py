serialText = {
    'status_open': 'Serial port is opened.',
    'status_close': 'Serial port is not opened.',
    'status_connect': 'Connect',
    'status_disconnect': 'Disconnect',
}

processText = {
    'cleaning': 'Hold your nose. Cleaning process is in progress.',
    'question_number': 'Question',
    'progress_scent': 'Scent diffusion is in progress.',
    'progress_scent_1': '1번 향기 발향 중입니다.',
    'progress_scent_2': '2번 향기 발향 중입니다.',
    'progress_scent_3': '2번 향기 발향 중입니다.',
    'question_threshold': '향이 느껴진 번호를 선택하세요.',
    'try_scent_threshold': '검사용 향을 확인해보시기 바랍니다.',\
    'question_discrimination': '다른 향기가 느껴진 번호를 한 개만 선택하세요.',
    'question_identification': 'Select the scent you experienced.', # 'Press the button to choose the scent image\nexperienced from these four options.',
    'question_train_st': '[자가 평가]\n향이 느껴진 강도를 0 ~ 10 중에서 평가하세요.',
    # '[Self-Check]\nRate your smell intensity from 0 to 10.',
}
# dsText.processText['question_number']

resultText = {
    'index': '문항',
    'scent_no1': '향1번호',
    'scent_no2': '향2번호',
    'scent_no3': '향3번호',
    'answer': '정답',
    'response': '선택',
    'is_correct': '응답여부',
    'index_correct': 'Correct',
    'index_incorrect': 'Incorrect',

    'results_data_path': 'data',
    'results_data_raw_path': 'data_raw',
    'results_save': 'data 폴더에 저장되었습니다.',
    'results_save_none': '저장할 데이터가 없습니다.',

    'result_test_threshold_title': '후각 역치검사 결과',
    'result_test_threshold_score': '역치검사 점수',
    'result_test_threshold_seq': '회차',
    'result_test_threshold_level': '역치',
    'result_test_threshold_density': '향 농도도',
    'result_test_threshold_time': '시간',
    'result_test_threshold_point': '점수',
    'result_test_threshold_range': 12,
    
    'result_test_discrimination_title': '후각 식별검사 결과',
    'result_test_discrimination_score': '식별검사 점수',
    'result_test_discrimination_seq': '회차',
    'result_test_discrimination_correct': '정답',
    'result_test_discrimination_incorrect': '오답',
    'result_test_discrimination_time': '시간',
    'result_test_discrimination_point': '점수',
    'result_test_discrimination_range': 12,
    
    'result_test_identification_title': '후각 인지검사 결과',
    'result_test_identification_score': '인지검사 점수',
    'result_test_identification_seq': '회차',
    'result_test_identification_correct': '정답',
    'result_test_identification_incorrect': '오답',
    'result_test_identification_time': '시간',
    'result_test_identification_point': '점수',
    'result_test_identification_range': 12,
}
# dsText.resultText['index_correct']

reportText = {
    'report_data_path': 'data',
    'report_data_temp_path': 'data_temp',
    
    'report_sheet': 'DigitalOlfactoryTestReport',
    'report_sheet_threshold': 'Threshold',
    'report_sheet_discrimination': 'Discrimination',
    'report_sheet_identification': 'Identification',

    'report_title': '디지털 후각 검사 결과지 (Digital Olfactory Test Report)',
    'report_reg_num': '등록번호',
    'report_date': '검사일자',
    'report_name': '이름',
    'report_gender': '성별',
    'report_age': '나이',
    'report_both_nostrils': '양측(   )',
    'report_right_nostril': '우측(   )',
    'report_left_nostril': '좌측(   )',
    'report_ammonia': 'Ammonia Response',
    'report_total_score': '종합 점수',
    'report_nomosmia': 'Nomosmia',
    'report_hyposmia': 'Hyposmia',
    'report_anosmia': 'Anosmia',
}
# dsText.reportText['report_sheet_threshold']

reviewText = {
    'review_test_title': '평가 의견',
    'review_test_score': '만족도/불편도 점수',
    'review_test_range': 12,
}
# dsText.reviewText['review_test_range']

# 주관식 처리 필요
# 감각 훈련 처리 필요
# saveData 년, 월, 일 처리
