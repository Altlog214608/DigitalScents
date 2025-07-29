from datetime import datetime
import sqlite3

DS_TEST_DB = "dsTestDB.db"

# 환자(검사 대상자)를 위한 테이블
def createTableSubject():
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    query = "create table if not exists DS_TEST_SUBJECT(\
        SUBJECT_ID integer primary key autoincrement not null,\
        SUBJECT_NAME text,\
        BIRTH_DATE text,\
        GENDER text)"
    cur.execute(query)
    con.commit()
    con.close()

def insertTableSubject(text_name, text_birth_date, text_gender):
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    data = (text_name, text_birth_date, text_gender)
    query = "insert into DS_TEST_SUBJECT(SUBJECT_NAME, BIRTH_DATE, GENDER) values(?, ?, ?)" 
    cur.execute(query, data)
    con.commit()
    con.close()

def selectTableSubject():
    datas = [('subject_id', 'subject_name', 'subject_birth_date', 'subject_gender')]
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    query = "select * from DS_TEST_SUBJECT"
    cur.execute(query)
    data = cur.fetchall()
    # print("select data:", data)
    for id, name, birth_date, gender in data:
        datas.append((id, name, birth_date, gender))
    con.commit()
    con.close()
    print("select datas:", datas)
    return datas

def selectTableSubjectByName(text_name):
    datas = [('subject_id', 'subject_name', 'subject_birth_date', 'subject_gender')]
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    query = "select * from DS_TEST_SUBJECT where SUBJECT_NAME = '%s'" % text_name
    cur.execute(query)
    data = cur.fetchall()
    # print("select data:", data)
    for id, name, birth_date, gender in data:
        datas.append((id, name, birth_date, gender))
    con.commit()
    con.close()
    print("select datas:", datas)
    return datas

def selectTableSubjectByBirthDate(text_birth_date):
    datas = [('subject_id', 'subject_name', 'subject_birth_date', 'subject_gender')]
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    query = "select * from DS_TEST_SUBJECT where BIRTH_DATE = '%s'" % text_birth_date
    cur.execute(query)
    data = cur.fetchall()
    # print("select data:", data)
    for id, name, birth_date, gender in data:
        datas.append((id, name, birth_date, gender))
    con.commit()
    con.close()
    print("select datas:", datas)
    return datas

def selectTableSubjectKeywords(text_name="", text_birth_date=""):
    datas = [('subject_id', 'subject_name', 'subject_birth_date', 'subject_gender')]
    if text_name == "" and text_birth_date == "":
        return datas
    elif text_name == "":
        return selectTableSubjectByBirthDate(text_birth_date)
    elif text_birth_date == "":
        return selectTableSubjectByName(text_name)
    else:
        return datas


# [['문항', '정답', '선택', '정답여부', '응답(주관식)', '정답여부(주관식)'], 
# [1, '장미', '장미', 1, '주관식X', 0], 
# [2, '커피', '사과', 0, '주관식X', 0], 
# [3, '베이비파우더', '베이비파우더', 1, '주관식X', 0], 
# [4, '생강', '레몬', 0, '주관식X', 0], 
# [5, '딸기', '딸기', 1, '주관식X', 0], 
# [6, '녹차', '녹차', 1, '주관식X', 0], 
# [7, '재/연기', '바나나', 0, '주관식X', 0], 
# [8, '허브', '버섯', 0, '주관식X', 0], 
# [9, '멜론', '멜론', 1, '주관식X', 0], 
# [10, '나무', '나무', 1, '주관식X', 0], 
# [11, '비누', '비누', 1, '주관식X', 0], 
# [12, '초콜릿', '숯불고기', 0, '주관식X', 0]]


# 인지지검사 정보를 위한 테이블
def createTableTestID():
    con = sqlite3.connect(DS_TEST_DB)
    cur = con.cursor()
    query = "create table if not exists DS_TEST_ID(\
        SUBJECT_ID integer primary key,\
        SUBJECT_NAME text,\
        BIRTH_DATE text,\
        GENDER text,\
        TEST_DATETIME datetime,\
        TEST_SCORE int,\
        ANSWER_01 text,\
        ANSWER_02 text,\
        ANSWER_03 text,\
        ANSWER_04 text,\
        ANSWER_05 text,\
        ANSWER_06 text,\
        ANSWER_07 text,\
        ANSWER_08 text,\
        ANSWER_09 text,\
        ANSWER_10 text,\
        ANSWER_11 text,\
        ANSWER_12 text,\
        CHOICE_01 text,\
        CHOICE_02 text,\
        CHOICE_03 text,\
        CHOICE_04 text,\
        CHOICE_05 text,\
        CHOICE_06 text,\
        CHOICE_07 text,\
        CHOICE_08 text,\
        CHOICE_09 text,\
        CHOICE_10 text,\
        CHOICE_11 text,\
        CHOICE_12 text)"
    cur.execute(query)
    con.commit()
    con.close()

def insertTableTestID(text_name, text_birth_date, text_gender,\
                      int_answer_count, int_choice_count,\
                      datetime_test_id, int_test_score, test_id_data):
    data_answers = []
    data_choices = []
    for i in range(int_answer_count):
        if i > int_choice_count:
            data_answers.append("")
            data_choices.append("")
        else:
            data_answers.append(test_id_data['answer'])
            data_choices.append(test_id_data['choice'])

    print("insertTableTestID")
    print(data_answers)
    print(data_choices)
    



    # con = sqlite3.connect(DS_TEST_DB)
    # cur = con.cursor()
    # data = (text_name, text_birth_date, text_gender)
    # query = "insert into DS_TEST_ID(SUBJECT_NAME, BIRTH_DATE, GENDER) values(?, ?, ?)" 
    # cur.execute(query, data)
    # con.commit()
    # con.close()




if __name__ == "__main__":
    createTableSubject()
    now_date = datetime.now().date
    now_time = datetime.now().time
    insertTableSubject("김종우", "324892", "남성")
    insertTableSubject("최미윤", "821034", "여성")
    # insertCurrentTable("Rose", 32)
    # selectTableSubject()
    selectTableSubjectKeywords(text_name="김종우")
    selectTableSubjectKeywords(text_birth_date="821034")
    # selectDataFromTable("Lemon")