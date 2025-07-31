""" Scent Smart (Digital Scent Olfactory Solution) """
import os
import sys
import json
import struct
import xlsxwriter
import serial

from datetime import datetime

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtTest
# from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import Qt, QCoreApplication, QTimer
from PySide6.QtCore import Signal #Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QScroller, QAbstractItemView, QLineEdit

import dsSerial
import dsComm
import dsSetting
import dsSound, dsText, dsUtils, dsUiCustom
import dsTest, dsTestTH, dsTestDC, dsTestID 
import dsTestDB
import dsTrainST, dsTrainSTDB
import dsTrainID

from dsImage import dsBtnImg, dsBgImg, dsResultImg
from dsUiChartWidget import scentPieChartWidget, scentLineChartWidget
from dsUiCustom import scentSlider

os.environ["PYSIDE_DESIGNER_PLUGINS"] = "."
# __platform__ = sys.platform

# UI 관리 클래스
class UiDlg(QWidget):

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def __init__(self):
        super().__init__()
        # 시리얼 통신 수신 설정
        self.setSerialReadThread()
        # 시작시 설정 반영
        self.loadSettingsFile()

    # 다이얼로그 종료시 오류 해결
    def closeEvent(self, event):
        self.deleteLater()
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 시리얼 통신 설정 (Signal, Thread, Read, Write, Console지정)
    _serial_received_data = Signal(bytes, name="serialReceivedData")

    def setSerialReadThread(self):
        self._serial = serial.Serial()
        self._serial_read_thread = dsSerial.SerialReadThread(self._serial)
        self._serial_read_thread._serial_received_data.connect(lambda v: self._serial_received_data.emit(v))
        self._serial_received_data.connect(self.readSerialData)
        self._serial_read_thread.start(QtCore.QThread.Priority.HighestPriority)
    
    def readSerialData(self, rdata):
        self._serial_console.append("RX(%d):"%len(rdata) + str(rdata.hex()))
        self._serial_console.moveCursor(QtGui.QTextCursor.End)
        print("RX(%d):"%len(rdata) + str(rdata.hex()))
        self.parseReadData(rdata)

    def write_data(self, wdata):
        # print("write_data")
        if dsSerial._is_open(self._serial):
            self._serial.write(wdata)
            self._serial_console.append("TX(%d):"%len(wdata) + str(wdata.hex()))
            self._serial_console.moveCursor(QtGui.QTextCursor.End)
            print("TX(%d):"%len(wdata) + str(wdata.hex()))
        else:
            self._serial_console.append(dsText.serialText['status_close'])
            self._serial_console.moveCursor(QtGui.QTextCursor.End)
            print(dsText.serialText['status_close'])

    def setSerialConsole(self, text_console):
        self._serial_console = text_console

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 텍스트 입력 Enter key 필터링
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.KeyPress: # and obj is self.text_box:
            if event.key() == QtCore.Qt.Key.Key_Return: # and self.text_box.hasFocus():
                return True
                # print('Enter pressed')
            if event.key() == QtCore.Qt.Key.Key_Tab:
                return True
                # print('Tab pressed')
        return super().eventFilter(obj, event)
    
    # 창 모양
    def setWindowBySetting(self, dialog):
        if dsSetting.dsParam['window_bars_onoff'] == 1:
            dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint) # 강제 설정해야 문제 상황 없을 것
        if dsSetting.dsParam['front_onoff'] == 1:
            dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    # 현재 창 위치에서 새 창으로 전환하기
    def uiDlgChange(self, prev_dlg, next_dlg):
        prev_dlg.hide()
        next_qr = next_dlg.frameGeometry()
        self.prev_cp = prev_dlg.frameGeometry().center()
        next_qr.moveCenter(self.prev_cp)
        next_dlg.move(next_qr.topLeft())
        next_dlg.show()


    def uiDlgShow(self, next_dlg):
        next_dlg.show()

    # 현재 창 위치에서 새 창 팝업하기
    def uiDlgShowUp(self, prev_dlg, next_dlg):
        next_qr = next_dlg.frameGeometry()
        self.prev_cp = prev_dlg.frameGeometry().center()
        next_qr.moveCenter(self.prev_cp)
        next_dlg.move(next_qr.topLeft())
        next_dlg.show()

    # 팝업 창과 현재 창 2개 닫과 새 창으로 전환하기
    def uiDlgChangeWithDlg(self, prev_dlg, popup_dlg, next_dlg):
        prev_dlg.hide()
        popup_dlg.hide()
        next_qr = next_dlg.frameGeometry()
        self.prev_cp = prev_dlg.frameGeometry().center()
        next_qr.moveCenter(self.prev_cp)
        next_dlg.move(next_qr.topLeft())
        next_dlg.show()

    def uiDlgHide(self, dlg):
        dlg.hide()
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 시작
    def uiDlgStart(self):
        self.uiDlgInit()
        self.ui_main_dlg.show()
        dsSound.playGuideSound('intro_main')

    # UI 연동 호출: UI객체.objectname.이벤트(QtSignal).connect(함수명)
    def uiDlgInit(self):
        uiLoader = QUiLoader()
        # Custom Widget 등록 (승격된 위젯)
        uiLoader.registerCustomWidget(scentLineChartWidget)
        uiLoader.registerCustomWidget(scentPieChartWidget)
        uiLoader.registerCustomWidget(scentSlider)
        # UI 개별 로딩
        self.uiDlgProtocol(uiLoader)
        self.uiDlgMain(uiLoader)
        self.uiDlgLogin(uiLoader)
        self.uiDlgSubject(uiLoader)
        self.uiDlgMenu(uiLoader)
        # self.uiDlgTestThreshold(uiLoader)
        # self.uiDlgTestDiscrimination(uiLoader)
        self.uiDlgTestIdentification(uiLoader)
        # self.uiDlgTrainST(uiLoader)
        # self.uiDlgTrainID(uiLoader)
        self.uiDlgMessages(uiLoader)
        self.uiDlgSettings(uiLoader)
        self.uiDlgTimer()
        self.uiDlgDB()

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 메인
    def uiDlgMain(self, uiLoader):
        self.ui_main_dlg = uiLoader.load(
            "./ui/ui_main.ui")

        self.ui_main_dlg.ui_main_btn_login.clicked.connect(self.uiMainBtnLogin)
        self.ui_main_dlg.ui_main_btn_exit.clicked.connect(self.uiMainBtnExit)

        self.ui_main_dlg.ui_main_btn_help.setVisible(False)
        # self.ui_main_dlg.ui_main_btn_help.clicked.connect(self.uiMainBtnHelp)
        # self.ui_main_dlg.textEdit_name.installEventFilter(self)
        # self.ui_main_dlg.textEdit_age.installEventFilter(self)

        self.setWindowBySetting(self.ui_main_dlg)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 로그인 관리
    def uiDlgLogin(self, uiLoader):
        self.ui_dlg_login = uiLoader.load(
            "./ui/ui_dlg_login.ui")
        self.ui_dlg_login.le_pw.setEchoMode(QLineEdit.Password)
        self.ui_dlg_login.pb_start.clicked.connect(self.uiDlgLoginStart)
        self.ui_dlg_login.pb_reset_pw.clicked.connect(self.uiDlgLoginResetPW)

        self.setWindowBySetting(self.ui_dlg_login)

        self.ui_dlg_login_resetpw = uiLoader.load(
            "./ui/ui_dlg_login_resetpw.ui")
        self.ui_dlg_login_resetpw.le_pw_old.setEchoMode(QLineEdit.Password)
        self.ui_dlg_login_resetpw.le_pw_new.setEchoMode(QLineEdit.Password)
        self.ui_dlg_login_resetpw.le_pw_new_check.setEchoMode(QLineEdit.Password)
        self.ui_dlg_login_resetpw.pb_reset.clicked.connect(self.uiDlgLoginResetPWReset)


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 환자 정보 관리
    def uiDlgSubject(self, uiLoader):
        self.ui_subject_dlg = uiLoader.load(
            "./ui/ui_subject.ui")

        # self.ui_subject_dlg.ui_main_btn_login.clicked.connect(self.uiMainBtnLogin)
        # self.ui_subject_dlg.ui_main_btn_exit.clicked.connect(self.uiMainBtnExit)


        self.setWindowBySetting(self.ui_subject_dlg)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 메뉴
    def uiDlgMenu(self, uiLoader):
        self.ui_menu_dlg = uiLoader.load(
            "./ui/ui_menu.ui")
        self.ui_menu_dlg.ui_menu_btn_quit.clicked.connect(
            self.uiMenuBtnQuit)
        self.ui_menu_dlg.ui_menu_btn_test_threshold.clicked.connect(
            self.uiMenuBtnTestThreshold)
        self.ui_menu_dlg.ui_menu_btn_test_threshold.setVisible(False)
        self.ui_menu_dlg.ui_menu_btn_test_discrimination.clicked.connect(
            self.uiMenuBtnTestDiscrimination)
        self.ui_menu_dlg.ui_menu_btn_test_discrimination.setVisible(False)
        self.ui_menu_dlg.ui_menu_btn_test_identification.clicked.connect(
            self.uiMenuBtnTestIdentification)
        self.ui_menu_dlg.ui_menu_btn_test_results.clicked.connect(
            self.uiMenuBtnTestResults)
        self.ui_menu_dlg.ui_menu_btn_test_results.setVisible(False)
        self.ui_menu_dlg.ui_menu_btn_settings.clicked.connect(
            self.uiMenuBtnSettings)
        # self.ui_menu_dlg.pb_test.setVisible(False)
        self.ui_menu_dlg.pb_test.clicked.connect(
            self.uiMenuBtnTest)
        self.ui_menu_dlg.ui_menu_btn_train_st.setVisible(False)
        self.ui_menu_dlg.ui_menu_btn_train_st.clicked.connect(
            self.uiMenuBtnTrainST)
        self.ui_menu_dlg.ui_menu_btn_train_id.setVisible(False)
        self.ui_menu_dlg.ui_menu_btn_train_id.clicked.connect(
            self.uiMenuBtnTrainID)
        self.setWindowBySetting(self.ui_menu_dlg)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 후각 역치 검사
    def uiDlgTestThreshold(self, uiLoader):
        # 후각 역치 검사 가이드
        self.ui_test_threshold_guide_picture = uiLoader.load(
            "./ui/ui_test_threshold_1_guide_picture.ui")
        self.ui_test_threshold_guide_picture.ui_test_btn_back.clicked.connect(
            self.uiTestThresholdGuidePictureBtnBack)
        self.ui_test_threshold_guide_picture.ui_test_btn_forward.clicked.connect(
            self.uiTestThresholdGuidePictureBtnForward)
        # self.ui_test_threshold_guide_picture.ui_test_btn_practice.clicked.connect(
        #     self.uiTestThresholdBtnPractice)
        self.ui_test_threshold_guide_picture.ui_test_btn_try_scent.clicked.connect(
            self.uiTestThresholdBtnTryScent)
        self.setWindowBySetting(self.ui_test_threshold_guide_picture)
        
        # 후각 역치 검사 준비
        self.ui_test_threshold_ready = uiLoader.load(
            "./ui/ui_test_threshold_2_ready.ui")
        self.setWindowBySetting(self.ui_test_threshold_ready)

        # 후각 역치 검사 시향 (역치 검사만 시향함)
        self.ui_test_threshold_try_scent = uiLoader.load(
            "./ui/ui_test_threshold_try_scent.ui")
        self.setWindowBySetting(self.ui_test_threshold_try_scent)

        # 후각 역치 검사 응답
        self.ui_test_threshold_response = uiLoader.load(
            "./ui/ui_test_threshold_3_response.ui")
        self.ui_test_threshold_response.pb_check_1.clicked.connect(
            self.uiTestThresholdResponseChoice1)
        self.ui_test_threshold_response.pb_check_2.clicked.connect(
            self.uiTestThresholdResponseChoice2)
        self.ui_test_threshold_response.pb_check_3.clicked.connect(
            self.uiTestThresholdResponseChoice3)
        self.ui_test_threshold_response.ui_menu_btn_quit.clicked.connect(
            self.uiTestThresholdResponseQuit)
        self.ui_test_threshold_response.pb_retry.clicked.connect(
            self.uiTestThresholdResponseRetry)
        self.ui_test_threshold_response.pb_next.clicked.connect(
            self.uiTestThresholdResponseNext)
        self.ui_test_threshold_response.pb_try_scent.clicked.connect(
            self.uiTestThresholdResponseTryScent)
        self.ui_test_threshold_response.pb_node_1.setVisible(False)
        self.ui_test_threshold_response.pb_node_2.setVisible(False)
        self.ui_test_threshold_response.pb_node_3.setVisible(False)
        self.ui_test_threshold_response.pb_node_4.setVisible(False)
        self.ui_test_threshold_response.pb_node_5.setVisible(False)
        self.ui_test_threshold_response.pb_node_6.setVisible(False)
        self.ui_test_threshold_response.pb_node_7.setVisible(False)
        self.setWindowBySetting(self.ui_test_threshold_response)

        # 후각 역치 검사 종료
        self.ui_test_threshold_completion = uiLoader.load(
            "./ui/ui_test_threshold_5_completion.ui")
        self.ui_test_threshold_completion.pb_complete.clicked.connect(
            self.uiTestThresholdCompletionComplete)
        self.setWindowBySetting(self.ui_test_threshold_completion)

        # 후각 역치 검사 결과
        self.ui_test_threshold_results = uiLoader.load(
            "./ui/ui_test_threshold_6_results.ui")
        self.ui_test_threshold_results.pushButton_confirm.clicked.connect(
            self.uiTestThresholdResultsConfirm)
        self.ui_test_threshold_results.ui_menu_btn_quit.clicked.connect(
            self.uiTestThresholdResultsConfirm)
        self.setWindowBySetting(self.ui_test_threshold_results)

        # 후각 역치 검사 시작시 확인
        self.ui_test_threshold_start_confirm = uiLoader.load(
            "./ui/ui_start_confirm.ui")
        self.ui_test_threshold_start_confirm.pb_start.clicked.connect(
            self.uiTestThresholdStartConfirmStart)
        self.ui_test_threshold_start_confirm.pb_resume.clicked.connect(
            self.uiTestThresholdStartConfirmResume)
        self.ui_test_threshold_start_confirm.pb_close.clicked.connect(
            self.uiTestThresholdStartConfirmClose)
        self.setWindowBySetting(self.ui_test_threshold_start_confirm)
        self.ui_test_threshold_start_confirm.setWindowModality(Qt.WindowModality.ApplicationModal)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def uiDlgTestDiscrimination(self, uiLoader):
        # 후각 식별 검사 가이드
        self.ui_test_discrimination_guide_picture = uiLoader.load(
            "./ui/ui_test_discrimination_1_guide_picture.ui")
        self.ui_test_discrimination_guide_picture.ui_test_btn_back.clicked.connect(
            self.uiTestDiscriminationGuidePictureBtnBack)
        self.ui_test_discrimination_guide_picture.ui_test_btn_forward.clicked.connect(
            self.uiTestDiscriminationGuidePictureBtnForward)
        self.setWindowBySetting(self.ui_test_discrimination_guide_picture)
        
        # 후각 식별 검사 준비
        self.ui_test_discrimination_ready = uiLoader.load(
            "./ui/ui_test_discrimination_2_ready.ui")
        self.setWindowBySetting(self.ui_test_discrimination_ready)

        # 후각 식별 검사 응답
        self.ui_test_discrimination_response = uiLoader.load(
            "./ui/ui_test_discrimination_3_response.ui")
        self.ui_test_discrimination_response.pb_check_1.clicked.connect(
            self.uiTestDiscriminationResponseChoice1)
        self.ui_test_discrimination_response.pb_check_2.clicked.connect(
            self.uiTestDiscriminationResponseChoice2)
        self.ui_test_discrimination_response.pb_check_3.clicked.connect(
            self.uiTestDiscriminationResponseChoice3)
        self.ui_test_discrimination_response.ui_menu_btn_quit.clicked.connect(
            self.uiTestDiscriminationResponseQuit)
        self.ui_test_discrimination_response.pb_retry.clicked.connect(
            self.uiTestDiscriminationResponseRetry)
        self.ui_test_discrimination_response.pb_next.clicked.connect(
            self.uiTestDiscriminationResponseNext)
        self.setWindowBySetting(self.ui_test_discrimination_response)
        
        # 후각 식별 검사 종료
        self.ui_test_discrimination_completion = uiLoader.load(
            "./ui/ui_test_discrimination_5_completion.ui")
        self.ui_test_discrimination_completion.pb_complete.clicked.connect(
            self.uiTestDiscriminationCompletionComplete)
        self.setWindowBySetting(self.ui_test_discrimination_completion)

        # 후각 식별 검사 결과
        self.ui_test_discrimination_results = uiLoader.load(
            "./ui/ui_test_discrimination_6_results.ui")
        self.ui_test_discrimination_results.pushButton_confirm.clicked.connect(
            self.uiTestDiscriminationResultsConfirm)
        self.ui_test_discrimination_results.ui_menu_btn_quit.clicked.connect(
            self.uiTestDiscriminationResultsConfirm)
        self.setWindowBySetting(self.ui_test_discrimination_results)
        
        # 후각 식별 검사 시작시 확인
        self.ui_test_discrimination_start_confirm = uiLoader.load(
            "./ui/ui_start_confirm.ui")
        self.ui_test_discrimination_start_confirm.pb_start.clicked.connect(
            self.uiTestDiscriminationStartConfirmStart)
        self.ui_test_discrimination_start_confirm.pb_resume.clicked.connect(
            self.uiTestDiscriminationStartConfirmResume)
        self.ui_test_discrimination_start_confirm.pb_close.clicked.connect(
            self.uiTestDiscriminationStartConfirmClose)
        self.setWindowBySetting(self.ui_test_discrimination_start_confirm)
        self.ui_test_discrimination_start_confirm.setWindowModality(Qt.WindowModality.ApplicationModal)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def uiDlgTestIdentification(self, uiLoader):
        # 후각 인지 검사 가이드
        self.ui_test_identification_guide_picture = uiLoader.load(
            "./ui/ui_test_identification_1_guide_picture.ui")
        self.ui_test_identification_guide_picture.ui_test_btn_back.clicked.connect(
            self.uiTestIdentificationGuidePictureBtnBack)
        self.ui_test_identification_guide_picture.ui_test_btn_forward.clicked.connect(
            self.uiTestIdentificationGuidePictureBtnForward)
        self.setWindowBySetting(self.ui_test_identification_guide_picture)

        # 후각 인지 검사 준비
        self.ui_test_identification_ready = uiLoader.load(
            "./ui/ui_test_identification_2_ready.ui")
        self.setWindowBySetting(self.ui_test_identification_ready)
        
        # 후각 인지 검사 응답
        self.ui_test_identification_response = uiLoader.load(
            "./ui/ui_test_identification_3_response.ui")
        self.ui_test_identification_response.pb_check_1.clicked.connect(
            self.uiTestIdentificationResponseChoice1)
        self.ui_test_identification_response.pb_check_2.clicked.connect(
            self.uiTestIdentificationResponseChoice2)
        self.ui_test_identification_response.pb_check_3.clicked.connect(
            self.uiTestIdentificationResponseChoice3)
        self.ui_test_identification_response.pb_check_4.clicked.connect(
            self.uiTestIdentificationResponseChoice4)
        self.ui_test_identification_response.ui_menu_btn_quit.clicked.connect(
            self.uiTestIdentificationResponseQuit)
        self.ui_test_identification_response.ui_menu_btn_result.clicked.connect(
            self.uiTestIdentificationResponseResult)
        self.ui_test_identification_response.pb_retry.clicked.connect(
            self.uiTestIdentificationResponseRetry)
        self.ui_test_identification_response.pb_next.clicked.connect(
            self.uiTestIdentificationResponseNext)
        self.ui_test_identification_response.pb_retry.setVisible(False)
        self.ui_test_identification_response.pb_next.setVisible(False)
        self.ui_test_identification_response.label_next.setVisible(True)
        self.setWindowBySetting(self.ui_test_identification_response)

        # 후각 인지 검사 종료
        self.ui_test_identification_completion = uiLoader.load(
            "./ui/ui_test_identification_5_completion.ui")
        self.ui_test_identification_completion.pb_complete.clicked.connect(
            self.uiTestIdentificationCompletionComplete)
        self.setWindowBySetting(self.ui_test_identification_completion)

        # 후각 인지 검사 결과
        self.ui_test_identification_results = uiLoader.load(
            "./ui/ui_test_identification_6_results.ui")
        self.ui_test_identification_results.pushButton_confirm.clicked.connect(
            self.uiTestIdentificationResultsConfirm)
        self.ui_test_identification_results.ui_menu_btn_quit.clicked.connect(
            self.uiTestIdentificationResultsConfirm)
        self.setWindowBySetting(self.ui_test_identification_results)
        self.gradeTestResultsIdentification(0, 0)

        # 후각 인지 검사 시작시 확인
        self.ui_test_identification_start_confirm = uiLoader.load(
            "./ui/ui_start_confirm.ui")
        self.ui_test_identification_start_confirm.pb_start.clicked.connect(
            self.uiTestIdentificationStartConfirmStart)
        self.ui_test_identification_start_confirm.pb_resume.clicked.connect(
            self.uiTestIdentificationStartConfirmResume)
        self.ui_test_identification_start_confirm.pb_close.clicked.connect(
            self.uiTestIdentificationStartConfirmClose)
        self.setWindowBySetting(self.ui_test_identification_start_confirm)
        self.ui_test_identification_start_confirm.setWindowModality(Qt.WindowModality.ApplicationModal)

        # 후각 인지 검사 결과시 확인
        self.ui_test_identification_result_confirm = uiLoader.load(
            "./ui/ui_resume_confirm.ui")
        self.ui_test_identification_result_confirm.pb_resume.clicked.connect(
            self.uiTestIdentificationResultConfirmResume)
        self.ui_test_identification_result_confirm.pb_close.clicked.connect(
            self.uiTestIdentificationResultConfirmClose)
        self.setWindowBySetting(self.ui_test_identification_result_confirm)
        self.ui_test_identification_result_confirm.setWindowModality(Qt.WindowModality.ApplicationModal)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def uiDlgTDIResults(self, uiLoader):
        # 후각 TDI 검사 결과
        self.ui_test_results = uiLoader.load(
            "./ui/ui_test_result.ui")
        self.ui_test_results.pushButton_confirm.clicked.connect(
            self.uiTestResultsConfirm)
        self.ui_test_results.pushButton_save.clicked.connect(
            self.uiTestResultsSave)
        self.ui_test_results.pushButton_review.clicked.connect(
            self.uiTestResultsReview)
        self.ui_test_results.pushButton_file.clicked.connect(
            self.uiTestResultsFile)
        self.setWindowBySetting(self.ui_test_results)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
    def uiDlgTrainST(self, uiLoader):
        # 훈련
        self.ui_train_st_guide_picture = uiLoader.load(
            "./ui/ui_train_st_1_guide_picture.ui")
        self.ui_train_st_guide_picture.ui_train_btn_back.clicked.connect(
            self.uiTrainSTGuidePictureBtnBack)
        self.ui_train_st_guide_picture.ui_train_btn_forward.clicked.connect(
            self.uiTrainSTGuidePictureBtnForward)
        self.ui_train_st_guide_picture.pb_records.clicked.connect(
            self.uiTrainSTGuidePictureRecords)
        self.setWindowBySetting(self.ui_train_st_guide_picture)

        # 훈련 준비
        self.ui_train_st_ready = uiLoader.load(
            "./ui/ui_train_st_2_ready.ui")
        self.setWindowBySetting(self.ui_train_st_ready)

        # 훈련 향 선택
        self.ui_train_st_select = uiLoader.load(
            "./ui/ui_train_st_3_select.ui")
        self.ui_train_st_select.pb_check_1.clicked.connect(
            self.uiTrainSTSelectChoice1)
        self.ui_train_st_select.pb_check_2.clicked.connect(
            self.uiTrainSTSelectChoice2)
        self.ui_train_st_select.pb_check_3.clicked.connect(
            self.uiTrainSTSelectChoice3)
        self.ui_train_st_select.pb_check_4.clicked.connect(
            self.uiTrainSTSelectChoice4)
        self.ui_train_st_select.pb_quit.clicked.connect(
            self.uiTrainSTSelectQuit)
        self.setWindowBySetting(self.ui_train_st_select)

        # 훈련 응답
        self.ui_train_st_response = uiLoader.load(
            "./ui/ui_train_st_4_response.ui")
        self.ui_train_st_response.pb_back.clicked.connect(
            self.uiTrainSTResponseBack)
        self.ui_train_st_response.pb_back.setVisible(False)
        self.ui_train_st_response.pb_next.clicked.connect(
            self.uiTrainSTResponseNext)
        self.ui_train_st_response.pb_next.setVisible(False)
        self.ui_train_st_response.pb_retry.clicked.connect(
            self.uiTrainSTResponseRetry)
        self.ui_train_st_response.pb_retry.setVisible(False)
        self.ui_train_st_response.pb_quit.clicked.connect(
            self.uiTrainSTResponseQuit)
        self.ui_train_st_response.pb_quit.setVisible(False)
        self.ui_train_st_response.label_bg_selfcheck.setVisible(False)
        self.ui_train_st_response.hs_selfcheck.valueChanged.connect(
            self.uiTrainSTResponseSelfCheckChanged)
        self.ui_train_st_response.hs_selfcheck.setVisible(False)
        self.ui_train_st_response.label_selfcheck.installEventFilter(self)
        self.ui_train_st_response.label_selfcheck.setVisible(False)
        self.setWindowBySetting(self.ui_train_st_response)

        # 훈련 종료
        self.ui_train_st_completion = uiLoader.load(
            "./ui/ui_train_st_5_completion.ui")
        self.ui_train_st_completion.pb_complete.clicked.connect(
            self.uiTrainSTCompletionComplete)
        self.setWindowBySetting(self.ui_train_st_completion)

        # 훈련 결과 기록
        self.ui_train_st_results = uiLoader.load(
            "./ui/ui_train_st_6_results.ui")
        self.ui_train_st_results.pushButton_confirm.clicked.connect(
            self.uiTrainSTResultsConfirm)
        self.ui_train_st_results.ui_menu_btn_quit.clicked.connect(
            self.uiTrainSTResultsConfirm)
        self.setWindowBySetting(self.ui_train_st_results)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def uiDlgTrainID(self, uiLoader):
        # 재활
        self.ui_train_id_guide_picture = uiLoader.load(
            "./ui/ui_train_id_1_guide_picture.ui")
        self.ui_train_id_guide_picture.ui_train_btn_back.clicked.connect(
            self.uiTrainIDGuidePictureBtnBack)
        self.ui_train_id_guide_picture.ui_train_btn_forward.clicked.connect(
            self.uiTrainIDGuidePictureBtnForward)
        # self.ui_train_id_guide_picture.pb_records.clicked.connect(
        #     self.uiTrainIDGuidePictureRecords)
        self.setWindowBySetting(self.ui_train_id_guide_picture)

        # 재활 준비
        self.ui_train_id_ready = uiLoader.load(
            "./ui/ui_train_id_2_ready.ui")
        self.setWindowBySetting(self.ui_train_id_ready)

        # 재활 콘텐츠 Scene 선택
        self.ui_train_id_select = uiLoader.load(
            "./ui/ui_train_id_3_select.ui")
        self.ui_train_id_select.pb_scene_01.clicked.connect(
            self.uiTrainIDSelectScene1)
        self.ui_train_id_select.pb_scene_02.clicked.connect(
            self.uiTrainIDSelectScene2)
        self.ui_train_id_select.pb_scene_03.clicked.connect(
            self.uiTrainIDSelectScene3)
        self.ui_train_id_select.pb_scene_04.clicked.connect(
            self.uiTrainIDSelectScene4)
        self.ui_train_id_select.pb_scene_05.clicked.connect(
            self.uiTrainIDSelectScene5)
        self.ui_train_id_select.pb_scene_06.clicked.connect(
            self.uiTrainIDSelectScene6)
        self.ui_train_id_select.pb_scene_07.clicked.connect(
            self.uiTrainIDSelectScene7)
        self.ui_train_id_select.pb_scene_08.clicked.connect(
            self.uiTrainIDSelectScene8)
        self.ui_train_id_select.pb_quit.clicked.connect(
            self.uiTrainIDSelectQuit)
        self.setWindowBySetting(self.ui_train_id_select)

        # 재활 콘텐츠 Scene 구성안 (숫자: 버튼 개수)
        self.ui_train_id_scene_choice_0 = uiLoader.load(
            "./ui/ui_train_id_choice_0.ui")
        self.ui_train_id_scene_choice_0.label_next.setVisible(False)
        self.ui_train_id_scene_choice_0.pg_scent.setVisible(False)
        self.ui_train_id_scene_choice_0.pb_retry.clicked.connect(
            self.uiTrainIDRetry)
        self.ui_train_id_scene_choice_0.pb_retry.setVisible(False)
        self.ui_train_id_scene_choice_0.pb_next.clicked.connect(
            self.uiTrainIDNext)
        self.ui_train_id_scene_choice_0.pb_quit.clicked.connect(
            self.uiTrainIDQuit)
        self.setWindowBySetting(self.ui_train_id_scene_choice_0)

        self.ui_train_id_scene_choice_1 = uiLoader.load(
            "./ui/ui_train_id_choice_1.ui")
        self.ui_train_id_scene_choice_1.label_next.setVisible(False)
        self.ui_train_id_scene_choice_1.pg_scent.setVisible(False)
        self.ui_train_id_scene_choice_1.pb_retry.clicked.connect(
            self.uiTrainIDRetry)
        self.ui_train_id_scene_choice_1.pb_retry.setVisible(False)
        self.ui_train_id_scene_choice_1.pb_next.clicked.connect(
            self.uiTrainIDNext)
        self.ui_train_id_scene_choice_1.pb_quit.clicked.connect(
            self.uiTrainIDQuit)
        self.ui_train_id_scene_choice_1.pb_check_1.clicked.connect(
            self.uiTrainIDChoice1Check1)
        self.setWindowBySetting(self.ui_train_id_scene_choice_1)

        self.ui_train_id_scene_choice_2 = uiLoader.load(
            "./ui/ui_train_id_choice_2.ui")
        self.ui_train_id_scene_choice_2.label_next.setVisible(False)
        self.ui_train_id_scene_choice_2.pg_scent.setVisible(False)
        self.ui_train_id_scene_choice_2.pb_retry.clicked.connect(
            self.uiTrainIDRetry)
        self.ui_train_id_scene_choice_2.pb_retry.setVisible(False)
        self.ui_train_id_scene_choice_2.pb_next.clicked.connect(
            self.uiTrainIDNext)
        self.ui_train_id_scene_choice_2.pb_quit.clicked.connect(
            self.uiTrainIDQuit)
        self.ui_train_id_scene_choice_2.pb_check_1.clicked.connect(
            self.uiTrainIDChoice2Check1)
        self.ui_train_id_scene_choice_2.pb_check_2.clicked.connect(
            self.uiTrainIDChoice2Check2)
        self.setWindowBySetting(self.ui_train_id_scene_choice_2)

        self.ui_train_id_scene_choice_3 = uiLoader.load(
            "./ui/ui_train_id_choice_3.ui")
        self.ui_train_id_scene_choice_3.label_next.setVisible(False)
        self.ui_train_id_scene_choice_3.pg_scent.setVisible(False)
        self.ui_train_id_scene_choice_3.pb_retry.clicked.connect(
            self.uiTrainIDRetry)
        self.ui_train_id_scene_choice_3.pb_retry.setVisible(False)
        self.ui_train_id_scene_choice_3.pb_next.clicked.connect(
            self.uiTrainIDNext)
        self.ui_train_id_scene_choice_3.pb_quit.clicked.connect(
            self.uiTrainIDQuit)
        self.ui_train_id_scene_choice_3.pb_check_1.clicked.connect(
            self.uiTrainIDChoice3Check1)
        self.ui_train_id_scene_choice_3.pb_check_2.clicked.connect(
            self.uiTrainIDChoice3Check2)
        self.ui_train_id_scene_choice_3.pb_check_3.clicked.connect(
            self.uiTrainIDChoice3Check3)
        self.setWindowBySetting(self.ui_train_id_scene_choice_3)

        self.ui_train_id_scene_choice_4 = uiLoader.load(
            "./ui/ui_train_id_choice_4.ui")
        self.ui_train_id_scene_choice_4.label_next.setVisible(False)
        self.ui_train_id_scene_choice_4.pg_scent.setVisible(False)
        self.ui_train_id_scene_choice_4.pb_retry.clicked.connect(
            self.uiTrainIDRetry)
        self.ui_train_id_scene_choice_4.pb_retry.setVisible(False)
        self.ui_train_id_scene_choice_4.pb_next.clicked.connect(
            self.uiTrainIDNext)
        self.ui_train_id_scene_choice_4.pb_quit.clicked.connect(
            self.uiTrainIDQuit)
        self.ui_train_id_scene_choice_4.pb_check_1.clicked.connect(
            self.uiTrainIDChoice4Check1)
        self.ui_train_id_scene_choice_4.pb_check_2.clicked.connect(
            self.uiTrainIDChoice4Check2)
        self.ui_train_id_scene_choice_4.pb_check_3.clicked.connect(
            self.uiTrainIDChoice4Check3)
        self.ui_train_id_scene_choice_4.pb_check_4.clicked.connect(
            self.uiTrainIDChoice4Check4)
        self.setWindowBySetting(self.ui_train_id_scene_choice_4)

    def uiTrainIDSelectScene1(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_1)
        
    def uiTrainIDSelectScene2(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_2)
        
    def uiTrainIDSelectScene3(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_3)
        
    def uiTrainIDSelectScene4(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_4)
        
    def uiTrainIDSelectScene5(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_5)
        
    def uiTrainIDSelectScene6(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_6)
        
    def uiTrainIDSelectScene7(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_7)
        
    def uiTrainIDSelectScene8(self):
        self.startTrainIDScenes(dsTrainID.id_train_scene_8)
    
    def uiTrainIDSelectQuit(self):
        self.uiDlgChange(self.ui_train_id_select, self.ui_menu_dlg)
        # 사운드 (메인)
        dsSound.playGuideSound('intro_menu')
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def uiDlgMessages(self, uiLoader):
        # 메시지 다이얼로그들
        self.ui_test_results_save_dlg = uiLoader.load(
            "./ui/ui_dlg_msg.ui")
        self.ui_test_results_save_dlg.pb_close.clicked.connect(
            self.uiTestResultsSaveDlgClose)
        self.setWindowBySetting(self.ui_test_results_save_dlg)

        # 평가 다이얼로그
        self.ui_test_results_review_dlg = uiLoader.load(
            "./ui/ui_dlg_review.ui")
        self.ui_test_results_review_dlg.pb_close.clicked.connect(
            self.uiTestResultsReviewDlgClose)
        self.ui_test_results_review_dlg.hs_review.valueChanged.connect(
            self.uiTestResultsReviewChanged)
        self.ui_test_results_review_dlg.te_review.installEventFilter(self)
        self.setWindowBySetting(self.ui_test_results_review_dlg)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 설정
    def uiDlgSettings(self, uiLoader):
        self.ui_settings_dlg = uiLoader.load(
            "./ui/ui_settings.ui")
        self.ui_settings_dlg.hs_scent_power.valueChanged.connect(
            self.uiSettingsScentPowerChanged)
        self.ui_settings_dlg.hs_scent_run_time.valueChanged.connect(
            self.uiSettingsScentRunTimeChanged)
        self.ui_settings_dlg.hs_scent_post_delay.valueChanged.connect(
            self.uiSettingsScentPostDelayChanged)
        self.ui_settings_dlg.hs_cleaning_power.valueChanged.connect(
            self.uiSettingsCleaningPowerChanged)
        self.ui_settings_dlg.hs_cleaning_run_time.valueChanged.connect(
            self.uiSettingsCleaningRunTimeChanged)
        self.ui_settings_dlg.hs_cleaning_post_delay.valueChanged.connect(
            self.uiSettingsCleaningPostDelayChanged)
        self.ui_settings_dlg.hs_scent_emit_interval.valueChanged.connect(
            self.uiSettingsScentEmitIntervalChanged)
        self.ui_settings_dlg.hs_thres_test_max_level.valueChanged.connect(
            self.uiSettingsThresTestMaxLevelChanged)
        self.ui_settings_dlg.hs_thres_node_max_num.valueChanged.connect(
            self.uiSettingsThresNodeMaxNumChanged)
        self.ui_settings_dlg.hs_thres_node_score_num.valueChanged.connect(
            self.uiSettingsThresNodeScoreNumChanged)
        self.ui_settings_dlg.cb_voice_onoff.setCurrentIndex(1)
        self.ui_settings_dlg.cb_result_show_onoff.setCurrentIndex(0)
        self.ui_settings_dlg.pushButton_back.clicked.connect(
            self.uiSettingsBackClicked)
        self.ui_settings_dlg.pushButton_update_settings.clicked.connect(
            self.uiSettingUpdateSettings)
        self.setWindowBySetting(self.ui_settings_dlg)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 프로토콜 메시지 통신 확인
    def uiDlgProtocol(self, uiLoader):
        self.ui_data_protocol_dlg = uiLoader.load(
            "./ui/ui_data_protocol.ui")
        self.available_port_list = dsSerial._get_available_ports()
        self.ui_data_protocol_dlg.comboBox_port.insertItems(
            0, [x.portName() for x in self.available_port_list])
        self.ui_data_protocol_dlg.comboBox_baudrate.insertItems(
            0, [str(x) for x in dsSerial.BAUDRATES])
        self.ui_data_protocol_dlg.comboBox_databits.insertItems(
            0, [str(x) for x in dsSerial.DATABITS])
        self.ui_data_protocol_dlg.comboBox_flowcontrol.insertItems(
            0, [str(x) for x in dsSerial.FLOWCONTROL])
        self.ui_data_protocol_dlg.comboBox_parity.insertItems(
            0, [str(x) for x in dsSerial.PARITY])
        self.ui_data_protocol_dlg.comboBox_stopbits.insertItems(
            0, [str(x) for x in dsSerial.STOPBITS])
        self.ui_data_protocol_dlg.pushButton_connect.clicked.connect(
            self.pushButton_connect_clicked)
        self.ui_data_protocol_dlg.pushButton_emit.clicked.connect(
            self.pushButton_emit_clicked)
        self.ui_data_protocol_dlg.pushButton_clean.clicked.connect(
            self.pushButton_clean_clicked)
        self.ui_data_protocol_dlg.pushButton_emit_clean.clicked.connect(
            self.pushButton_emit_clean_clicked)
        self.ui_data_protocol_dlg.pushButton_stop.clicked.connect(
            self.pushButton_stop_clicked)
        self.ui_data_protocol_dlg.pushButton_temperature.clicked.connect(
            self.pushButton_temperature_clicked)
        self.ui_data_protocol_dlg.pushButton_pressure.clicked.connect(
            self.pushButton_pressure_clicked)
        self.ui_data_protocol_dlg.pushButton_temperature_pressure.clicked.connect(
            self.pushButton_temperature_pressure_clicked)
        self.ui_data_protocol_dlg.pushButton_back.clicked.connect(
            self.pushButton_back_clicked)
        self.setWindowBySetting(self.ui_data_protocol_dlg)

        # 시리얼 통신 기본 설정
        self.ui_data_protocol_dlg.comboBox_baudrate.setCurrentIndex(0)
        self.ui_data_protocol_dlg.comboBox_databits.setCurrentIndex(3)
        # 시리얼 통신 수신 연결
        self.available_port_list = dsSerial._get_available_ports()
        # 시리얼 콘솔로 Text edit 설정
        self.setSerialConsole(self.ui_data_protocol_dlg.textEdit_console)
        # 기본 설정으로 시리얼 연결 COM
        if len(self.available_port_list) > 0:
            # self.connect_serial_default(self.available_port_list[0].portName())
            dsSerial._connect_default(self._serial, self._serial_read_thread,
                                      port_name=self.available_port_list[0].portName())
        self.ui_data_protocol_dlg.pushButton_connect.setText(
           {False: dsText.serialText['status_connect'], True: dsText.serialText['status_disconnect']}[dsSerial._is_open(self._serial)])

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 타이머 설정
    def uiDlgTimer(self):
        self.test_timer = QTimer(self)
        self.test_timer.setInterval(1000)
        self.test_timer.timeout.connect(self.testTimerTimeout)
        self.test_timer.start()

    def testTimerTimeout(self):
        if dsTest.test_type == 1: # 역치 검사 
            dsTestTH.th_time_count += 1
        elif dsTest.test_type == 2: # 식별 검사
            dsTestDC.dc_time_count += 1
        elif dsTest.test_type == 3: # 인지 검사
            dsTestID.id_time_count += 1
        # print("%d: 역치:%d, 식별:%d, 인지:%d" % \
        #       (dsTestInfo.test_type, dsTestTH.th_time_count, dsTestDC.dc_time_count, dsTestID.id_time_count))
        self.updateUiTimes()

    def updateUiTimes(self):
        # 역치 검사 UI
        if dsTest.test_type == 1: # 역치 검사 
            self.ui_test_threshold_response.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestTH.th_time_count))
            self.ui_test_threshold_completion.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestTH.th_time_count))
        # 식별 검사 UI
        elif dsTest.test_type == 2: # 식별 검사
            self.ui_test_discrimination_response.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestDC.dc_time_count))
            self.ui_test_discrimination_completion.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestDC.dc_time_count))
        # 인지 검사 UI
        elif dsTest.test_type == 3: # 인지 검사
            self.ui_test_identification_response.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestID.id_time_count))
            self.ui_test_identification_completion.label_time.setText(
                dsUtils.hmsFormFromCounts(dsTestID.id_time_count))

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # DB 설정
    def uiDlgDB(self):
        # dsTrainSTDB.createTable()
        dsTestDB.createTableSubject()
        dsTestDB.createTableTestID()

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 수신 데이터 파싱
    def parseReadData(self, data):
        print("parseReadData: ", data)
        # try:
        #     mid, mfunc, maddress = struct.unpack_from('>BBH', data, offset=0)
        #     self.ui_data_protocol_dlg.textEdit_console.append("ID:%d, FUNC:%d, ADDR:%d" % (mid, mfunc, maddress))
        #     self.ui_data_protocol_dlg.textEdit_console.moveCursor(QtGui.QTextCursor.End)
        #     # print(mid, mfunc, maddress)
        # except Exception as err:
        #     print("Protocol Error: ", err)

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def requestFrequency(self, frequency): # PWM 주파수수
        # print("requestScentNo: ", scent_no)
        sendMsg= dsComm.sendMsgWriteSingleRegister(id=1, 
                            func=6,
                            address=4212,
                            data_command=400)
        self.write_data(sendMsg)

    def requestScentNo(self, scent_no, command): # 발향, 세정 통합 메시지  1: 발향만, 4: 발향/세정정
        # print("requestScentNo: ", scent_no)
        sendMsg= dsComm.sendMsgForEmitClean(id=1, 
                            func=16, 
                            address=4200,
                            qor=8,
                            data_length=16,
                            data_command=command,
                            data_scent_no=scent_no,
                            data_scent_pump_power=dsSetting.dsParam['scent_power'], 
                            data_clean_pump_power=dsSetting.dsParam['cleaning_power'],
                            data_scent_period=dsSetting.dsParam['scent_run_time'],
                            data_clean_period=dsSetting.dsParam['cleaning_run_time'],
                            data_scent_delay=dsSetting.dsParam['scent_post_delay'],
                            data_cleanup_delay=dsSetting.dsParam['cleaning_post_delay'])
        self.write_data(sendMsg)
        
    def requestScentNoAndTime(self, scent_no, command, scent_run_time): # 발향, 세정 통합 메시지
        # print("requestBySettingValues: ", scent_no)
        sendMsg = dsComm.sendMsgForEmitClean(id=1, 
                            func=16, 
                            address=4200,
                            qor=8,
                            data_length=16,
                            data_command=command,
                            data_scent_no=scent_no,
                            data_scent_pump_power=dsSetting.dsParam['scent_power'], 
                            data_clean_pump_power=dsSetting.dsParam['cleaning_power'],
                            data_scent_period=scent_run_time,
                            data_clean_period=dsSetting.dsParam['cleaning_run_time'],
                            data_scent_delay=dsSetting.dsParam['scent_post_delay'],
                            data_cleanup_delay=dsSetting.dsParam['cleaning_post_delay'])      
        self.write_data(sendMsg)  
    
    def requestScentWithValues(self, scent_no, command, \
                        scent_pump_power, clean_pump_power, scent_period, clean_period, scent_delay,cleanup_delay): # 발향, 세정 통합 메시지
        # print("requestScentWithValues: ", scent_no)
        sendMsg = dsComm.sendMsgForEmitClean(id=1, 
                            func=16, 
                            address=4200,
                            qor=8,
                            data_length=16,
                            data_command=command,
                            data_scent_no=scent_no,
                            data_scent_pump_power=scent_pump_power, 
                            data_clean_pump_power=clean_pump_power,
                            data_scent_period=scent_period,
                            data_clean_period=clean_period,
                            data_scent_delay=scent_delay,
                            data_cleanup_delay=cleanup_delay)
        self.write_data(sendMsg)
    
    def progressBarScentAndClean(self, scent_no, progress_bar, label_text):
        # 명령 전달
        self.requestScentNo(scent_no, command=1) # 1:발향만, 4:발향/세정
        # 발향 Progress
        scent_time = int(dsSetting.dsParam['scent_run_time'])
        for i in range(1, 101):
            QtTest.QTest.qWait(scent_time * 9)
            progress_bar.setValue(i)

        # # 세정 Progress
        # label_text.setText(dsText.processText['cleaning'])
        # progress_bar.setStyleSheet(dsUiCustom.pb_red_style)
        # # 사운드
        # dsSound.playGuideSound('cleaning_caution')
        # # for j in range(scent_time_rate+1, 101):
        # #     QtTest.QTest.qWait(all_time * 10)
        # #     progress_bar.setValue(j)
        # cleaning_time = int(dsSetting.dsParam['cleaning_run_time'])
        # for i in range(1, 101):
        #     QtTest.QTest.qWait(cleaning_time * 9)
        #     progress_bar.setValue(i)
        # progress_bar.setStyleSheet(dsUiCustom.pb_blue_style)
        
        # 발향 간격 시간
        QtTest.QTest.qWait(dsSetting.dsParam['scent_emit_interval']*1000)

    def progressBarScentAndCleanForTrainST(self, scent_no, progress_bar, label_text):
        # 명령 전달
        self.requestScentNoAndTime(scent_no, command=4, scent_run_time=15)
        scent_time = 15
        for i in range(1, 101):
            QtTest.QTest.qWait(scent_time * 9)
            progress_bar.setValue(i)

        # 세정 Progress
        label_text.setText(dsText.processText['cleaning'])
        progress_bar.setStyleSheet(dsUiCustom.pb_red_style)
        # 사운드
        dsSound.playGuideSound('cleaning_caution')
        cleaning_time = 5
        for i in range(1, 101):
            QtTest.QTest.qWait(cleaning_time * 9)
            progress_bar.setValue(i)
        progress_bar.setStyleSheet(dsUiCustom.pb_blue_style)
        
        # 발향 간격 시간
        QtTest.QTest.qWait(dsSetting.dsParam['scent_emit_interval']*1000)

    def progressBarScentAndCleanForTrainID(self, scent_no, progress_bar, label_text):
        progress_bar.setVisible(True)
        # 명령 전달
        self.requestScentNo(scent_no, command=4)
        # 발향 Progress
        scent_time = int(dsSetting.dsParam['scent_run_time'])
        for i in range(1, 101):
            QtTest.QTest.qWait(scent_time * 9)
            progress_bar.setValue(i)

        # 세정 Progress
        progress_bar.setStyleSheet(dsUiCustom.pb_red_style)
        # 사운드
        # dsSound.playGuideSound('cleaning_caution')
        cleaning_time = int(dsSetting.dsParam['cleaning_run_time'])
        for i in range(1, 101):
            QtTest.QTest.qWait(cleaning_time * 9)
            progress_bar.setValue(i)
        progress_bar.setStyleSheet(dsUiCustom.pb_blue_style)
        
        # 발향 간격 시간
        QtTest.QTest.qWait(dsSetting.dsParam['scent_emit_interval']*1000)
        progress_bar.setVisible(False)
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # UI Protocol
    def pushButton_connect_clicked(self):
        if dsSerial._is_open(self._serial):
            dsSerial._disconnect(self._serial, self._serial_read_thread)
        else:
            serial_info = {
                "port_name": self.ui_data_protocol_dlg.comboBox_port.currentText(),
                "baudrate": dsSerial.BAUDRATES[self.ui_data_protocol_dlg.comboBox_baudrate.currentIndex()],
                "bytesize": dsSerial.DATABITS[self.ui_data_protocol_dlg.comboBox_databits.currentIndex()],
                "flow_control": dsSerial.FLOWCONTROL[self.ui_data_protocol_dlg.comboBox_flowcontrol.currentIndex()],
                "parity": dsSerial.PARITY[self.ui_data_protocol_dlg.comboBox_parity.currentIndex()],


                
                "stop_bits": dsSerial.STOPBITS[self.ui_data_protocol_dlg.comboBox_stopbits.currentIndex()],
            }
            dsSerial._connect(self._serial, self._serial_read_thread, **serial_info)
        self.ui_data_protocol_dlg.pushButton_connect.setText(
            {False: dsText.serialText['status_connect'], True: dsText.serialText['status_disconnect']}[dsSerial._is_open(self._serial)])

    def pushButton_emit_clicked(self):
        self.requestScentTest(1)
        
    def pushButton_clean_clicked(self):
        self.requestScentTest(2)

    def pushButton_emit_clean_clicked(self):
        self.requestScentTest(4)

    def pushButton_stop_clicked(self):
        sendMsg = dsComm.sendMsgWriteSingleRegister(id=1, 
                            func=6, 
                            address=4200,
                            data_command=3)
        self.write_data(sendMsg)

    def pushButton_temperature_clicked(self):
        sendMsg = dsComm.sendMsgReadRegister(id=1,
                                func=4,
                                address=4043,
                                qor=2)
        self.write_data(sendMsg)
        
    def pushButton_pressure_clicked(self):
        sendMsg = dsComm.sendMsgReadRegister(id=1,
                                func=4,
                                address=4045,
                                qor=1)
        self.write_data(sendMsg)
        
    def pushButton_temperature_pressure_clicked(self):
        self.requestTempPress()

    def pushButton_back_clicked(self):
        self.uiDlgChange(self.ui_data_protocol_dlg, self.ui_menu_dlg)

    def requestScentTest(self, command):
        scent_no = self.ui_data_protocol_dlg.sb_scentnum.value()
        scent_power = int(self.ui_data_protocol_dlg.textEdit_emit_power.toPlainText())
        clean_power = int(self.ui_data_protocol_dlg.textEdit_clean_power.toPlainText())
        scent_period = int(self.ui_data_protocol_dlg.textEdit_emit_period.toPlainText())
        clean_period = int(self.ui_data_protocol_dlg.textEdit_clean_period.toPlainText())
        scent_delay = int(self.ui_data_protocol_dlg.textEdit_scent_delay.toPlainText())
        cleanup_delay = int(self.ui_data_protocol_dlg.textEdit_cleanup_delay.toPlainText())
        self.requestScentWithValues(scent_no,
                             command,
                             scent_power,
                             clean_power,
                             scent_period,
                             clean_period,
                             scent_delay,
                             cleanup_delay)

    def requestTempPress(self):
        sendMsg = dsComm.sendMsgReadRegister(id=1,
                                func=4,
                                address=4043,
                                qor=3)
        self.write_data(sendMsg)
        
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # UI Main Widgets
    def uiMainBtnLogin(self):
        # 이름, 연령, 성별을 확인한다. 파일명 저장할 때 활용한다.
        self.name = "" #self.ui_main_dlg.textEdit_name.toPlainText()
        self.age = "" #self.ui_main_dlg.textEdit_age.toPlainText()
        self.gender = "" #self.ui_main_dlg.cb_gender.currentText()
        print("uiMainBtnLogin: %s, %s세, %s" % (self.name, self.age, self.gender))
        
        # 전체 다이얼로그에 이름, 나이, 성별을 표시한다.
        # self.ui_menu_dlg.label_name.setText(self.name)
        # self.ui_menu_dlg.label_age.setText(self.age)
        # self.ui_menu_dlg.label_gender.setText(self.gender)

        # self.ui_test_threshold_guide_picture.label_name.setText(self.name)
        # self.ui_test_threshold_guide_picture.label_age.setText(self.age)
        # self.ui_test_threshold_guide_picture.label_gender.setText(self.gender)

        # self.ui_test_threshold_ready.label_name.setText(self.name)
        # self.ui_test_threshold_ready.label_age.setText(self.age)
        # self.ui_test_threshold_ready.label_gender.setText(self.gender)

        # self.ui_test_threshold_try_scent.label_name.setText(self.name)
        # self.ui_test_threshold_try_scent.label_age.setText(self.age)
        # self.ui_test_threshold_try_scent.label_gender.setText(self.gender)
        
        # self.ui_test_threshold_response.label_name.setText(self.name)
        # self.ui_test_threshold_response.label_age.setText(self.age)
        # self.ui_test_threshold_response.label_gender.setText(self.gender)
        
        # self.ui_test_threshold_completion.label_name.setText(self.name)
        # self.ui_test_threshold_completion.label_age.setText(self.age)
        # self.ui_test_threshold_completion.label_gender.setText(self.gender)

        # self.ui_test_threshold_results.label_name.setText(self.name)
        # self.ui_test_threshold_results.label_age.setText(self.age)
        # self.ui_test_threshold_results.label_gender.setText(self.gender)
        
        # self.ui_test_discrimination_guide_picture.label_name.setText(self.name)
        # self.ui_test_discrimination_guide_picture.label_age.setText(self.age)
        # self.ui_test_discrimination_guide_picture.label_gender.setText(
        #     self.gender)
        
        # self.ui_test_discrimination_ready.label_name.setText(self.name)
        # self.ui_test_discrimination_ready.label_age.setText(self.age)
        # self.ui_test_discrimination_ready.label_gender.setText(self.gender)
        
        # self.ui_test_discrimination_response.label_name.setText(self.name)
        # self.ui_test_discrimination_response.label_age.setText(self.age)
        # self.ui_test_discrimination_response.label_gender.setText(self.gender)

        # self.ui_test_discrimination_completion.label_name.setText(self.name)
        # self.ui_test_discrimination_completion.label_age.setText(self.age)
        # self.ui_test_discrimination_completion.label_gender.setText(self.gender)

        # self.ui_test_discrimination_results.label_name.setText(self.name)
        # self.ui_test_discrimination_results.label_age.setText(self.age)
        # self.ui_test_discrimination_results.label_gender.setText(self.gender)

        # self.ui_test_identification_guide_picture.label_name.setText(self.name)
        # self.ui_test_identification_guide_picture.label_age.setText(self.age)
        # self.ui_test_identification_guide_picture.label_gender.setText(self.gender)
        
        # self.ui_test_identification_ready.label_name.setText(self.name)
        # self.ui_test_identification_ready.label_age.setText(self.age)
        # self.ui_test_identification_ready.label_gender.setText(self.gender)

        # self.ui_test_identification_response.label_name.setText(self.name)
        # self.ui_test_identification_response.label_age.setText(self.age)
        # self.ui_test_identification_response.label_gender.setText(self.gender)

        # self.ui_test_identification_completion.label_name.setText(self.name)
        
        # self.ui_test_identification_completion.label_age.setText(self.age)
        # self.ui_test_identification_completion.label_gender.setText(self.gender)

        # self.ui_test_identification_results.label_name.setText(self.name)
        # self.ui_test_identification_results.label_age.setText(self.age)
        # self.ui_test_identification_results.label_gender.setText(self.gender)

        # self.ui_test_results.label_name.setText(self.name)
        # self.ui_test_results.label_age.setText(self.age)
        # self.ui_test_results.label_gender.setText(self.gender)

        # self.ui_message_scent_dlg.label_name.setText(self.name)
        # self.ui_message_scent_dlg.label_age.setText(self.age)
        # self.ui_message_scent_dlg.label_gender.setText(self.gender)

        self.uiDlgChange(self.ui_main_dlg, self.ui_menu_dlg)

        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 설정 로드 및 반영한다.
        self.updateSettingsUI()
        # 사용자 변경에 따른 정보 초기화
        # self.initinateUserInfo()
        # 검사 정보 초기화
        # self.initTestThreshold()
        # self.initTestDiscrimination()
        self.initTestIdentification()
        # 훈련 정보 초기화
        # self.initTrainST()
        # PWM Frequency
        self.requestFrequency(400)

    # def uiMainBtnHelp(self):
    #     dsSound.playGuideSound('intro_main')

    # 메인 장치 종료
    def uiMainBtnExit(self):
        # os.system('shutdown -s -t 0') # PC 전원 종료
        QCoreApplication.instance().quit() # 프로그램 종료
        
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # UI Dialog Login
    def uiDlgLoginStart(self):
        pw = self.ui_dlg_login.le_pw.text()
        print(pw)
        if self.checkPW(pw):
            print("TRUE")
        else:
            self.countErrorPW()
            print("FALSE")
        self.clearPWEdit()

    # PW 입력창 클리어
    def clearPWEdit(self):
        self.ui_dlg_login.le_pw.setText("")
        self.ui_dlg_login_resetpw.le_pw_old.setText("")
        self.ui_dlg_login_resetpw.le_pw_new.setText("")
        self.ui_dlg_login_resetpw.le_pw_new_check.setText("")

    # PW 확인한다.
    def checkPW(self, pw):
        self.loadPWFile()
        if pw == dsSetting.dsAP['AP'] and dsSetting.dsAP['APC'] < 5:
            return True
        return False
    
    # PW 오류 회수
    def countErrorPW(self):
        self.loadPWFile()
        pwc = dsSetting.dsAP['APC']
        if pwc < 5:
            pwc += 1
        self.ui_dlg_login.label_msg.setText(dsText.pwText[pwc])
        dsSetting.dsAP['APC'] = pwc
        self.savePWFile()

    # PW 파일을 로드한다.
    def loadPWFile(self):
        if os.path.isfile('dsAP'):
            json_dsAP = open('dsAP').read()
            dsSetting.dsAP = json.loads(json_dsAP)
            try:
                pw = dsSetting.dsAP['AP']
                pwc = dsSetting.dsAP['APC']
            except:
                os.remove('dsAP')

    # PW 파일에 저장한다.
    def savePWFile(self):
        with open('dsAP', 'w', encoding='utf-8') as make_file:
            json.dump(dsSetting.dsAP, make_file, ensure_ascii=False, indent='\t')

    def uiDlgLoginResetPW(self):
        self.clearPWEdit()
        self.uiDlgChange(self.ui_dlg_login, self.ui_dlg_login_resetpw)

    def uiDlgLoginResetPWReset(self):
        self.clearPWEdit()
        self.uiDlgChange(self.ui_dlg_login_resetpw, self.ui_dlg_login)

        

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # UI Menu Widgets
    def uiMenuBtnQuit(self):
        # 새로운 다이얼로그를 보인다.
        self.uiDlgChange(self.ui_menu_dlg, self.ui_main_dlg)
        # 사운드 (메인)
        dsSound.playGuideSound('intro_main')

    def uiMenuBtnTestThreshold(self):
        if dsTestTH.th_test_index > 0:
            self.ui_test_threshold_start_confirm.show()
        else:
            self.uiTestThresholdStart()
            self.uiDlgHide(self.ui_menu_dlg)

    def uiMenuBtnTestDiscrimination(self):
        if dsTestDC.dc_test_index > 0:
            self.ui_test_discrimination_start_confirm.show()
        else:
            self.uiTestDiscriminationStart()
            self.uiDlgHide(self.ui_menu_dlg)

    def uiMenuBtnTestIdentification(self):
        if dsTestID.id_test_index > 0 and dsTestID.id_test_index < len(dsTestID.id_test_data):
            self.ui_test_identification_start_confirm.show()
        else:
            self.uiTestIdentificationStart()
            self.uiDlgHide(self.ui_menu_dlg)

    def uiMenuBtnTestResults(self):
        dsTest.TDI_score = 0 
        dsTestTH.T_score = 0
        dsTestDC.D_score = 0
        dsTestID.I_score = 0
        dsTest.TDI_status = 0
        dsTest.VAS_score = 0
        # 메뉴 -> 결과 (TDI 결과 보여줌)
        # 역치 검사 표 초기화
        self.ui_test_results.resultTableT.clear()
        self.ui_test_results.resultTableT.setRowCount(0)
        self.ui_test_results.resultTableT.setColumnCount(len(dsTestTH.th_results[0]) - 2)  # 회차(-1), 추세 제외
        self.ui_test_results.resultTableT.setHorizontalHeaderLabels(dsTestTH.th_results[0][1:7])  # 회차,추세 제외
        self.ui_test_results.resultTableT.setColumnWidth(0, 40)  # 1번째 열 크기 늘임
        self.ui_test_results.resultTableT.setColumnWidth(1, 60)  # 2번째 열 크기 늘임
        self.ui_test_results.resultTableT.setColumnWidth(2, 60)  # 3번째 열 크기 늘임
        self.ui_test_results.resultTableT.setColumnWidth(3, 60)  # 4번째 열 크기 늘임
        self.ui_test_results.resultTableT.setColumnWidth(4, 60)  # 4번째 열 크기 늘임
        self.ui_test_results.resultTableT.setColumnWidth(5, 70)  # 5번째 열 크기 늘임
        # Width 825 맞추면 됨
        T_count_correct = 0
        T_count_not_correct = 0
        T_tableIndex = 0
        # 차트에 넣을 데이터
        T_chart_x = []
        T_chart_y = []
        # 점수 환산용 데이터
        T_score_data = []
        for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
                in dsTestTH.th_results:
            if T_tableIndex > 0:
                nRow = self.ui_test_results.resultTableT.rowCount()
                self.ui_test_results.resultTableT.setRowCount(nRow + 1)
                self.ui_test_results.resultTableT.setItem(nRow, 0, QTableWidgetItem(str(threshold)))
                self.ui_test_results.resultTableT.setItem(nRow, 1, QTableWidgetItem(str(current_level)))
                self.ui_test_results.resultTableT.setItem(nRow, 2, QTableWidgetItem(str(answer)))
                self.ui_test_results.resultTableT.setItem(nRow, 3, QTableWidgetItem(str(response)))
                self.ui_test_results.resultTableT.setItem(nRow, 4, QTableWidgetItem(dsUtils.isCorrectToOX(is_correct)))
                self.ui_test_results.resultTableT.setItem(nRow, 5, QTableWidgetItem(dsUtils.isCorrectToOX(is_node)))
                self.ui_test_results.resultTableT.item(nRow, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableT.item(nRow, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableT.item(nRow, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableT.item(nRow, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableT.item(nRow, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableT.item(nRow, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_correct == 1:
                    T_count_correct += 1
                elif is_correct == 0:
                    T_count_not_correct += 1
                T_chart_x.append(index)
                # T_chart_y.append(threshold)
                T_chart_y.append(current_level)
                # 점수 환산용 데이터
                if is_node == 1 and node_num > (
                    dsSetting.dsParam['thres_node_max_num'] - dsSetting.dsParam['thres_node_score_num']):
                    T_score_data.append(threshold)
            T_tableIndex += 1
        
        # 차트 (역치 검사는 라인 차트)
        # if T_tableIndex > 1:
        #     self.ui_test_results.widgetChartT.canvas.ax.clear()
        #     self.ui_test_results.widgetChartT.canvas.ax.set_xlabel('회차')
        #     self.ui_test_results.widgetChartT.canvas.ax.set_ylabel('단계')
        #     self.ui_test_results.widgetChartT.canvas.ax.plot(T_chart_x, T_chart_y, marker='*', color='r')
        #     self.ui_test_results.widgetChartT.canvas.draw()
        # self.ui_test_results.widgetChartT.apply_line_chart() # 데이터가 없을 때 테스트로 표시
        # if T_tableIndex > 1:
        self.ui_test_results.widgetChartT.applyLineChart(T_chart_x, T_chart_y)

        # 텍스트 표시
        dsTestTH.T_score = dsUtils.average(T_score_data)
        self.ui_test_results.label_tscore.setText("%d" % dsTestTH.T_score)
        # self.ui_test_results.label_rate.setText("후각 능력: %1.1f 단계" % score)
        self.ui_test_results.label_th_time.setText(dsUtils.hmsFormFromCounts(dsTestTH.th_time_count))

        # 식별 검사 표 초기화
        self.ui_test_results.resultTableD.clear()
        self.ui_test_results.resultTableD.setRowCount(0)
        self.ui_test_results.resultTableD.setColumnCount(len(dsTestDC.dc_results[0]) - 1)  # 문항 제외(-1)
        self.ui_test_results.resultTableD.setHorizontalHeaderLabels(dsTestDC.dc_results[0][1:])  # 문항 제외
        self.ui_test_results.resultTableD.setColumnWidth(0, 60)  # 1번째 열 크기 늘임
        self.ui_test_results.resultTableD.setColumnWidth(1, 60)  # 2번째 열 크기 늘임
        self.ui_test_results.resultTableD.setColumnWidth(2, 60)  # 3번째 열 크기 늘임
        self.ui_test_results.resultTableD.setColumnWidth(3, 60)  # 4번째 열 크기 늘임
        self.ui_test_results.resultTableD.setColumnWidth(4, 50)  # 5번째 열 크기 늘임
        self.ui_test_results.resultTableD.setColumnWidth(5, 60)  # 6번째 열 크기 늘임
        # Width 825 맞추면 됨
        D_count_correct = 0
        D_count_not_correct = 0
        D_tableIndex = 0
        for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct in dsTestDC.dc_results:
            if D_tableIndex > 0:
                nRow = self.ui_test_results.resultTableD.rowCount()
                self.ui_test_results.resultTableD.setRowCount(nRow + 1)
                self.ui_test_results.resultTableD.setItem(nRow, 0, QTableWidgetItem(str(scent_no1)))
                self.ui_test_results.resultTableD.setItem(nRow, 1, QTableWidgetItem(str(scent_no2)))
                self.ui_test_results.resultTableD.setItem(nRow, 2, QTableWidgetItem(str(scent_no3)))
                self.ui_test_results.resultTableD.setItem(nRow, 3, QTableWidgetItem(str(answer)))
                self.ui_test_results.resultTableD.setItem(nRow, 4, QTableWidgetItem(str(response)))
                self.ui_test_results.resultTableD.setItem(nRow, 5, QTableWidgetItem(dsUtils.isCorrectToOX(is_correct)))
                self.ui_test_results.resultTableD.item(nRow, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableD.item(nRow, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableD.item(nRow, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableD.item(nRow, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableD.item(nRow, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableD.item(nRow, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_correct == 1:
                    D_count_correct += 1
                elif is_correct == 0:
                    D_count_not_correct += 1
            D_tableIndex += 1
        # 차트 (식별 검사는 파이 차트)
        # if D_tableIndex > 1:
        #     self.ui_test_results.widgetChartD.canvas.ax.clear()
        #     self.ui_test_results.widgetChartD.canvas.ax.pie([D_count_not_correct, D_count_correct],
        #                                                     labels = ['오답', '정답'],
        #                                                     shadow = True,
        #                                                     startangle = 90,
        #                                                     autopct = '%d%%',
        #                                                     colors = ['red', 'blue'])
        #     self.ui_test_results.widgetChartD.canvas.ax.axis('equal')
        #     self.ui_test_results.widgetChartD.canvas.draw()
        # self.ui_test_results.widgetChartD.apply_pie_chart() # 데이터가 없을 때 테스트로 표시
        # if D_tableIndex > -1:
        self.ui_test_results.widgetChartD.applyPieChart(D_count_not_correct, D_count_correct)

        # 텍스트 표시
        dsTestDC.D_score = D_count_correct
        self.ui_test_results.label_dscore.setText("%d" % dsTestDC.D_score)
        # D_question_cnt = D_count_correct + D_count_not_correct
        # D_correct_pct = (D_count_correct * 100) / D_question_cnt
        self.ui_test_results.label_dc_time.setText(dsUtils.hmsFormFromCounts(dsTestDC.dc_time_count))

        # 인지 검사 표 초기화
        self.ui_test_results.resultTableI.clear()
        self.ui_test_results.resultTableI.setRowCount(0)
        self.ui_test_results.resultTableI.setColumnCount(len(dsTestID.id_results[0]) - 3)  # 문항, 주관식 제외 (-3)
        self.ui_test_results.resultTableI.setHorizontalHeaderLabels(
            [dsTestID.id_results[0][1], dsTestID.id_results[0][2],
             dsTestID.id_results[0][3]])
        self.ui_test_results.resultTableI.setColumnWidth(0, 110)  # 1번째 열 크기 늘임
        self.ui_test_results.resultTableI.setColumnWidth(1, 110)  # 2번째 열 크기 늘임
        self.ui_test_results.resultTableI.setColumnWidth(2, 130)  # 3번째 열 크기 늘임
        I_count_correct = 0
        I_count_not_correct = 0
        I_tableIndex = 0
        for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                in dsTestID.id_results:
            if I_tableIndex > 0:
                nRow = self.ui_test_results.resultTableI.rowCount()
                self.ui_test_results.resultTableI.setRowCount(nRow + 1)
                self.ui_test_results.resultTableI.setItem(nRow, 0, QTableWidgetItem(answer))
                self.ui_test_results.resultTableI.setItem(nRow, 1, QTableWidgetItem(choice_response))
                self.ui_test_results.resultTableI.setItem(nRow, 2,
                                                          QTableWidgetItem(dsUtils.isCorrectToOX(is_choice_correct)))
                self.ui_test_results.resultTableI.item(nRow, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableI.item(nRow, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_results.resultTableI.item(nRow, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_choice_correct == 1:
                    I_count_correct += 1
                elif is_choice_correct == 0:
                    I_count_not_correct += 1
            I_tableIndex += 1
        # 차트 (인지 검사는 파이 차트)
        # if I_tableIndex > 1:
        #     self.ui_test_results.widgetChartI.canvas.ax.clear()
        #     self.ui_test_results.widgetChartI.canvas.ax.pie([I_count_not_correct, I_count_correct],
        #                                                     labels = ['오답', '정답'],
        #                                                     shadow = True, 
        #                                                     startangle = 90,
        #                                                     autopct = '%d%%',
        #                                                     colors = ['red', 'blue'])
        #     self.ui_test_results.widgetChartI.canvas.ax.axis('equal')
        #     self.ui_test_results.widgetChartI.canvas.draw()
        # self.ui_test_results.widgetChartI.applyPieChart(0, 16) # 데이터가 없을 때 테스트로 표시
        #if I_tableIndex > -1:
        self.ui_test_results.widgetChartI.applyPieChart(I_count_not_correct, I_count_correct)

        # 텍스트 표시
        dsTestID.I_score = I_count_correct
        self.ui_test_results.label_iscore.setText("%d" % dsTestID.I_score)
        # question_cnt = count_correct + count_not_correct
        # correct_pct = (count_correct * 100) / question_cnt
        self.ui_test_results.label_id_time.setText(dsUtils.hmsFormFromCounts(dsTestID.id_time_count))

        # TDI 결과창 화면 보이기
        dsTest.TDI_score = dsTestTH.T_score + dsTestDC.D_score + dsTestID.I_score
        self.ui_test_results.label_tdi_score.setText("%d" % dsTest.TDI_score)

        # TDI 결과 이미지 보이기 (후각 정상 / 소실 / 감퇴 결과 이미지)
        if len(dsTestTH.th_results) > 1 or \
                len(dsTestDC.dc_results) > 1 or \
                len(dsTestID.id_results) > 1:
            if dsTest.TDI_score > 21: 
                self.ui_test_results.resultImage.setPixmap(
                    QtGui.QPixmap(dsResultImg['Good']))  # 배경 이미지 삽입
            elif dsTest.TDI_score >= 14.5: 
                self.ui_test_results.resultImage.setPixmap(
                    QtGui.QPixmap(dsResultImg['Warning']))  # 배경 이미지 삽입
            else:
                self.ui_test_results.resultImage.setPixmap(
                    QtGui.QPixmap(dsResultImg['Bad']))  # 배경 이미지 삽입
        else:
                self.ui_test_results.resultImage.setPixmap(
                    QtGui.QPixmap(dsResultImg['None']))  # 배경 이미지 삽입
            
        self.uiDlgChange(self.ui_menu_dlg, self.ui_test_results)
        # 사운드
        dsSound.playGuideSound('test_results')

    def uiMenuBtnSettings(self):
        # 메뉴 -> 설정
        self.updateSettingsUI()
        self.uiDlgChange(self.ui_menu_dlg, self.ui_settings_dlg)

    def uiMenuBtnTest(self):
        # 메뉴 -> 시험
        self.uiDlgChange(self.ui_menu_dlg, self.ui_data_protocol_dlg)

    def uiMenuBtnTrainST(self):
        self.uiTrainSTStart()
        self.uiDlgHide(self.ui_menu_dlg)

    def uiMenuBtnTrainID(self):
        self.uiTrainIDStart()
        self.uiDlgHide(self.ui_menu_dlg)


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 역치 검사
    def initTestThreshold(self):
        # 초기화
        dsTestTH.th_time_count = 0
        dsTestTH.th_test_index = 0
        # self.th_test_sequence = 1
        dsTestTH.th_test_current_level = 1
        dsTestTH.th_is_last_correct = -1
        dsTestTH.th_node_num = 0
        dsTestTH.th_temp_response = 0
        self.checkResponseThreshold(0) # 초기화
        # 역치 검사 데이터 리스트
        self.initTestThresholdResultsList()

    def initTestThresholdResultsList(self):
        dsTestTH.clear()
        dsTestTH.th_results.append(dsTestTH.th_results_title)
        # [['회차', '역치', '향 농도', '정답', '선택', '정답여부', '변곡점여부', '변곡점번호']]

    def uiTestThresholdStart(self):
        # 메뉴 -> 역치 검사 가이드
        self.uiDlgChange(self.ui_menu_dlg, self.ui_test_threshold_guide_picture)
        # 사운드
        dsSound.playGuideSound('intro_threshold')

    def uiTestThresholdResume(self):
        self.uiTestThresholdResponseRetry()

    def uiTestThresholdGuidePictureBtnBack(self):
        # 가이드 -> 메뉴
        self.uiDlgChange(self.ui_test_threshold_guide_picture, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    # def uiTestThresholdBtnPractice(self):
    #     self.uiDlgChange(self.ui_test_threshold_guide_picture, self.ui_test_threshold_practice)
    #     # 사운드
    #     dsSound.playGuideSound('scent_emit_threshold_practice')
    #     dsTest.test_type = 1
    
    def uiTestThresholdBtnTryScent(self):
        self.tryScentThreshold()

    def uiTestThresholdGuidePictureBtnForward(self):
        self.uiDlgHide(self.ui_test_threshold_guide_picture)
        self.startThreshold()

    def startThreshold(self):
        dsTest.test_type = 1  # 검사 타입: 역치 검사
        # 초기화
        dsTestTH.th_time_count = 0
        dsTestTH.th_test_index = 0
        # self.th_test_sequence = 1
        dsTestTH.th_test_current_level = 1
        dsTestTH.th_is_last_correct = -1
        dsTestTH.th_node_num = 0
        # 역치 검사 데이터 리스트
        self.initTestThresholdResultsList()
        self.checkResponseThreshold(0) # 초기화
        self.waitTestThresholdReady()
        self.testThresholdProceed()

    def waitTestThresholdReady(self):
        self.ui_test_threshold_ready.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestTH.th_test_index+1))
        self.uiDlgShow(self.ui_test_threshold_ready)
        # 사운드
        dsSound.playGuideSound('ready_test')
        # 진행바
        for i in range(1, 51):
            QtTest.QTest.qWait(30)
            self.ui_test_threshold_ready.pg_ready.setValue(i*2)
        QtTest.QTest.qWait(100)
        self.uiDlgHide(self.ui_test_threshold_ready)
        self.ui_test_threshold_ready.pg_ready.setValue(0)

    def setResponseUiTestThreshold(self):
        self.unselectResponseThreshold()
        self.ui_test_threshold_response.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestTH.th_test_index+1))
        self.ui_test_threshold_response.pg_scent_1.setVisible(True)
        self.ui_test_threshold_response.pg_scent_1.setValue(0)
        self.ui_test_threshold_response.pg_scent_2.setVisible(True)
        self.ui_test_threshold_response.pg_scent_2.setValue(0)
        self.ui_test_threshold_response.pg_scent_3.setVisible(True)
        self.ui_test_threshold_response.pg_scent_3.setValue(0)
        self.ui_test_threshold_response.label_guide.setText("")
        
        self.ui_test_threshold_response.pb_node_1.setVisible(False)
        self.ui_test_threshold_response.pb_node_2.setVisible(False)
        self.ui_test_threshold_response.pb_node_3.setVisible(False)
        self.ui_test_threshold_response.pb_node_4.setVisible(False)
        self.ui_test_threshold_response.pb_node_5.setVisible(False)
        self.ui_test_threshold_response.pb_node_6.setVisible(False)
        self.ui_test_threshold_response.pb_node_7.setVisible(False)
        if dsTestTH.th_node_num > 0:
            self.ui_test_threshold_response.pb_node_1.setVisible(True)
        if dsTestTH.th_node_num > 1:
            self.ui_test_threshold_response.pb_node_2.setVisible(True)
        if dsTestTH.th_node_num > 2:
            self.ui_test_threshold_response.pb_node_3.setVisible(True)
        if dsTestTH.th_node_num > 3:
            self.ui_test_threshold_response.pb_node_4.setVisible(True)
        if dsTestTH.th_node_num > 4:
            self.ui_test_threshold_response.pb_node_5.setVisible(True)
        if dsTestTH.th_node_num > 5:
            self.ui_test_threshold_response.pb_node_6.setVisible(True)
        if dsTestTH.th_node_num > 6:
            self.ui_test_threshold_response.pb_node_7.setVisible(True)

    def testThresholdProceed(self):
        dsTest.test_type = 1
        self.ui_test_threshold_response.pb_retry.setVisible(False)
        self.ui_test_threshold_response.label_next.setVisible(False)
        self.ui_test_threshold_response.pb_try_scent.setVisible(False)
        self.ui_test_threshold_response.ui_menu_btn_quit.setVisible(False)
        self.setResponseUiTestThreshold()
        self.uiDlgShow(self.ui_test_threshold_response)
        self.sequentialThreshold()
        self.ui_test_threshold_response.pb_retry.setVisible(True)
        self.ui_test_threshold_response.label_next.setVisible(True)
        self.ui_test_threshold_response.pb_try_scent.setVisible(True)
        self.ui_test_threshold_response.ui_menu_btn_quit.setVisible(True)
        # 선택 단계
        self.ui_test_threshold_response.pg_scent_1.setVisible(False)
        self.ui_test_threshold_response.pg_scent_2.setVisible(False)
        self.ui_test_threshold_response.pg_scent_3.setVisible(False)
        # 사운드
        dsSound.playGuideSound('question_threshold')
        self.ui_test_threshold_response.label_guide.setText(dsText.processText['question_threshold'])
        self.selectResponseThreshold() # 선택했으면 버튼이 나타남

    def sequentialThreshold(self):
        # 1번 향기
        self.ui_test_threshold_response.label_guide.setText(dsText.processText['progress_scent_1'])
        # 사운드
        dsSound.playGuideSound('progress_scent_1')
        # 진행바
        if dsTestTH.th_test_data[dsTestTH.th_test_index]['scent_squence'] == 1:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_test_current_level+dsTestTH.th_scent_offset,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_1,
                                          label_text=self.ui_test_threshold_response.label_guide)
        else:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_scent_none,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_1,
                                          label_text=self.ui_test_threshold_response.label_guide)
        # 2번 향기
        self.ui_test_threshold_response.label_guide.setText(dsText.processText['progress_scent_2'])
        # 사운드
        dsSound.playGuideSound('progress_scent_2')
        # 진행바
        if dsTestTH.th_test_data[dsTestTH.th_test_index]['scent_squence'] == 2:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_test_current_level+dsTestTH.th_scent_offset,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_2,
                                          label_text=self.ui_test_threshold_response.label_guide)
        else:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_scent_none,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_2,
                                          label_text=self.ui_test_threshold_response.label_guide)
        # 3번 향기
        self.ui_test_threshold_response.label_guide.setText(dsText.processText['progress_scent_3'])
        # 사운드
        dsSound.playGuideSound('progress_scent_3')
        # 진행바
        if dsTestTH.th_test_data[dsTestTH.th_test_index]['scent_squence'] == 3:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_test_current_level+dsTestTH.th_scent_offset,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_3,
                                          label_text=self.ui_test_threshold_response.label_guide)
        else:
            self.progressBarScentAndClean(scent_no=dsTestTH.th_scent_none,
                                          progress_bar=self.ui_test_threshold_response.pg_scent_3,
                                          label_text=self.ui_test_threshold_response.label_guide)
       
    def tryScentThreshold(self):
        self.ui_test_threshold_try_scent.label_guide.setText(dsText.processText['try_scent_threshold'])
        self.uiDlgShow(self.ui_test_threshold_try_scent)
        # 사운드
        dsSound.playGuideSound('try_scent_threshold')
        # 진행바
        self.progressBarScentAndClean(scent_no=12,
                                    progress_bar=self.ui_test_threshold_try_scent.pg_ready,
                                    label_text=self.ui_test_threshold_try_scent.label_guide)
        self.uiDlgHide(self.ui_test_threshold_try_scent)
        self.ui_test_threshold_try_scent.pg_ready.setValue(0)

    def uiTestThresholdResponseRetry(self):
        self.checkResponseThreshold(0) # 초기화
        self.waitTestThresholdReady()
        self.testThresholdProceed()

    def uiTestThresholdResponseNext(self):
        self.confirmResponseThreshold()
        self.uiTestThresholdProceed()
    
    def uiTestThresholdResponseTryScent(self):
        self.tryScentThreshold()

    # 역치 검사 응답
    def uiTestThresholdResponseChoice1(self):
        if dsTestTH.th_temp_response != 1:
            dsTestTH.th_temp_response = 1
            self.checkResponseThreshold(1)
            self.selectResponseThreshold()
        else:
            dsTestTH.th_temp_response = 0
            self.checkResponseThreshold(0)
            self.unselectResponseThreshold()

    def uiTestThresholdResponseChoice2(self):
        if dsTestTH.th_temp_response != 2:
            dsTestTH.th_temp_response = 2
            self.checkResponseThreshold(2)
            self.selectResponseThreshold()
        else:
            dsTestTH.th_temp_response = 0
            self.checkResponseThreshold(0)
            self.unselectResponseThreshold()

    def uiTestThresholdResponseChoice3(self):
        if dsTestTH.th_temp_response != 3:
            dsTestTH.th_temp_response = 3
            self.checkResponseThreshold(3)
            self.selectResponseThreshold()
        else:
            dsTestTH.th_temp_response = 0
            self.checkResponseThreshold(0)
            self.unselectResponseThreshold()

    def checkResponseThreshold(self, number):
        if number == 1:
            self.ui_test_threshold_response.pb_check_1.setStyleSheet(
                dsBtnImg['check_s'])
            self.ui_test_threshold_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        elif number == 2:
            self.ui_test_threshold_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_2.setStyleSheet(
                dsBtnImg['check_s'])
            self.ui_test_threshold_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        elif number == 3:
            self.ui_test_threshold_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_3.setStyleSheet(
                dsBtnImg['check_s'])
        else:
            self.ui_test_threshold_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_threshold_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])

    def selectResponseThreshold(self):
        if self.ui_test_threshold_response.pg_scent_1.isVisible() == False \
            and self.ui_test_threshold_response.pg_scent_2.isVisible() == False \
            and self.ui_test_threshold_response.pg_scent_3.isVisible() == False \
            and dsTestTH.th_temp_response != 0 :
            # self.ui_test_threshold_response.pb_retry.setVisible(True)
            self.ui_test_threshold_response.pb_next.setVisible(True)
            # self.ui_test_threshold_response.ui_menu_btn_quit.setVisible(True)
    
    def unselectResponseThreshold(self):
        dsTestTH.th_temp_response = 0
        # self.ui_test_threshold_response.pb_retry.setVisible(False)
        self.ui_test_threshold_response.pb_next.setVisible(False)
        # self.ui_test_threshold_response.ui_menu_btn_quit.setVisible(False)

    def confirmResponseThreshold(self):
        self.saveTestDataThreshold(dsTestTH.th_temp_response)
        self.checkResponseThreshold(0) # 초기화
        self.uiDlgHide(self.ui_test_threshold_response)

    def uiTestThresholdProceed(self):
        if dsTestTH.th_test_index < dsTestTH.th_test_total_number and dsTestTH.th_node_num < dsSetting.dsParam['thres_node_max_num']:
            # 다음 검사
            dsTestTH.th_test_index += 1
            self.waitTestThresholdReady()
            self.testThresholdProceed()
        else:
            # 검사 종료
            dsTest.test_type = 0
            self.uiDlgHide(self.ui_test_threshold_response)
            if dsSetting.dsParam['result_show_onoff'] == 1:
                # 결과 화면을 구성한다.
                self.makeTestResultsThreshold()
                self.uiDlgShow(self.ui_test_threshold_results)
                # 사운드
                dsSound.playGuideSound('result_threshold')
            else:
                self.uiDlgShow(self.ui_test_threshold_completion)
                # 사운드
                dsSound.playGuideSound('end_threshold')

    def uiTestThresholdResponseQuit(self):
        dsTest.test_type = 0
        self.uiDlgChange(self.ui_test_threshold_response, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    # 역치검사 회차, 향 농도, 정답, 선택, 정답여부, 증감추이를 저장한다.
    def saveTestDataThreshold(self, num_response):
        # 정답 여부 확인
        if dsTestTH.th_test_data[dsTestTH.th_test_index]['scent_squence'] == num_response:
            is_correct = 1
        else:
            is_correct = 0
        # 변곡점 여부 확인 (지난회 검사와 결과가 다르면 변곡점, 첫회 검사는 변곡점으로 인정 안함)
        if (dsTestTH.th_is_last_correct >= 0) and (is_correct != dsTestTH.th_is_last_correct):  # 최초 시작점(-1) 아니고 결과다르면
            is_node = 1
            dsTestTH.th_node_num += 1
        elif (dsTestTH.th_is_last_correct >= 0) and (
                (dsTestTH.th_test_current_level == dsSetting.dsParam['thres_test_max_level']) or (
                dsTestTH.th_test_current_level == 1)):  # 최고점, 최저점은 변곡점으로 인정
            is_node = 1
            dsTestTH.th_node_num += 1
        else:
            is_node = 0
        # 리스트에 저장
        dsTestTH.th_results.append([dsTestTH.th_test_index,
                                         dsSetting.dsParam['thres_test_max_level'] - dsTestTH.th_test_current_level + 1,  # 역치
                                         dsTestTH.th_test_current_level,  # 향 농도
                                         dsTestTH.th_test_data[dsTestTH.th_test_index]['scent_squence'],
                                         num_response,
                                         is_correct,
                                         is_node,
                                         dsTestTH.th_node_num])
        dsTestTH.th_is_last_correct = is_correct
        print(dsTestTH.th_results)
        # 다음 회차 검사 레벨 조정
        if is_correct == 1:
            # 단계를 1단계 낮춘다.
            if dsTestTH.th_test_current_level > 1:
                dsTestTH.th_test_current_level -= 1
            else:
                dsTestTH.th_test_current_level = 1
        else:
            # 단계를 2단계 높인다.
            if dsTestTH.th_test_current_level < dsSetting.dsParam['thres_test_max_level']:
                dsTestTH.th_test_current_level += 2
            else:
                dsTestTH.th_test_current_level = dsSetting.dsParam['thres_test_max_level']
            # 최대 농도 레벨을 넘지 않도록 함
            if dsTestTH.th_test_current_level > dsSetting.dsParam['thres_test_max_level']:
                dsTestTH.th_test_current_level = dsSetting.dsParam['thres_test_max_level']

    # 검사 결과 화면을 구성한다. (역치검사)
    def makeTestResultsThreshold(self):
        # 표 초기화
        self.ui_test_threshold_results.resultTable.clear()
        self.ui_test_threshold_results.resultTable.setRowCount(0)
        self.ui_test_threshold_results.resultTable.setColumnCount(
            len(dsTestTH.th_results[0]) - 2)  # 회차 제외(-1), 변곡점번호 제외
        self.ui_test_threshold_results.resultTable.setHorizontalHeaderLabels(
            dsTestTH.th_results[0][1:7])  # 회차 제외, 변곡점번호 제외
        self.ui_test_threshold_results.resultTable.setColumnWidth(0, 120)  # 1번째 열 크기 늘임
        self.ui_test_threshold_results.resultTable.setColumnWidth(1, 120)  # 2번째 열 크기 늘임
        self.ui_test_threshold_results.resultTable.setColumnWidth(2, 120)  # 3번째 열 크기 늘임
        self.ui_test_threshold_results.resultTable.setColumnWidth(3, 120)  # 4번째 열 크기 늘임
        self.ui_test_threshold_results.resultTable.setColumnWidth(4, 170)  # 4번째 열 크기 늘임
        self.ui_test_threshold_results.resultTable.setColumnWidth(5, 175)  # 5번째 열 크기 늘임
        # Width 825 맞추면 됨
        count_correct = 0
        count_not_correct = 0
        tableIndex = 0
        # 차트에 넣을 데이터
        chart_x = []
        chart_y = []
        # 점수 환산용 데이터
        score_data = []
        for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
                in dsTestTH.th_results:
            if tableIndex > 0:
                nRow = self.ui_test_threshold_results.resultTable.rowCount()
                self.ui_test_threshold_results.resultTable.setRowCount(nRow + 1)
                # self.ui_test_threshold_results.resultTable.setItem(nRow, 0, QTableWidgetItem(str(index))) # 회차 제외
                self.ui_test_threshold_results.resultTable.setItem(nRow, 0, QTableWidgetItem(str(threshold)))
                self.ui_test_threshold_results.resultTable.setItem(nRow, 1, QTableWidgetItem(str(current_level)))
                self.ui_test_threshold_results.resultTable.setItem(nRow, 2, QTableWidgetItem(str(answer)))
                self.ui_test_threshold_results.resultTable.setItem(nRow, 3, QTableWidgetItem(str(response)))
                self.ui_test_threshold_results.resultTable.setItem(nRow, 4,
                                                                   QTableWidgetItem(dsUtils.isCorrectToOX(is_correct)))
                self.ui_test_threshold_results.resultTable.setItem(nRow, 5,
                                                                   QTableWidgetItem(dsUtils.isCorrectToOX(is_node)))
                self.ui_test_threshold_results.resultTable.item(nRow, 0).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_threshold_results.resultTable.item(nRow, 1).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_threshold_results.resultTable.item(nRow, 2).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_threshold_results.resultTable.item(nRow, 3).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_threshold_results.resultTable.item(nRow, 4).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_threshold_results.resultTable.item(nRow, 5).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_correct == 1:
                    count_correct += 1
                elif is_correct == 0:
                    count_not_correct += 1
                chart_x.append(index)
                # chart_y.append(threshold)
                chart_y.append(current_level)
                # 점수 환산용 데이터
                if is_node == 1 and node_num > (
                        dsSetting.dsParam['thres_node_max_num'] - dsSetting.dsParam['thres_node_score_num']):
                    score_data.append(threshold)
            tableIndex += 1
        # 차트 (역치 검사는 라인 차트)
        if tableIndex > 1:
            # self.ui_test_threshold_results.widgetChart.canvas.ax.clear()
            # self.ui_test_threshold_results.widgetChart.canvas.ax.set_xlabel('회차')
            # self.ui_test_threshold_results.widgetChart.canvas.ax.set_ylabel('단계')
            # self.ui_test_threshold_results.widgetChart.canvas.ax.plot(chart_x, chart_y, marker='*', color='r')
            # self.ui_test_threshold_results.widgetChart.canvas.draw()
            self.ui_test_threshold_results.widgetChart.apply_line_chart(chart_x, chart_y)

        # 텍스트 표시
        score = dsUtils.average(score_data)
        dsTestTH.T_score = score
        self.ui_test_threshold_results.label_result.setText("%1.1f" % score)

    def uiTestThresholdCompletionComplete(self):
        self.saveDataResultsTemp()
        self.saveDataThreshold()
        self.uiDlgChange(self.ui_test_threshold_completion, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestTH.th_test_index = 0 #1
        dsTestTH.th_test_current_level = 1
        dsTestTH.th_is_last_correct = -1
        dsTestTH.th_node_num = 0

    def uiTestThresholdResultsConfirm(self):
        self.saveDataThreshold()
        self.uiDlgChange(self.ui_test_threshold_results, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestTH.th_test_index = 0 #1
        dsTestTH.th_test_current_level = 1
        dsTestTH.th_is_last_correct = -1
        dsTestTH.th_node_num = 0

    def uiTestThresholdStartConfirmStart(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_threshold_start_confirm.hide()
        self.uiTestThresholdStart()
        
    def uiTestThresholdStartConfirmResume(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_threshold_start_confirm.hide()
        self.uiTestThresholdResume()

    def uiTestThresholdStartConfirmClose(self):
        self.ui_test_threshold_start_confirm.hide()

    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 식별 검사
    def initTestDiscrimination(self):
        # 초기화
        dsTestDC.dc_time_count = 0
        dsTestDC.dc_test_index = 0
        # self.dc_test_sequence = 1
        dsTestDC.dc_temp_response = 0
        self.checkResponseDiscrimination(0)
        # 식별 검사 데이터 리스트
        self.initTestDiscriminationResultsList()

    def initTestDiscriminationResultsList(self):
        dsTestDC.dc_results.clear()
        dsTestDC.dc_results.append(dsTestDC.dc_results_title)

    def uiTestDiscriminationStart(self):
        # 메뉴 -> 식별 검사 가이드
        self.uiDlgChange(self.ui_menu_dlg, self.ui_test_discrimination_guide_picture)
        # 사운드
        dsSound.playGuideSound('intro_discrimination')

    def uiTestDiscriminationResume(self):
        self.uiTestDiscriminationResponseRetry()

    def uiTestDiscriminationGuidePictureBtnBack(self):
        # 가이드 -> 메뉴
        self.uiDlgChange(self.ui_test_discrimination_guide_picture, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTestDiscriminationGuidePictureBtnForward(self):
        self.uiDlgHide(self.ui_test_discrimination_guide_picture)
        self.startDiscrimination()

    def startDiscrimination(self):
        dsTest.test_type = 2  # 검사 타입: 식별 검사
        # 초기화
        dsTestDC.dc_time_count = 0
        dsTestDC.dc_test_index = 0
        # self.dc_test_sequence = 1
        # 식별 검사 데이터 리스트
        self.initTestDiscriminationResultsList()
        self.checkResponseDiscrimination(0)
        self.waitTestDiscriminationReady()
        self.testDiscriminationProceed()

    def waitTestDiscriminationReady(self):
        self.ui_test_discrimination_ready.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestDC.dc_test_index+1))
        self.uiDlgShow(self.ui_test_discrimination_ready)
        # 사운드
        dsSound.playGuideSound('ready_test')
        # 진행바
        for i in range(1, 51):
            QtTest.QTest.qWait(30)
            self.ui_test_discrimination_ready.pg_ready.setValue(i*2)
        QtTest.QTest.qWait(100)
        self.uiDlgHide(self.ui_test_discrimination_ready)
        self.ui_test_discrimination_ready.pg_ready.setValue(0)

    def setResponseUiTestDiscrimination(self):
        self.unselectResponseDiscrimination()
        self.ui_test_discrimination_response.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestDC.dc_test_index+1))
        self.ui_test_discrimination_response.pg_scent_1.setVisible(True)
        self.ui_test_discrimination_response.pg_scent_1.setValue(0)
        self.ui_test_discrimination_response.pg_scent_2.setVisible(True)
        self.ui_test_discrimination_response.pg_scent_2.setValue(0)
        self.ui_test_discrimination_response.pg_scent_3.setVisible(True)
        self.ui_test_discrimination_response.pg_scent_3.setValue(0)
        self.ui_test_discrimination_response.label_guide.setText("")

    def testDiscriminationProceed(self):
        dsTest.test_type = 2
        self.ui_test_discrimination_response.pb_retry.setVisible(False)
        self.ui_test_discrimination_response.label_next.setVisible(False)
        self.ui_test_discrimination_response.ui_menu_btn_quit.setVisible(False)
        self.setResponseUiTestDiscrimination()
        self.uiDlgShow(self.ui_test_discrimination_response)
        self.sequentialDiscrimination()
        self.ui_test_discrimination_response.pb_retry.setVisible(True)
        self.ui_test_discrimination_response.label_next.setVisible(True)
        self.ui_test_discrimination_response.ui_menu_btn_quit.setVisible(True)
        # 선택 단계
        self.ui_test_discrimination_response.pg_scent_1.setVisible(False)
        self.ui_test_discrimination_response.pg_scent_2.setVisible(False)
        self.ui_test_discrimination_response.pg_scent_3.setVisible(False)
        # 사운드
        dsSound.playGuideSound('question_discrimination')
        self.ui_test_discrimination_response.label_guide.setText(dsText.processText['question_discrimination'])
        self.selectResponseDiscrimination() # 선택했으면 버튼이 나타남

    def sequentialDiscrimination(self):
        # 1번 향기
        self.ui_test_discrimination_response.label_guide.setText(dsText.processText['progress_scent_1'])
        # 사운드
        dsSound.playGuideSound('progress_scent_1')
        # 진행바
        self.progressBarScentAndClean(scent_no=dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no1'],
                                      progress_bar=self.ui_test_discrimination_response.pg_scent_1,
                                      label_text=self.ui_test_discrimination_response.label_guide)
        # 2번 향기
        self.ui_test_discrimination_response.label_guide.setText(dsText.processText['progress_scent_2'])
        # 사운드
        dsSound.playGuideSound('progress_scent_2')
        # 진행바
        self.progressBarScentAndClean(scent_no=dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no2'],
                                      progress_bar=self.ui_test_discrimination_response.pg_scent_2,
                                      label_text=self.ui_test_discrimination_response.label_guide)
        # 3번 향기
        self.ui_test_discrimination_response.label_guide.setText(dsText.processText['progress_scent_3'])
        # 사운드
        dsSound.playGuideSound('progress_scent_3')
        # 진행바
        self.progressBarScentAndClean(scent_no=dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no3'],
                                      progress_bar=self.ui_test_discrimination_response.pg_scent_3,
                                      label_text=self.ui_test_discrimination_response.label_guide)

    def uiTestDiscriminationResponseRetry(self):
        self.checkResponseDiscrimination(0)
        self.waitTestDiscriminationReady()
        self.testDiscriminationProceed()
    
    def uiTestDiscriminationResponseNext(self):
        self.confirmResponseDiscrimination()
        self.uiTestDiscriminationProceed()

    # 식별 검사 응답
    def uiTestDiscriminationResponseChoice1(self):
        if dsTestDC.dc_temp_response != 1:
            dsTestDC.dc_temp_response = 1
            self.checkResponseDiscrimination(1)
            self.selectResponseDiscrimination()
        else:
            dsTestDC.dc_temp_response = 0
            self.checkResponseDiscrimination(0)
            self.unselectResponseDiscrimination()

    def uiTestDiscriminationResponseChoice2(self):
        if dsTestDC.dc_temp_response != 2:
            dsTestDC.dc_temp_response = 2
            self.checkResponseDiscrimination(2)
            self.selectResponseDiscrimination()
        else:
            dsTestDC.dc_temp_response = 0
            self.checkResponseDiscrimination(0)
            self.unselectResponseDiscrimination()

    def uiTestDiscriminationResponseChoice3(self):
        if dsTestDC.dc_temp_response != 3:
            dsTestDC.dc_temp_response = 3
            self.checkResponseDiscrimination(3)
            self.selectResponseDiscrimination()
        else:
            dsTestDC.dc_temp_response = 0
            self.checkResponseDiscrimination(0)
            self.unselectResponseDiscrimination()

    def checkResponseDiscrimination(self, number):
        if number == 1:
            self.ui_test_discrimination_response.pb_check_1.setStyleSheet(
                dsBtnImg['check_s'])
            self.ui_test_discrimination_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        elif number == 2:
            self.ui_test_discrimination_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_2.setStyleSheet(
                dsBtnImg['check_s'])
            self.ui_test_discrimination_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        elif number == 3:
            self.ui_test_discrimination_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_3.setStyleSheet(
                dsBtnImg['check_s'])
        else:
            self.ui_test_discrimination_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_discrimination_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])

    def selectResponseDiscrimination(self):
        if self.ui_test_discrimination_response.pg_scent_1.isVisible() == False \
            and self.ui_test_discrimination_response.pg_scent_2.isVisible() == False \
            and self.ui_test_discrimination_response.pg_scent_3.isVisible() == False \
            and dsTestDC.dc_temp_response != 0 :
            # self.ui_test_discrimination_response.pb_retry.setVisible(True)
            self.ui_test_discrimination_response.pb_next.setVisible(True)
            # self.ui_test_discrimination_response.ui_menu_btn_quit.setVisible(True)
    
    def unselectResponseDiscrimination(self):
        dsTestDC.dc_temp_response = 0
        # self.ui_test_discrimination_response.pb_retry.setVisible(False)
        self.ui_test_discrimination_response.pb_next.setVisible(False)
        # self.ui_test_discrimination_response.ui_menu_btn_quit.setVisible(False)

    def confirmResponseDiscrimination(self):
        self.saveTestDataDiscrimination(dsTestDC.dc_temp_response)
        self.checkResponseDiscrimination(0) # 초기화
        self.uiDlgHide(self.ui_test_discrimination_response)

    def uiTestDiscriminationProceed(self):
        if (dsTestDC.dc_test_index + 1) < len(dsTestDC.dc_test_data):
            # 다음 검사
            # print("id: %d, data: %d" % (dsTestDC.dc_test_index, len(dsTestDC.dc_test_data)))
            dsTestDC.dc_test_index += 1
            self.waitTestDiscriminationReady()
            self.testDiscriminationProceed()
        else:
            # 검사 종료
            # print("id: %d, data: %d" % (dsTestDC.dc_test_index, len(dsTestDC.dc_test_data)))
            dsTest.test_type = 0
            self.uiDlgHide(self.ui_test_discrimination_response)
            if dsSetting.dsParam['result_show_onoff'] == 1:
                # 검사 결과 화면을 구성한다.
                self.makeTestResultsDiscrimination()
                self.uiDlgShow(self.ui_test_discrimination_results)
                # 사운드
                dsSound.playGuideSound('result_discrimination')
            else:
                self.uiDlgShow(self.ui_test_discrimination_completion)
                # 사운드
                dsSound.playGuideSound('end_discrimination')

    def uiTestDiscriminationResponseQuit(self):
        dsTest.test_type = 0
        self.uiDlgChange(self.ui_test_discrimination_response, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    # 식별검사 문항, 향1번호, 향2번호, 향3번호, 정답, 응답, 정답여부를 저장한다. 
    def saveTestDataDiscrimination(self, num_response):
        """Function"""
        # 정답 여부 확인
        if dsTestDC.dc_test_data[dsTestDC.dc_test_index]['answer'] == num_response:
            is_correct = 1
        else:
            is_correct = 0
        # 리스트에 저장
        dsTestDC.dc_results.append(
            [(dsTestDC.dc_test_index + 1), dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no1'],
             dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no2'], dsTestDC.dc_test_data[dsTestDC.dc_test_index]['scent_no3'],
             dsTestDC.dc_test_data[dsTestDC.dc_test_index]['answer'], num_response, is_correct])
        # print("saveTestDataDiscrimination")
        print(dsTestDC.dc_results)

    # 검사 결과 화면을 구성한다. (식별검사)
    def makeTestResultsDiscrimination(self):
        """Function"""
        # 표 초기화
        self.ui_test_discrimination_results.resultTable.clear()
        self.ui_test_discrimination_results.resultTable.setRowCount(0)
        self.ui_test_discrimination_results.resultTable.setColumnCount(
            len(dsTestDC.dc_results[0]) - 1)  # 문항 제외(-1)
        self.ui_test_discrimination_results.resultTable.setHorizontalHeaderLabels(
            dsTestDC.dc_results[0][1:])  # 문항 제외
        self.ui_test_discrimination_results.resultTable.setColumnWidth(0, 120)  # 1번째 열 크기 늘임
        self.ui_test_discrimination_results.resultTable.setColumnWidth(1, 120)  # 2번째 열 크기 늘임
        self.ui_test_discrimination_results.resultTable.setColumnWidth(2, 120)  # 3번째 열 크기 늘임
        self.ui_test_discrimination_results.resultTable.setColumnWidth(3, 120)  # 4번째 열 크기 늘임
        self.ui_test_discrimination_results.resultTable.setColumnWidth(4, 120)  # 5번째 열 크기 늘임
        self.ui_test_discrimination_results.resultTable.setColumnWidth(5, 225)  # 6번째 열 크기 늘임
        # Width 825 맞추면 됨
        count_correct = 0
        count_not_correct = 0
        tableIndex = 0
        for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct in dsTestDC.dc_results:
            if tableIndex > 0:
                nRow = self.ui_test_discrimination_results.resultTable.rowCount()
                self.ui_test_discrimination_results.resultTable.setRowCount(nRow + 1)
                # self.ui_test_discrimination_results.resultTable.setItem(nRow, 0, QTableWidgetItem(str(index))) # 문항
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 0, QTableWidgetItem(str(scent_no1)))
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 1, QTableWidgetItem(str(scent_no2)))
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 2, QTableWidgetItem(str(scent_no3)))
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 3, QTableWidgetItem(str(answer)))
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 4, QTableWidgetItem(str(response)))
                self.ui_test_discrimination_results.resultTable.setItem(nRow, 5, QTableWidgetItem(
                    dsUtils.isCorrectToOX(is_correct)))
                self.ui_test_discrimination_results.resultTable.item(nRow, 0).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_discrimination_results.resultTable.item(nRow, 1).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_discrimination_results.resultTable.item(nRow, 2).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_discrimination_results.resultTable.item(nRow, 3).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_discrimination_results.resultTable.item(nRow, 4).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_discrimination_results.resultTable.item(nRow, 5).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_correct == 1:
                    count_correct += 1
                elif is_correct == 0:
                    count_not_correct += 1
            tableIndex += 1
        # 차트 (식별 검사는 파이 차트)
        if tableIndex > 1:
            # self.ui_test_discrimination_results.widgetChart.canvas.ax.clear()
            # self.ui_test_discrimination_results.widgetChart.canvas.ax.pie([count_not_correct, count_correct],
            #                                                                labels = ['오답', '정답'],
            #                                                                shadow = True, 
            #                                                                startangle = 90,
            #                                                                autopct = '%d%%',
            #                                                                colors = ['red', 'blue'])
            # self.ui_test_discrimination_results.widgetChart.canvas.ax.axis('equal')
            # self.ui_test_discrimination_results.widgetChart.canvas.draw()
            self.ui_test_discrimination_results.widgetChart.apply_pie_chart(count_not_correct, count_correct)
        # 텍스트 표시
        question_cnt = count_correct + count_not_correct
        if question_cnt > 0:
            correct_pct = (count_correct * 100) / question_cnt
        else:
            correct_pct = 0
            # self.ui_test_discrimination_results.label_rate.setText(
            #     "정답률: %d%% (총 %d문항 중 %d문항)" % (correct_pct, question_cnt, count_correct))
        self.ui_test_discrimination_results.label_correctRate.setText(
            "%1.1f" % correct_pct)
        self.ui_test_discrimination_results.label_totalNumber.setText(
            "%d" % question_cnt)
        self.ui_test_discrimination_results.label_correctNumber.setText(
            "%d" % count_correct)

    def uiTestDiscriminationCompletionComplete(self):
        self.saveDataResultsTemp()
        self.saveDataDiscrimination()
        self.uiDlgChange(self.ui_test_discrimination_completion, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestDC.dc_test_index = 0

    def uiTestDiscriminationResultsConfirm(self):
        self.saveDataDiscrimination()
        self.uiDlgChange(self.ui_test_discrimination_results, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestDC.dc_test_index = 0
        
    def uiTestDiscriminationStartConfirmStart(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_discrimination_start_confirm.hide()
        self.uiTestDiscriminationStart()
        
    def uiTestDiscriminationStartConfirmResume(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_discrimination_start_confirm.hide()
        self.uiTestDiscriminationResume()
        
    def uiTestDiscriminationStartConfirmClose(self):
        self.ui_test_discrimination_start_confirm.hide()

    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 인지 검사
    def initTestIdentification(self):
        # 초기화
        dsTestID.id_time_count = 0
        dsTestID.id_test_index = 0
        self.checkResponseIdentification(0)
        # 인지 검사 데이터 리스트
        self.initTestIdentificationResultsList()

    def initTestIdentificationResultsList(self):
        dsTestID.id_results.clear()
        dsTestID.id_results.append(dsTestID.id_results_title)
        # dsTestID.test_data_identification = [['Question', 'Correct answer', 'Your selection', 'O/X', '응답(주관식)', '정답여부(주관식)']]
        # dsTestID.id_results = [['문항', '정답', '선택', '정답여부', '응답(주관식)', '정답여부(주관식)']]

    def uiTestIdentificationStart(self):
        # 메뉴 -> 인지 검사 가이드
        self.uiDlgChange(self.ui_menu_dlg, self.ui_test_identification_guide_picture)
        # 사운드
        dsSound.playGuideSound('intro_identification')

    def uiTestIdentificationResume(self):
        self.uiTestIdentificationResponseRetry()

    def uiTestIdentificationGuidePictureBtnBack(self):
        # 가이드 -> 메뉴
        self.uiDlgChange(self.ui_test_identification_guide_picture, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTestIdentificationGuidePictureBtnForward(self):
        self.uiDlgHide(self.ui_test_identification_guide_picture)
        self.startIdentification()
        
    def startIdentification(self):
        # 가이드 -> 인지 검사
        dsTest.test_type = 3  # 검사 타입: 인지 검사
        # 초기화
        dsTestID.id_time_count = 0
        dsTestID.id_test_index = 0
        # 인지 검사 데이터 리스트
        self.initTestIdentificationResultsList()
        self.checkResponseIdentification(0)
        self.waitTestIdentificationReady()
        self.testIdentificationProceed()

    def waitTestIdentificationReady(self):
        self.ui_test_identification_ready.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestID.id_test_index+1))
        self.uiDlgShow(self.ui_test_identification_ready)
        # 사운드
        dsSound.playGuideSound('ready_test')
        # 진행바
        for i in range(1, 51):
            QtTest.QTest.qWait(30)
            self.ui_test_identification_ready.pg_ready.setValue(i*2)
        QtTest.QTest.qWait(100)
        self.uiDlgHide(self.ui_test_identification_ready)
        self.ui_test_identification_ready.pg_ready.setValue(0)

    def setResponseUiTestIdentification(self):
        self.unselectResponseIdentification()
        self.ui_test_identification_response.label_seq.setText(
            dsText.processText['question_number'] + " %d." % (dsTestID.id_test_index+1))
        self.ui_test_identification_response.pg_scent.setVisible(True)
        self.ui_test_identification_response.pg_scent.setValue(0)
        self.ui_test_identification_response.label_guide.setText(dsText.processText['progress_scent'])
        # 선택지 이미지 반영
        self.ui_test_identification_response.label_select_1.setText(
            dsTestID.id_test_data[dsTestID.id_test_index]['choice1'])
        self.ui_test_identification_response.pb_select_1.setStyleSheet(
            dsBtnImg[dsTestID.id_test_data[dsTestID.id_test_index]['choice1']])
        self.ui_test_identification_response.label_select_2.setText(
            dsTestID.id_test_data[dsTestID.id_test_index]['choice2'])
        self.ui_test_identification_response.pb_select_2.setStyleSheet(
            dsBtnImg[dsTestID.id_test_data[dsTestID.id_test_index]['choice2']])
        self.ui_test_identification_response.label_select_3.setText(
            dsTestID.id_test_data[dsTestID.id_test_index]['choice3'])
        self.ui_test_identification_response.pb_select_3.setStyleSheet(
            dsBtnImg[dsTestID.id_test_data[dsTestID.id_test_index]['choice3']])
        self.ui_test_identification_response.label_select_4.setText(
            dsTestID.id_test_data[dsTestID.id_test_index]['choice4'])
        self.ui_test_identification_response.pb_select_4.setStyleSheet(
            dsBtnImg[dsTestID.id_test_data[dsTestID.id_test_index]['choice4']])

    def testIdentificationProceed(self):
        dsTest.test_type = 3
        self.ui_test_identification_response.pb_retry.setVisible(False)
        self.ui_test_identification_response.label_next.setVisible(False)
        self.ui_test_identification_response.ui_menu_btn_quit.setVisible(False)
        self.ui_test_identification_response.ui_menu_btn_result.setVisible(False)
        self.setResponseUiTestIdentification()
        self.uiDlgShow(self.ui_test_identification_response)
        self.sequentialIdentification()
        self.ui_test_identification_response.pb_retry.setVisible(True)
        self.ui_test_identification_response.label_next.setVisible(True)
        self.ui_test_identification_response.ui_menu_btn_quit.setVisible(True)
        self.ui_test_identification_response.ui_menu_btn_result.setVisible(True)
        # 선택 단계
        self.ui_test_identification_response.pg_scent.setVisible(False)
        # 사운드
        dsSound.playGuideSound('question_identification')
        self.ui_test_identification_response.label_guide.setText(dsText.processText['question_identification'])
        self.selectResponseIdentification() # 선택했으면 버튼이 나타남

    def sequentialIdentification(self):
        # 사운드
        dsSound.playGuideSound('progress_scent')
        # 진행바
        self.progressBarScentAndClean(scent_no=dsTestID.id_test_data[dsTestID.id_test_index]['scent_no'],
                                      progress_bar=self.ui_test_identification_response.pg_scent,
                                      label_text=self.ui_test_identification_response.label_guide)
        
    def uiTestIdentificationResponseRetry(self):
        self.checkResponseIdentification(0)
        self.waitTestIdentificationReady()
        self.testIdentificationProceed()

    def uiTestIdentificationResponseNext(self):
        self.confirmResponseIdentification()
        self.uiTestIdentificationProceed()

    # 인지 검사 응답
    def uiTestIdentificationResponseChoice1(self):
        if dsTestID.id_temp_response != dsTestID.id_test_data[dsTestID.id_test_index]['choice1']:
            dsTestID.id_temp_response = dsTestID.id_test_data[dsTestID.id_test_index]['choice1']
            self.checkResponseIdentification(1)
            self.selectResponseIdentification()
        else:
            dsTestID.id_temp_response = ""
            self.checkResponseIdentification(0)
            self.unselectResponseIdentification()

    def uiTestIdentificationResponseChoice2(self):
        if dsTestID.id_temp_response != dsTestID.id_test_data[dsTestID.id_test_index]['choice2']:
            dsTestID.id_temp_response = dsTestID.id_test_data[dsTestID.id_test_index]['choice2']
            self.checkResponseIdentification(2)
            self.selectResponseIdentification()
        else:
            dsTestID.id_temp_response = ""
            self.checkResponseIdentification(0)
            self.unselectResponseIdentification()

    def uiTestIdentificationResponseChoice3(self):
        if dsTestID.id_temp_response != dsTestID.id_test_data[dsTestID.id_test_index]['choice3']:
            dsTestID.id_temp_response = dsTestID.id_test_data[dsTestID.id_test_index]['choice3']
            self.checkResponseIdentification(3)
            self.selectResponseIdentification()
        else:
            dsTestID.id_temp_response = ""
            self.checkResponseIdentification(0)
            self.unselectResponseIdentification()

    def uiTestIdentificationResponseChoice4(self):
        if dsTestID.id_temp_response != dsTestID.id_test_data[dsTestID.id_test_index]['choice4']:
            dsTestID.id_temp_response = dsTestID.id_test_data[dsTestID.id_test_index]['choice4']
            self.checkResponseIdentification(4)
            self.selectResponseIdentification()
        else:
            dsTestID.id_temp_response = ""
            self.checkResponseIdentification(0)
            self.unselectResponseIdentification()

    def checkResponseIdentification(self, number):
        if number == 1:
            self.ui_test_identification_response.pb_check_1.setStyleSheet(
                dsBtnImg['check'])
            self.ui_test_identification_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_4.setStyleSheet(
                dsBtnImg['null'])
        elif number == 2:
            self.ui_test_identification_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_2.setStyleSheet(
                dsBtnImg['check'])
            self.ui_test_identification_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_4.setStyleSheet(
                dsBtnImg['null'])
        elif number == 3:
            self.ui_test_identification_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_3.setStyleSheet(
                dsBtnImg['check'])
            self.ui_test_identification_response.pb_check_4.setStyleSheet(
                dsBtnImg['null'])
        elif number == 4:
            self.ui_test_identification_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_4.setStyleSheet(
                dsBtnImg['check'])
        else: 
            self.ui_test_identification_response.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
            self.ui_test_identification_response.pb_check_4.setStyleSheet(
                dsBtnImg['null'])

    def selectResponseIdentification(self):
        if self.ui_test_identification_response.pg_scent.isVisible() == False \
            and dsTestID.id_temp_response != "" :
            # self.ui_test_identification_response.pb_retry.setVisible(True)
            self.ui_test_identification_response.pb_next.setVisible(True)
            # self.ui_test_identification_response.ui_menu_btn_quit.setVisible(True)
            # self.ui_test_identification_response.ui_menu_btn_result.setVIsible(True)
    
    def unselectResponseIdentification(self):
        dsTestID.id_temp_response = ""
        # self.ui_test_identification_response.pb_retry.setVisible(False)
        self.ui_test_identification_response.pb_next.setVisible(False)
        # self.ui_test_identification_response.ui_menu_btn_quit.setVisible(False)
        # self.ui_test_identification_response.ui_menu_btn_result.setVIsible(False)

    def confirmResponseIdentification(self):
        self.saveTestDataIdentification("주관식X", dsTestID.id_temp_response)
        self.checkResponseIdentification(0) # 초기화
        self.uiDlgHide(self.ui_test_identification_response)

    def uiTestIdentificationResponseQuit(self):
        dsTest.test_type = 0
        self.uiDlgChange(self.ui_test_identification_response, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTestIdentificationResponseResult(self):
        # 검사 결과 화면을 구성한다.
        self.makeTestResultsIdentification()
        self.uiDlgChange(self.ui_test_identification_response, self.ui_test_identification_results)
        # 사운드
        dsSound.playGuideSound('result_identification')

    # 인지검사 인덱스, 정답, 응답(주관식), 정답여부(주관식), 응답, 정답여부을 리스트에 추가한다.
    def saveTestDataIdentification(self, str_response, choice_response):
        if dsTestID.id_test_data[dsTestID.id_test_index]['answer'] == str_response:
            is_str_correct = 1
        else:
            is_str_correct = 0
        if dsTestID.id_test_data[dsTestID.id_test_index]['answer'] == choice_response:
            is_choice_correct = 1
        else:
            is_choice_correct = 0
        dsTestID.id_results.append([(dsTestID.id_test_index + 1),
                                              dsTestID.id_test_data[dsTestID.id_test_index]['answer'],
                                              choice_response,
                                              is_choice_correct,
                                              str_response,
                                              is_str_correct, ])
        print(dsTestID.id_results)

    def uiTestIdentificationProceed(self):
        # print("uiTestIdentificationProceed")
        if (dsTestID.id_test_index + 1) < len(dsTestID.id_test_data):
            # 다음 검사
            # print("id: %d, data: %d" % (dsTestID.id_test_index, len(dsTestID.id_test_data)))
            dsTestID.id_test_index += 1
            self.waitTestIdentificationReady()
            self.testIdentificationProceed()
        else:
            # 검사 종료
            # print("id: %d, data: %d" % (dsTestID.id_test_index, len(dsTestID.id_test_data)))
            dsTestID.id_test_index += 1
            dsTest.test_type = 0
            self.uiDlgHide(self.ui_test_identification_response)
            if dsSetting.dsParam['result_show_onoff'] == 1:
                # 검사 결과 화면을 구성한다.
                self.makeTestResultsIdentification()
                self.uiDlgShow(self.ui_test_identification_results)
                # 사운드
                dsSound.playGuideSound('result_identification')
            else:
                self.uiDlgShow(self.ui_test_identification_completion)
                # 사운드
                dsSound.playGuideSound('end_identification')

    # 검사 결과 화면을 구성한다. (인지검사)
    def makeTestResultsIdentification(self):
        # 표 초기화
        self.ui_test_identification_results.resultTable.verticalHeader().setVisible(False) # 번호
        self.ui_test_identification_results.resultTable.clear()
        self.ui_test_identification_results.resultTable.setRowCount(0)
        self.ui_test_identification_results.resultTable.setColumnCount(
            len(dsTestID.id_results[0]) - 3)  # 문항, 주관식 제외(-3)
        self.ui_test_identification_results.resultTable.setHorizontalHeaderLabels(
            [dsTestID.id_results[0][1], dsTestID.id_results[0][2],
             dsTestID.id_results[0][3]])
        self.ui_test_identification_results.resultTable.setColumnWidth(0, 300)  # 1번째 열 크기 늘임
        self.ui_test_identification_results.resultTable.setColumnWidth(1, 300)  # 2번째 열 크기 늘임
        self.ui_test_identification_results.resultTable.setColumnWidth(2, 210)  # 3번째 열 크기 늘임
        # Width 825 맞추면 됨
        count_correct = 0
        count_not_correct = 0
        tableIndex = 0
        for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                in dsTestID.id_results:
            if tableIndex > 0:
                nRow = self.ui_test_identification_results.resultTable.rowCount()
                self.ui_test_identification_results.resultTable.setRowCount(nRow + 1)
                self.ui_test_identification_results.resultTable.setItem(nRow, 0, QTableWidgetItem(answer))
                self.ui_test_identification_results.resultTable.setItem(nRow, 1, QTableWidgetItem(choice_response))
                self.ui_test_identification_results.resultTable.setItem(nRow, 2, QTableWidgetItem(
                    dsUtils.isCorrectToOX(is_choice_correct)))
                self.ui_test_identification_results.resultTable.item(nRow, 0).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_identification_results.resultTable.item(nRow, 1).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_test_identification_results.resultTable.item(nRow, 2).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                # 차트에 넣을 데이터 
                if is_choice_correct == 1:
                    count_correct += 1
                elif is_choice_correct == 0:
                    count_not_correct += 1
            tableIndex += 1

        # 차트 (인지 검사는 파이 차트)
        if tableIndex > 1:
            self.ui_test_identification_results.widgetChart.apply_pie_chart(count_not_correct, count_correct)
        
        # 텍스트 표시
        question_cnt = count_correct + count_not_correct
        if question_cnt > 0:
            correct_pct = (count_correct * 100) / question_cnt
        else:
            correct_pct = 0
            # self.ui_test_identification_results.label_rate.setText(
            #     "정답률: %d%% (총 %d문항 중 %d문항)" % (correct_pct, question_cnt, count_correct))
        self.ui_test_identification_results.label_correctRate.setText(
            "%d" % correct_pct)
            # "%1.1f" % correct_pct)
        self.gradeTestResultsIdentification(correct_pct, question_cnt) # 하이라이트

        self.ui_test_identification_results.label_totalNumber.setText(
            "%d" % question_cnt)
        self.ui_test_identification_results.label_correctNumber.setText(
            "%d" % count_correct)

    def gradeTestResultsIdentification(self, accuracy_rate, question_cnt):
        self.ui_test_identification_results.pb_id_grade_cur_1.setVisible(False)
        self.ui_test_identification_results.pb_id_grade_cur_2.setVisible(False)
        self.ui_test_identification_results.pb_id_grade_cur_3.setVisible(False)
        self.ui_test_identification_results.pb_id_grade_cur_4.setVisible(False)
        self.ui_test_identification_results.pb_id_grade_cur_5.setVisible(False)
        
        if question_cnt > 0:
            if accuracy_rate > 80:
                self.ui_test_identification_results.pb_id_grade_cur_5.setVisible(True)
            elif accuracy_rate > 60:
                self.ui_test_identification_results.pb_id_grade_cur_4.setVisible(True)
            elif accuracy_rate > 40:
                self.ui_test_identification_results.pb_id_grade_cur_3.setVisible(True)
            elif accuracy_rate > 20:
                self.ui_test_identification_results.pb_id_grade_cur_2.setVisible(True)
            else:
                self.ui_test_identification_results.pb_id_grade_cur_1.setVisible(True)

    def uiTestIdentificationCompletionComplete(self):
        # 인지 검사 결과를 파일에 저장한다.
        self.saveDataResultsTemp()
        self.saveDataIdentification()
        self.uiDlgChange(self.ui_test_identification_completion, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestID.id_test_index = 0

    def closeTestIdentificationResults(self):
        # 인지 검사 결과를 파일에 저장한다.
        self.saveDataIdentification()
        self.uiDlgChange(self.ui_test_identification_results, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')
        # 초기화
        dsTest.test_type = 0
        dsTestID.id_test_index = 0

    def uiTestIdentificationResultsConfirm(self):
        if dsTestID.id_test_index > 0 and dsTestID.id_test_index < len(dsTestID.id_test_data):
            self.ui_test_identification_result_confirm.show()
        else:
            self.closeTestIdentificationResults()

    def uiTestIdentificationStartConfirmStart(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_identification_start_confirm.hide()
        self.uiTestIdentificationStart()
        
    def uiTestIdentificationStartConfirmResume(self):
        self.uiDlgHide(self.ui_menu_dlg)
        self.ui_test_identification_start_confirm.hide()
        self.uiTestIdentificationResume()
        
    def uiTestIdentificationStartConfirmClose(self):
        self.ui_test_identification_start_confirm.hide()
        
    def uiTestIdentificationResultConfirmResume(self):
        self.ui_test_identification_result_confirm.hide()
        self.uiDlgHide(self.ui_test_identification_results)
        self.uiTestIdentificationResume()
        
    def uiTestIdentificationResultConfirmClose(self):
        self.ui_test_identification_result_confirm.hide()
        self.closeTestIdentificationResults()

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # TDI Score
    def setThresholdScore(self):
        dsTestTH.T_score = 0
        T_tableIndex = 0
        # 점수 환산용 데이터
        T_score_data = []
        for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
            in dsTestTH.th_results:
            if T_tableIndex > 0:
                if is_node == 1 and node_num > (
                    dsSetting.dsParam['thres_node_max_num'] - dsSetting.dsParam['thres_node_score_num']):
                    T_score_data.append(threshold)
            T_tableIndex += 1
        dsTestTH.T_score = dsUtils.average(T_score_data)

    def setDiscriminationScore(self):
        dsTestDC.D_score = 0
        D_count_correct = 0
        D_count_not_correct = 0
        D_tableIndex = 0
        for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct in dsTestDC.dc_results:
            if D_tableIndex > 0:
                if is_correct == 1:
                    D_count_correct += 1
                elif is_correct == 0:
                    D_count_not_correct += 1
            D_tableIndex += 1
        dsTestDC.D_score = D_count_correct

    def setIdentificationScore(self):
        dsTestID.I_score = 0
        I_count_correct = 0
        I_count_not_correct = 0
        I_tableIndex = 0
        for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                in dsTestID.id_results:
            if I_tableIndex > 0:
                if is_choice_correct == 1:
                    I_count_correct += 1
                elif is_choice_correct == 0:
                    I_count_not_correct += 1
            I_tableIndex += 1
        dsTestID.I_score = I_count_correct

    def setTestsScores(self):
        dsTest.TDI_score = 0
        self.setThresholdScore()
        self.setDiscriminationScore()
        self.setIdentificationScore()
        dsTest.TDI_score = dsTestTH.T_score + dsTestDC.D_score + dsTestID.I_score

    # TDI Results
    def uiTestResultsConfirm(self):
        self.uiDlgChange(self.ui_test_results, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTestResultsSave(self):
        if len(dsTestTH.th_results) > 1 or \
                len(dsTestDC.dc_results) > 1 or \
                len(dsTestID.id_results) > 1:
            # 통합 데이터 파일 저장
            self.saveDataResults()
            self.ui_test_results_save_dlg.label_msg.setText(
                dsText.resultText['results_save'])
        else:
            self.ui_test_results_save_dlg.label_msg.setText(
                dsText.resultText['results_save_none'])
        self.uiDlgShow(self.ui_test_results_save_dlg)

    def uiTestResultsReview(self):
        self.uiDlgShow(self.ui_test_results_review_dlg)

    def uiTestResultsFile(self):
        # data 폴더 윈도우 탐색기 열기
        os.startfile(dsText.resultText['.\\' + 'results_data_path'])

    # TDI Results Save, Review
    def uiTestResultsSaveDlgClose(self):
        self.uiDlgHide(self.ui_test_results_save_dlg)

    def uiTestResultsReviewDlgClose(self):
        self.uiDlgHide(self.ui_test_results_review_dlg)

    def uiTestResultsReviewChanged(self):
        self.ui_test_results_review_dlg.label_vas.setText(
            str(self.ui_test_results_review_dlg.hs_review.value()/10))

    def initinateUserInfo(self):
        self.ui_test_results_review_dlg.hs_review.setValue(100)
        self.ui_test_results_review_dlg.te_review.setText("")
    

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 재활
    def uiTrainIDStart(self):
        # 메뉴 -> 자가 훈련 가이드
        self.uiDlgChange(self.ui_menu_dlg, self.ui_train_id_guide_picture)
        # 사운드
        dsSound.playGuideSound('intro_train_id')

    def uiTrainIDGuidePictureBtnBack(self):
        # 가이드 -> 메뉴
        self.uiDlgChange(self.ui_train_id_guide_picture, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTrainIDGuidePictureBtnForward(self):
        self.uiDlgHide(self.ui_train_id_guide_picture)
        self.startTrainIDSelect()
    
    # def uiTrainIDGuidePictureRecords(self):
    #     self.makeTrainIDResults()
    #     self.uiDlgChange(self.ui_train_id_guide_picture, self.ui_train_id_results)
    #     # 사운드
    #     dsSound.playGuideSound('records_train_id')

    def startTrainIDSelect(self):
        self.uiDlgShow(self.ui_train_id_select)
        # 사운드
        dsSound.playGuideSound('select_train_id')

    def initTrainIDScenes(self, scene_list):
        dsTrainID.id_train_index = 0
        dsTrainID.id_train_scene_list = scene_list
        dsTrainID.id_train_size = len(dsTrainID.id_train_scene_list)
        print("RH Scene Size:", dsTrainID.id_train_size)

    def quitTrainIDScenes(self):
        dsTrainID.id_train_index = 0
        dsTrainID.id_train_size = 0
        dsTrainID.id_train_scene_list = []
        self.uiDlgHide(self.prev_rhs_screen)

    def startTrainIDScenes(self, scene_list):
        self.initTrainIDScenes(scene_list)
        self.continueTrainIDScenes()

    def continueTrainIDScenes(self):
        self.clearUiTrainIDChoiceChecks()
        if dsTrainID.id_train_index < dsTrainID.id_train_size and dsTrainID.id_train_size > 0:
            # 화면 구성
            self.makeTrainIDScreen(dsTrainID.id_train_scene_list[dsTrainID.id_train_index])
            # 인터페이스 구성
            self.showTrainIDScene()
            # 사운드 구성
            dsSound.playTrainIDSound(dsTrainID.id_train_scene_list[dsTrainID.id_train_index]['sound'])
            # 발향 구성
            self.emitTrainIDSceneScent(dsTrainID.id_train_scene_list[dsTrainID.id_train_index])
        else:
            print("Quit")
            self.quitTrainIDScenes()

    def makeTrainIDScreen(self, scene):
        # 레이아웃
        if scene['layout_type'] == 'choice_0':
            self.train_id_screen = self.ui_train_id_scene_choice_0
            self.makeTrainIDScreenChoice(self.train_id_screen, scene, 0)
        elif scene['layout_type'] == 'choice_1':
            self.train_id_screen = self.ui_train_id_scene_choice_1
            self.makeTrainIDScreenChoice(self.train_id_screen, scene, 1)
        elif scene['layout_type'] == 'choice_2': 
            self.train_id_screen = self.ui_train_id_scene_choice_2
            self.makeTrainIDScreenChoice(self.train_id_screen, scene, 2)
        elif scene['layout_type'] == 'choice_3':
            self.train_id_screen = self.ui_train_id_scene_choice_3
            self.makeTrainIDScreenChoice(self.train_id_screen, scene, 3)
        elif scene['layout_type'] == 'choice_4':
            self.train_id_screen = self.ui_train_id_scene_choice_4
            self.makeTrainIDScreenChoice(self.train_id_screen, scene, 4)
        
        # 이미지 (배경)
        self.train_id_screen.label_background.setStyleSheet(
            dsBgImg[scene['img_bg']])
        # 문구
        self.train_id_screen.label_guide.setText(
            scene['body_text'])
        
    def makeTrainIDScreenChoice(self, screen, scene, num_choice):
        print(num_choice)

        if num_choice > 0:
            screen.pb_select_1.setStyleSheet(
                dsBtnImg[scene['img_btn1']])
            screen.label_select_1.setText(
                scene['label_select_1'])
        if num_choice > 1:
            screen.pb_select_2.setStyleSheet(
                dsBtnImg[scene['img_btn2']])
            screen.label_select_2.setText(
                scene['label_select_2'])
        if num_choice > 2:
            screen.pb_select_3.setStyleSheet(
                dsBtnImg[scene['img_btn3']])
            screen.label_select_3.setText(
                scene['label_select_3'])
        if num_choice > 3:
            screen.pb_select_4.setStyleSheet(
                dsBtnImg[scene['img_btn4']])
            screen.label_select_4.setText(
                scene['label_select_4'])

    def showTrainIDScene(self):
        if dsTrainID.id_train_index > 0:
            self.uiDlgHide(self.prev_rhs_screen)
        self.uiDlgShow(self.train_id_screen)
        self.prev_rhs_screen = self.train_id_screen
    
    def emitTrainIDSceneScent(self, scene):
        if scene['scent'] > 0 and scene['scent'] < 9:
            self.progressBarScentAndCleanForTrainID(scent_no=scene['scent'],
                                      progress_bar=self.train_id_screen.pg_scent,
                                      label_text=self.train_id_screen.label_guide)

    def uiTrainIDRetry(self):
        print("uiTrainIDRetry")

    def uiTrainIDNext(self):
        print("uiTrainIDNext")
        # 다음 항목
        dsTrainID.id_train_index = dsTrainID.id_train_index + 1
        self.continueTrainIDScenes()

    def uiTrainIDQuit(self):
        print("uiTrainIDQuit")
        self.quitTrainIDScenes()
    
    def uiTrainIDChoice1Check1(self):
        self.ui_train_id_scene_choice_1.pb_check_1.setStyleSheet(
                dsBtnImg['check'])

    def uiTrainIDChoice2Check1(self):
        self.ui_train_id_scene_choice_2.pb_check_1.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_2.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        
    def uiTrainIDChoice2Check2(self):
        self.ui_train_id_scene_choice_2.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_2.pb_check_2.setStyleSheet(
                dsBtnImg['check'])
        
    def uiTrainIDChoice3Check1(self):
        self.ui_train_id_scene_choice_3.pb_check_1.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_3.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        
    def uiTrainIDChoice3Check2(self):
        self.ui_train_id_scene_choice_3.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_2.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_3.pb_check_3.setStyleSheet(
                dsBtnImg['null'])

    def uiTrainIDChoice3Check3(self):
        self.ui_train_id_scene_choice_3.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_3.setStyleSheet(
                dsBtnImg['check'])

    def uiTrainIDChoice4Check1(self):
        self.ui_train_id_scene_choice_4.pb_check_1.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_4.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_4.setStyleSheet(
                dsBtnImg['null'])

    def uiTrainIDChoice4Check2(self):
        self.ui_train_id_scene_choice_4.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_2.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_4.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_4.setStyleSheet(
                dsBtnImg['null'])

    def uiTrainIDChoice4Check3(self):
        self.ui_train_id_scene_choice_4.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_3.setStyleSheet(
                dsBtnImg['check'])
        self.ui_train_id_scene_choice_4.pb_check_4.setStyleSheet(
                dsBtnImg['null'])

    def uiTrainIDChoice4Check4(self):
        self.ui_train_id_scene_choice_4.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_4.setStyleSheet(
                dsBtnImg['check'])

    def clearUiTrainIDChoiceChecks(self):
        self.ui_train_id_scene_choice_1.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_2.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_2.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_3.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_1.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_2.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_3.setStyleSheet(
                dsBtnImg['null'])
        self.ui_train_id_scene_choice_4.pb_check_4.setStyleSheet(
                dsBtnImg['null'])

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 훈련
    def initTrainST(self):
        dsTrainST.st_train_index = 0
        self.ui_train_st_response.hs_selfcheck.setValue(0)
        self.ui_train_st_response.label_selfcheck.setText(
            str(self.ui_train_st_response.hs_selfcheck.value()/10))
        
    def initTrainSTCheck(self):
        self.ui_train_st_response.hs_selfcheck.setValue(0)
        self.ui_train_st_response.label_selfcheck.setText(
            str(self.ui_train_st_response.hs_selfcheck.value()/10))

    def uiTrainSTStart(self):
        # 메뉴 -> 자가 훈련 가이드
        self.uiDlgChange(self.ui_menu_dlg, self.ui_train_st_guide_picture)
        # 사운드
        dsSound.playGuideSound('intro_train_st')

    def uiTrainSTGuidePictureBtnBack(self):
        # 가이드 -> 메뉴
        self.uiDlgChange(self.ui_train_st_guide_picture, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiTrainSTGuidePictureBtnForward(self):
        self.uiDlgHide(self.ui_train_st_guide_picture)
        self.startTrainSTSelect()
    
    def uiTrainSTGuidePictureRecords(self):
        self.makeTrainSTResults()
        self.uiDlgChange(self.ui_train_st_guide_picture, self.ui_train_st_results)
        # 사운드
        dsSound.playGuideSound('records_train_st')

    def startTrainSTSelect(self):
        # 선택지 이미지 반영
        self.ui_train_st_select.label_select_1.setText(
            dsTrainST.st_train_data[1]['name'])
        self.ui_train_st_select.pb_select_1.setStyleSheet(
            dsBtnImg[dsTrainST.st_train_data[1]['name']])
        self.ui_train_st_select.label_select_2.setText(
            dsTrainST.st_train_data[2]['name'])
        self.ui_train_st_select.pb_select_2.setStyleSheet(
            dsBtnImg[dsTrainST.st_train_data[2]['name']])
        self.ui_train_st_select.label_select_3.setText(
            dsTrainST.st_train_data[3]['name'])
        self.ui_train_st_select.pb_select_3.setStyleSheet(
            dsBtnImg[dsTrainST.st_train_data[3]['name']])
        self.ui_train_st_select.label_select_4.setText(
            dsTrainST.st_train_data[4]['name'])
        self.ui_train_st_select.pb_select_4.setStyleSheet(
            dsBtnImg[dsTrainST.st_train_data[4]['name']])
        self.uiDlgShow(self.ui_train_st_select)
        # 사운드
        dsSound.playGuideSound('select_train_st')

    def uiTrainSTSelectChoice1(self):
        print(dsTrainST.st_train_data[1]['name'], dsTrainST.st_train_data[1]['scent_no'])
        dsTrainST.st_train_index = 1
        self.TrainSTProceed()

    def uiTrainSTSelectChoice2(self):
        print(dsTrainST.st_train_data[2]['name'], dsTrainST.st_train_data[2]['scent_no'])
        dsTrainST.st_train_index = 2
        self.TrainSTProceed()
    
    def uiTrainSTSelectChoice3(self):
        print(dsTrainST.st_train_data[3]['name'], dsTrainST.st_train_data[3]['scent_no'])
        dsTrainST.st_train_index = 3
        self.TrainSTProceed()
    
    def uiTrainSTSelectChoice4(self):
        print(dsTrainST.st_train_data[4]['name'], dsTrainST.st_train_data[4]['scent_no'])
        dsTrainST.st_train_index = 4
        self.TrainSTProceed()

    def uiTrainSTSelectQuit(self):
        self.uiDlgChange(self.ui_train_st_select, self.ui_menu_dlg)
        # 사운드
        dsSound.playGuideSound('intro_menu')

    def TrainSTProceed(self):
        self.uiDlgHide(self.ui_train_st_select)
        self.ui_train_st_response.pb_back.setVisible(False)
        self.ui_train_st_response.pb_next.setVisible(False)
        self.ui_train_st_response.pb_retry.setVisible(False)
        self.ui_train_st_response.pb_quit.setVisible(False)
        self.ui_train_st_response.label_bg_selfcheck.setVisible(False)
        self.ui_train_st_response.hs_selfcheck.setVisible(False)
        self.ui_train_st_response.label_selfcheck.setVisible(False)
        # self.ui_train_st_response.label_guide.setText('Olfactory training scent diffusion is in progress')
        self.ui_train_st_response.label_guide.setText(dsText.processText['progress_scent'])
        self.waitTrainSTReady()
        self.ui_train_st_response.pb_select.setStyleSheet(
            dsBtnImg[dsTrainST.st_train_data[dsTrainST.st_train_index]['name']])
        self.ui_train_st_response.label_select.setText(
            dsTrainST.st_train_data[dsTrainST.st_train_index]['name'])
        self.uiDlgShow(self.ui_train_st_response)
        self.sequentialTrainST()
        self.rateTrainST()

    def sequentialTrainST(self):
        # 사운드
        dsSound.playGuideSound('progress_scent_train')
        # 진행바
        self.ui_train_st_response.pg_scent.setVisible(True)
        self.progressBarScentAndCleanForTrainST(scent_no=dsTrainST.st_train_data[dsTrainST.st_train_index]['scent_no'],
                                      progress_bar=self.ui_train_st_response.pg_scent,
                                      label_text=self.ui_train_st_response.label_guide)
        self.ui_train_st_response.pg_scent.setVisible(False)

    def rateTrainST(self):
        self.ui_train_st_response.pb_back.setVisible(True)
        self.ui_train_st_response.pb_next.setVisible(True)
        self.ui_train_st_response.pb_retry.setVisible(True)
        self.ui_train_st_response.pb_quit.setVisible(True)
        self.ui_train_st_response.label_bg_selfcheck.setVisible(True)
        self.ui_train_st_response.hs_selfcheck.setVisible(True)
        self.ui_train_st_response.label_selfcheck.setVisible(True)
        self.ui_train_st_response.label_guide.setText(dsText.processText['question_train_st'])
        
        # 사운드
        dsSound.playGuideSound('rate_train_st')

    def waitTrainSTReady(self):
        self.uiDlgShow(self.ui_train_st_ready)
        # 사운드
        dsSound.playGuideSound('ready_test')
        # 진행바
        for i in range(1, 51):
            QtTest.QTest.qWait(30)
            self.ui_train_st_ready.pg_ready.setValue(i*2)
        QtTest.QTest.qWait(100)
        self.uiDlgHide(self.ui_train_st_ready)
        self.ui_train_st_ready.pg_ready.setValue(0)
    
    def uiTrainSTResponseBack(self):
        self.initTrainST()
        self.uiDlgChange(self.ui_train_st_response, self.ui_train_st_select)

    def uiTrainSTResponseNext(self):
        if self.ui_train_st_response.hs_selfcheck.value() > 0:
            dsTrainSTDB.insertCurrentTable(dsTrainST.st_train_data[dsTrainST.st_train_index]['name'], self.ui_train_st_response.hs_selfcheck.value())
            self.makeTrainSTResults()
            self.uiDlgChange(self.ui_train_st_response, self.ui_train_st_results)
            # 사운드
            dsSound.playGuideSound('records_train_st')

    def uiTrainSTResponseRetry(self):
        self.initTrainSTCheck()
        self.uiDlgHide(self.ui_train_st_response)
        self.TrainSTProceed()

    def uiTrainSTResponseQuit(self):
        self.initTrainST()
        self.uiDlgChange(self.ui_train_st_response, self.ui_menu_dlg)
        # 사운드
        dsSound.playGuideSound('intro_menu')

    def uiTrainSTResponseSelfCheckChanged(self):
        self.ui_train_st_response.label_selfcheck.setText(
            str(self.ui_train_st_response.hs_selfcheck.value()/10))

    def uiTrainSTCompletionComplete(self):
        self.initTrainST()

    def uiTrainSTResultsConfirm(self):
        self.initTrainST()
        self.uiDlgHide(self.ui_train_st_guide_picture)
        self.uiDlgChange(self.ui_train_st_results, self.ui_menu_dlg)
        # 사운드
        dsSound.playGuideSound('intro_menu')

    # 검사 결과 화면을 구성한다. (역치검사)
    def makeTrainSTResults(self):
        data_all = dsTrainSTDB.selectAllFromTable()
        # data_rose = dsTrainDB.selectDataFromTable("Rose")
        # data_lemon = dsTrainDB.selectDataFromTable("Lemon")
        # data_clove = dsTrainDB.selectDataFromTable("Clove")
        # data_eucalyptus = dsTrainDB.selectDataFromTable("Eucalyptus")
        # print(data_rose)
        # print(data_lemon)
        # print(data_clove)
        # print(data_eucalyptus)

        self.ui_train_st_results.resultTable.clear()
        self.ui_train_st_results.resultTable.setRowCount(0)
        self.ui_train_st_results.resultTable.setColumnCount(
            len(data_all[0]) - 4)  # 칸 삭제
        self.ui_train_st_results.resultTable.setHorizontalHeaderLabels(
            dsTrainST.st_train_results_title)  # 회차 제외, 변곡점번호 제외
        self.ui_train_st_results.resultTable.setColumnWidth(0, 190)  # 1번째 열 크기 늘임
        self.ui_train_st_results.resultTable.setColumnWidth(1, 180)  # 2번째 열 크기 늘임
        self.ui_train_st_results.resultTable.setColumnWidth(2, 250)  # 3번째 열 크기 늘임
        self.ui_train_st_results.resultTable.setColumnWidth(3, 200)  # 4번째 열 크기 늘임

        chart_x_rose = []
        chart_y_rose = []
        chart_x_lemon = []
        chart_y_lemon = []
        chart_x_clove = []
        chart_y_clove = []
        chart_x_eucalyptus = []
        chart_y_eucalyptus = []

        tableIndex = 0
        for name, year, month, day, hour, minute, train_scent, selfcheck in data_all:
            if tableIndex > 0:
                nRow = self.ui_train_st_results.resultTable.rowCount()
                self.ui_train_st_results.resultTable.setRowCount(nRow + 1)
                self.ui_train_st_results.resultTable.setItem(nRow, 0, QTableWidgetItem((str("%d.%d.%d"%(year, month, day)))))
                self.ui_train_st_results.resultTable.setItem(nRow, 1, QTableWidgetItem((str("%d:%d"%(hour, minute)))))
                self.ui_train_st_results.resultTable.setItem(nRow, 2, QTableWidgetItem(str(train_scent)))
                self.ui_train_st_results.resultTable.setItem(nRow, 3, QTableWidgetItem(str("%.1f"%(selfcheck/10))))
                self.ui_train_st_results.resultTable.item(nRow, 0).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_train_st_results.resultTable.item(nRow, 1).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_train_st_results.resultTable.item(nRow, 2).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_train_st_results.resultTable.item(nRow, 3).setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter)
                self.ui_train_st_results.resultTable.setCurrentCell(nRow, 3)
                
            if train_scent == "장미":
                chart_x_rose.append(tableIndex) #"%d.%d.%d %d:%d"%(year, month, day, hour, minute))
                chart_y_rose.append(selfcheck/10)
            elif train_scent == "레몬":
                chart_x_lemon.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
                chart_y_lemon.append(selfcheck/10) #(selfcheck)
            elif train_scent == "홍삼":
                chart_x_clove.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
                chart_y_clove.append(selfcheck/10)
            elif train_scent == "유칼립투스":
                chart_x_eucalyptus.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
                chart_y_eucalyptus.append(selfcheck/10)
            
            # 영문
            # if train_scent == "Rose":
            #     chart_x_rose.append(tableIndex) #"%d.%d.%d %d:%d"%(year, month, day, hour, minute))
            #     chart_y_rose.append(selfcheck/10)
            # elif train_scent == "Lemon":
            #     chart_x_lemon.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
            #     chart_y_lemon.append(selfcheck/10) #(selfcheck)
            # elif train_scent == "Clove":
            #     chart_x_clove.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
            #     chart_y_clove.append(selfcheck/10)
            # elif train_scent == "Eucalyptus":
            #     chart_x_eucalyptus.append(tableIndex) #("%d.%d.%d %d:%d"%(year, month, day, hour, minute))
            #     chart_y_eucalyptus.append(selfcheck/10)

            tableIndex += 1

        print(chart_y_rose)
        print(chart_y_lemon)
        print(chart_y_clove)
        print(chart_y_eucalyptus)
        
        self.ui_train_st_results.widgetChart.apply_line_4_chart(chart_x_rose, chart_y_rose, 
                                                                chart_x_lemon, chart_y_lemon,
                                                                chart_x_clove, chart_y_clove,
                                                                chart_x_eucalyptus, chart_y_eucalyptus)



    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 설정
    def uiSettingsBackClicked(self):
        self.uiDlgChange(self.ui_settings_dlg, self.ui_menu_dlg)
        # 사운드 (메뉴)
        dsSound.playGuideSound('intro_menu')

    def uiSettingsScentPowerChanged(self):
        self.ui_settings_dlg.te_scent_power.setPlainText(str(self.ui_settings_dlg.hs_scent_power.value()))

    def uiSettingsScentRunTimeChanged(self):
        self.ui_settings_dlg.te_scent_run_time.setPlainText(str(self.ui_settings_dlg.hs_scent_run_time.value()))

    def uiSettingsScentPostDelayChanged(self):
        self.ui_settings_dlg.te_scent_post_delay.setPlainText(str(self.ui_settings_dlg.hs_scent_post_delay.value()))

    def uiSettingsCleaningPowerChanged(self):
        self.ui_settings_dlg.te_cleaning_power.setPlainText(str(self.ui_settings_dlg.hs_cleaning_power.value()))

    def uiSettingsCleaningRunTimeChanged(self):
        self.ui_settings_dlg.te_cleaning_run_time.setPlainText(str(self.ui_settings_dlg.hs_cleaning_run_time.value()))

    def uiSettingsCleaningPostDelayChanged(self):
        self.ui_settings_dlg.te_cleaning_post_delay.setPlainText(str(self.ui_settings_dlg.hs_cleaning_post_delay.value()))
    
    def uiSettingsScentEmitIntervalChanged(self):
        self.ui_settings_dlg.te_scent_emit_interval.setPlainText(str(self.ui_settings_dlg.hs_scent_emit_interval.value()))

    def uiSettingsThresTestMaxLevelChanged(self):
        self.ui_settings_dlg.te_thres_test_max_level.setPlainText(
            str(self.ui_settings_dlg.hs_thres_test_max_level.value()))

    def uiSettingsThresNodeMaxNumChanged(self):
        self.ui_settings_dlg.te_thres_node_max_num.setPlainText(
            str(self.ui_settings_dlg.hs_thres_node_max_num.value()))

    def uiSettingsThresNodeScoreNumChanged(self):
        self.ui_settings_dlg.te_thres_node_score_num.setPlainText(
            str(self.ui_settings_dlg.hs_thres_node_score_num.value()))

    # 설정 파일을 로드한다.
    def loadSettingsFile(self):
        if os.path.isfile('settings'):
            json_data = open('settings').read()
            dsSetting.dsParam = json.loads(json_data)
            print(dsSetting.dsParam)

    # 설정을 파일에 저장한다.
    def saveSettingsFile(self):
        with open('settings', 'w', encoding='utf-8') as make_file:
            json.dump(dsSetting.dsParam, make_file, ensure_ascii=False, indent='\t')

    # json 파일을 로드하여 설정 값을 반영한다.
    def updateSettingsUI(self):
        self.loadSettingsFile()
        self.ui_settings_dlg.te_scent_power.setPlainText(str(dsSetting.dsParam['scent_power']))
        self.ui_settings_dlg.hs_scent_power.setValue(dsSetting.dsParam['scent_power'])
        self.ui_settings_dlg.te_scent_run_time.setPlainText(str(dsSetting.dsParam['scent_run_time']))
        self.ui_settings_dlg.hs_scent_run_time.setValue(dsSetting.dsParam['scent_run_time'])
        self.ui_settings_dlg.te_scent_post_delay.setPlainText(str(dsSetting.dsParam['scent_post_delay']))
        self.ui_settings_dlg.hs_scent_post_delay.setValue(dsSetting.dsParam['scent_post_delay'])
        self.ui_settings_dlg.te_cleaning_power.setPlainText(str(dsSetting.dsParam['cleaning_power']))
        self.ui_settings_dlg.hs_cleaning_power.setValue(dsSetting.dsParam['cleaning_power'])
        self.ui_settings_dlg.te_cleaning_run_time.setPlainText(str(dsSetting.dsParam['cleaning_run_time']))
        self.ui_settings_dlg.hs_cleaning_run_time.setValue(dsSetting.dsParam['cleaning_run_time'])
        self.ui_settings_dlg.te_cleaning_post_delay.setPlainText(str(dsSetting.dsParam['cleaning_post_delay']))
        self.ui_settings_dlg.hs_cleaning_post_delay.setValue(dsSetting.dsParam['cleaning_post_delay'])
        self.ui_settings_dlg.te_scent_emit_interval.setPlainText(str(dsSetting.dsParam['scent_emit_interval']))
        self.ui_settings_dlg.hs_scent_emit_interval.setValue(dsSetting.dsParam['scent_emit_interval'])
        self.ui_settings_dlg.te_thres_test_max_level.setPlainText(str(dsSetting.dsParam['thres_test_max_level']))
        self.ui_settings_dlg.hs_thres_test_max_level.setValue(dsSetting.dsParam['thres_test_max_level'])
        self.ui_settings_dlg.te_thres_node_max_num.setPlainText(str(dsSetting.dsParam['thres_node_max_num']))
        self.ui_settings_dlg.hs_thres_node_max_num.setValue(dsSetting.dsParam['thres_node_max_num'])
        self.ui_settings_dlg.te_thres_node_score_num.setPlainText(str(dsSetting.dsParam['thres_node_score_num']))
        self.ui_settings_dlg.hs_thres_node_score_num.setValue(dsSetting.dsParam['thres_node_score_num'])
        self.ui_settings_dlg.cb_voice_onoff.setCurrentIndex(dsSetting.dsParam['voice_onoff'])
        self.ui_settings_dlg.cb_result_show_onoff.setCurrentIndex(dsSetting.dsParam['result_show_onoff'])
        self.ui_settings_dlg.cb_front_onoff.setCurrentIndex(dsSetting.dsParam['front_onoff'])
        self.ui_settings_dlg.cb_window_bars_onoff.setCurrentIndex(dsSetting.dsParam['window_bars_onoff'])

    # 설정 UI의 변경사항을 반영하고 json 파일에 저장한다.
    def uiSettingUpdateSettings(self):
        dsSetting.dsParam['scent_power'] = int(self.ui_settings_dlg.te_scent_power.toPlainText())
        dsSetting.dsParam['scent_run_time'] = int(self.ui_settings_dlg.te_scent_run_time.toPlainText())
        dsSetting.dsParam['scent_post_delay'] = int(self.ui_settings_dlg.te_scent_post_delay.toPlainText())
        dsSetting.dsParam['cleaning_power'] = int(self.ui_settings_dlg.te_cleaning_power.toPlainText())
        dsSetting.dsParam['cleaning_run_time'] = int(self.ui_settings_dlg.te_cleaning_run_time.toPlainText())
        dsSetting.dsParam['cleaning_post_delay'] = int(self.ui_settings_dlg.te_cleaning_post_delay.toPlainText())
        dsSetting.dsParam['scent_emit_interval'] = int(self.ui_settings_dlg.te_scent_emit_interval.toPlainText())
        dsSetting.dsParam['thres_test_max_level'] = int(self.ui_settings_dlg.te_thres_test_max_level.toPlainText())
        dsSetting.dsParam['thres_node_max_num'] = int(self.ui_settings_dlg.te_thres_node_max_num.toPlainText())
        dsSetting.dsParam['thres_node_score_num'] = int(self.ui_settings_dlg.te_thres_node_score_num.toPlainText())
        dsSetting.dsParam['voice_onoff'] = self.ui_settings_dlg.cb_voice_onoff.currentIndex()
        dsSetting.dsParam['result_show_onoff'] = self.ui_settings_dlg.cb_result_show_onoff.currentIndex()
        dsSetting.dsParam['front_onoff'] = self.ui_settings_dlg.cb_front_onoff.currentIndex()
        dsSetting.dsParam['window_bars_onoff'] = self.ui_settings_dlg.cb_window_bars_onoff.currentIndex()
        print(dsSetting.dsParam)
        self.saveSettingsFile()

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # 데이터 저장
    def saveDataThreshold(self):
        # 데이터 폴더 만들기
        if not os.path.isdir(dsText.resultText['results_data_raw_path']):
            os.mkdir(dsText.resultText['results_data_raw_path'])
        now = datetime.now()
        save_file = '%s\\' + dsText.resultText['results_data_raw_path'] + '\\%s_%s세_%s_%04d년%02d월%02d일_%02d시%02d분_역치검사.xlsx' % (
            os.getcwd(), self.name, self.age, self.gender, now.year, now.month, now.day, now.hour, now.minute)
        workbook = xlsxwriter.Workbook(save_file)
        # 엑셀 채우기
        worksheet = workbook.add_worksheet()
        row = 0
        for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
                in dsTestTH.th_results:
            worksheet.write(row, 0, index)
            worksheet.write(row, 1, threshold)
            worksheet.write(row, 2, current_level)
            worksheet.write(row, 3, answer)
            worksheet.write(row, 4, response)
            worksheet.write(row, 5, is_correct)
            worksheet.write(row, 6, is_node)
            worksheet.write(row, 7, node_num)
            row += 1
        # 점수 정보 넣기
        worksheet.write('J1', dsText.resultText['result_test_threshold_title'])
        worksheet.write('J2', dsText.resultText['result_test_threshold_score'])
        worksheet.write('K2', '%.1f'%(dsTestTH.T_score))
        # 차트 만들기
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'name': '=Sheet1!$B$1',
                          'categories': '=Sheet1!$A$2:$A%d' % row,
                          'values': '=Sheet1!$B$2:$B$%d' % row,
                          'marker': {'type': 'automatic'}
                          })
        chart.set_title({'name': dsText.resultText['result_test_threshold_title']})
        chart.set_x_axis({'name': dsText.resultText['result_test_threshold_seq']})
        chart.set_y_axis({'name': dsText.resultText['result_test_threshold_level']})
        chart.set_style(10)
        worksheet.insert_chart('J3', chart, {'x_offset': 5, 'y_offset': 5})
        # 닫기
        workbook.close()

    def saveDataDiscrimination(self):
        # 데이터 폴더 만들기
        if not os.path.isdir(dsText.resultText['results_data_raw_path']):
            os.mkdir(dsText.resultText['results_data_raw_path'])
        now = datetime.now()
        save_file = '%s\\' + dsText.resultText['results_data_raw_path'] + '\\%s_%s세_%s_%04d년%02d월%02d일_%02d시%02d분_식별검사.xlsx' % (
            os.getcwd(), self.name, self.age, self.gender, now.year, now.month, now.day, now.hour, now.minute)
        workbook = xlsxwriter.Workbook(save_file)
        # 엑셀 채우기
        worksheet = workbook.add_worksheet()
        row = 0
        for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct \
                in dsTestDC.dc_results:
            worksheet.write(row, 0, index)
            worksheet.write(row, 1, scent_no1)
            worksheet.write(row, 2, scent_no2)
            worksheet.write(row, 3, scent_no3)
            worksheet.write(row, 4, answer)
            worksheet.write(row, 5, response)
            worksheet.write(row, 6, is_correct)
            row += 1
        # 점수 정보 넣기
        worksheet.write('I1', dsText.resultText['result_test_discrimination_title'])
        worksheet.write('I2', dsText.resultText['result_test_discrimination_correct'])
        worksheet.write('J2', '=COUNTIF(G:G, 1)')
        worksheet.write('I3', dsText.resultText['result_test_discrimination_incorrect'])
        worksheet.write('J3', '=12-J2')
        # 차트 만들기
        chart = workbook.add_chart({'type': 'pie'})
        chart.add_series({'name': dsText.resultText['result_test_discrimination_title'],
                          'categories': '=Sheet1!$I$2:$I$3',
                          'values': '=Sheet1!$J$2:$J$3',
                          'data_labels': {'value': True, 'percentage': True}
                          })
        chart.set_title({'name': dsText.resultText['result_test_discrimination_title']})
        # chart.set_rotation(90)
        chart.set_style(10)
        worksheet.insert_chart('I4', chart, {'x_offset': 5, 'y_offset': 5})
        workbook.close()

    def saveDataIdentification(self):
        # 데이터 폴더 만들기
        if not os.path.isdir(dsText.resultText['results_data_raw_path']):
            os.mkdir(dsText.resultText['results_data_raw_path'])
        now = datetime.now()
        save_file = '%s\\' % os.getcwd() \
            + dsText.resultText['results_data_raw_path'] \
            + '\\%s_%s세_%s_%04d년%02d월%02d일_%02d시%02d분_인지검사.xlsx' % (
            self.name, self.age, self.gender, now.year, now.month, now.day, now.hour, now.minute)
        workbook = xlsxwriter.Workbook(save_file)
        # 엑셀 채우기
        worksheet = workbook.add_worksheet()
        row = 0
        for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                in dsTestID.id_results:
            worksheet.write(row, 0, index)
            worksheet.write(row, 1, answer)
            worksheet.write(row, 2, choice_response)
            worksheet.write(row, 3, is_choice_correct)
            # worksheet.write(row, 4, str_response) # 주관식 불필요
            # worksheet.write(row, 5, is_str_correct) # 주관식 불필요
            row += 1
        # 점수 정보 넣기
        worksheet.write('F1', dsText.resultText['result_test_identification_title'])
        worksheet.write('F2', dsText.resultText['result_test_identification_correct'])
        worksheet.write('G2', '=COUNTIF(D:D, 1)')
        worksheet.write('F3', dsText.resultText['result_test_identification_incorrect'])
        worksheet.write('G3', '=12-G2')
        # 차트 만들기
        chart = workbook.add_chart({'type': 'pie'})
        chart.add_series({'name': dsText.resultText['result_test_identification_title'],
                          'categories': '=Sheet1!$F$2:$F$3',
                          'values': '=Sheet1!$G$2:$G$3',
                          'data_labels': {'value': True, 'percentage': True}
                          })
        chart.set_title({'name': dsText.resultText['result_test_identification_title']})
        # chart.set_rotation(90)
        chart.set_style(10)
        worksheet.insert_chart('F4', chart, {'x_offset': 5, 'y_offset': 5})
        workbook.close()

    def saveDataResults(self):
        if len(dsTestTH.th_results) > 1 or \
                len(dsTestDC.dc_results) > 1 or \
                len(dsTestID.id_results) > 1:
            print("saveDataResults")
        else:
            return
        # 데이터 폴더 만들기
        if not os.path.isdir(dsText.reportText['report_data_path']):
            os.mkdir(dsText.reportText['report_data_path'])
        now = datetime.now()
        save_file = '%s\\'+ dsText.reportText['report_data_path'] + '\\%s_%s세_%s_%04d년%02d월%02d일_%02d시%02d분_종합결과.xlsx' % (
            os.getcwd(), self.name, self.age, self.gender, now.year, now.month, now.day, now.hour, now.minute)
        workbook = xlsxwriter.Workbook(save_file)

        # 엑셀
        worksheet_main = workbook.add_worksheet(dsText.reportText['report_sheet'])
        worksheet_main.set_column('A:M', 5.4) # 엑셀 셀 크기

        # 셀 포맷
        format_title = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
        format_small_title = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'left', 'valign': 'vcenter'})
        format_small_table_title = workbook.add_format({'bold': True, 'font_size': 11, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_score = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'right', 'valign': 'vcenter'})
        format_score_base = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'left', 'valign': 'vcenter'})
        format_table = workbook.add_format({'font_size': 9, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'shrink': True})

        # 메인 시트 일반 정보
        worksheet_main.write('G1', dsText.reportText['report_title'], format_title)
        worksheet_main.write('A3', dsText.reportText['report_reg_num'], format_small_title)
        worksheet_main.write('A4', dsText.reportText['report_date'], format_small_title)
        worksheet_main.write('C4', '%04d년%02d월%02d일_%02d시%02d분' % (now.year, now.month, now.day, now.hour, now.minute))
        worksheet_main.write('A5', dsText.reportText['report_name'], format_small_title)
        worksheet_main.write('B5', self.name)
        worksheet_main.write('C5', dsText.reportText['report_gender'], format_small_title)
        worksheet_main.write('D5', self.gender)
        worksheet_main.write('E5', dsText.reportText['report_age'], format_small_title)
        worksheet_main.write('F5', self.age)
        worksheet_main.write('A6', dsText.reportText['report_both_nostrils'], format_small_title)
        worksheet_main.write('C6', dsText.reportText['report_right_nostril'], format_small_title)
        worksheet_main.write('E6', dsText.reportText['report_left_nostril'], format_small_title)

        worksheet_main.merge_range('G3:I3', dsText.reportText['report_ammonia'], format_small_table_title)
        worksheet_main.merge_range('G4:I5', '', format_small_table_title) # 빈칸
        worksheet_main.merge_range('J3:K3', dsText.reportText['report_total_score'], format_small_table_title)
        worksheet_main.merge_range('J4:K5', '%d'%(dsTest.TDI_score), format_small_table_title)
        worksheet_main.merge_range('L3:M3', dsText.reportText['report_nomosmia'], format_small_table_title)
        worksheet_main.merge_range('L4:M4', dsText.reportText['report_hyposmia'], format_small_table_title)
        worksheet_main.merge_range('L5:M5', dsText.reportText['report_anosmia'], format_small_table_title)
        
        # 메인 시트 점수 정보
        worksheet_main.write('A8', dsText.resultText['result_test_threshold_title'], format_small_title)
        worksheet_main.write('E8', dsText.resultText['result_test_threshold_time'] + ':  %s' % dsUtils.hmsFormFromCounts(dsTestTH.th_time_count))
        worksheet_main.write('K8', dsText.resultText['result_test_threshold_point'] + ':', format_score)
        worksheet_main.write('L8', '%.1f'%(dsTestTH.T_score), format_score)
        worksheet_main.write('M8', '/' + dsText.resultText['result_test_threshold_range'], format_score_base)
        
        worksheet_main.write('A24', dsText.resultText['result_test_discrimination_title'], format_small_title)
        worksheet_main.write('E24', dsText.resultText['result_test_discrimination_time'] + '  %s' % dsUtils.hmsFormFromCounts(dsTestDC.dc_time_count))
        worksheet_main.write('K24', dsText.resultText['result_test_discrimination_point'] + ':', format_score)
        worksheet_main.write('L24', '%d'%(dsTestDC.D_score), format_score)
        worksheet_main.write('M24', '/' + dsText.resultText['result_test_discrimination_range'], format_score_base)
        
        worksheet_main.write('A30', dsText.resultText['result_test_identification_title'], format_small_title)
        worksheet_main.write('E30', dsText.resultText['result_test_identification_time'] + ':  %s' % dsUtils.hmsFormFromCounts(dsTestID.id_time_count))
        worksheet_main.write('K30', dsText.resultText['result_test_identification_point'] + ':', format_score)
        worksheet_main.write('L30', '%d'%(dsTestID.I_score), format_score)
        worksheet_main.write('M30', '/' + dsText.resultText['result_test_identification_range'], format_score_base)
        
        worksheet_main.write('A36', dsText.reviewText['review_test_title'], format_small_title)
        worksheet_main.write('K36', dsText.reviewText['review_test_score'] + ':', format_score)
        worksheet_main.write('L36', str(self.ui_test_results_review_dlg.hs_review.value()/10), format_score)
        worksheet_main.write('M36', '/' + dsText.reviewText['review_test_range'], format_score_base)
        worksheet_main.merge_range('A37:M39', self.ui_test_results_review_dlg.te_review.toPlainText(), format_table)

        # 역치 결과 Sheet
        if len(dsTestTH.th_results) > 1:
            worksheet_th = workbook.add_worksheet(dsText.reportText['report_sheet_threshold'])
            row = 0
            for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
                    in dsTestTH.th_results:
                worksheet_th.write(row, 0, index)
                worksheet_th.write(row, 1, threshold)
                worksheet_th.write(row, 2, current_level)
                worksheet_th.write(row, 3, answer)
                worksheet_th.write(row, 4, response)
                worksheet_th.write(row, 5, is_correct)
                worksheet_th.write(row, 6, is_node)
                worksheet_th.write(row, 7, node_num)
                row += 1
            # 점수 정보 넣기
            worksheet_th.write('J1', dsText.resultText['result_test_threshold_title'])
            worksheet_th.write('J2', dsText.resultText['result_test_threshold_score'])
            worksheet_th.write('K2', '%.1f'%(dsTestTH.T_score))
            # 차트 만들기
            chart_th = workbook.add_chart({'type': 'line'})
            chart_th.add_series({'name': '=Threshold!$B$1',
                              'categories': '=Threshold!$A$2:$A%d' % row,
                              'values': '=Threshold!$C$2:$C$%d' % row,
                              'marker': {'type': 'automatic'}
                              })
            chart_th.set_title({'name': dsText.resultText['result_test_threshold_title']})
            chart_th.set_x_axis({'name': dsText.resultText['result_test_threshold_seq']})
            chart_th.set_y_axis({'name': dsText.resultText['result_test_threshold_density']})
            chart_th.set_style(10)
            worksheet_th.insert_chart('J3', chart_th, {'x_offset': 5, 'y_offset': 5})
            # 메인 시트 차트
            m_chart_th = workbook.add_chart({'type': 'line'})
            m_chart_th.add_series({#'name': '=Threshold!$B$1', # 이름 안보이게
                              'categories': '=Threshold!$A$2:$A%d' % row,
                              'values': '=Threshold!$C$2:$C$%d' % row,
                              'marker': {'type': 'automatic'}
                              })
            # m_chart_th.set_title({'name': '역치검사 결과'})
            m_chart_th.set_x_axis({'name': dsText.resultText['result_test_threshold_seq']})
            m_chart_th.set_y_axis({'name': dsText.resultText['result_test_threshold_density']})
            m_chart_th.set_legend({'none': True}) # 범례 안보이게
            m_chart_th.set_style(10)
            worksheet_main.insert_chart('B9', m_chart_th, {'x_offset': 0, 'y_offset': 5})

        # 식별 결과 Sheet
        if len(dsTestDC.dc_results) > 1:
            worksheet_dc = workbook.add_worksheet("Discrimination")
            row = 0
            m_col = 0 # 메인 시트
            for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct \
                    in dsTestDC.dc_results:
                worksheet_dc.write(row, 0, index)
                worksheet_dc.write(row, 1, scent_no1)
                worksheet_dc.write(row, 2, scent_no2)
                worksheet_dc.write(row, 3, scent_no3)
                worksheet_dc.write(row, 4, answer)
                worksheet_dc.write(row, 5, response)
                worksheet_dc.write(row, 6, is_correct)
                row += 1
                # 메인 시트
                worksheet_main.write(24, m_col, index, format_table)
                worksheet_main.write(25, m_col, answer, format_table)
                worksheet_main.write(26, m_col, response, format_table)
                worksheet_main.write(27, m_col, dsUtils.isCorrectToOX(is_correct), format_table)
                m_col += 1
            # 점수 정보 넣기
            worksheet_dc.write('I1', dsText.resultText['result_test_discrimination_title'])
            worksheet_dc.write('I2', dsText.resultText['result_test_discrimination_correct'])
            worksheet_dc.write('J2', '=COUNTIF(G:G, 1)')
            worksheet_dc.write('I3', dsText.resultText['result_test_discrimination_incorrect'])
            worksheet_dc.write('J3', '=12-J2')
            # 차트 만들기
            chart_dc = workbook.add_chart({'type': 'pie'})
            chart_dc.add_series({'name': dsText.resultText['result_test_discrimination_title'],
                              'categories': '=Discrimination!$I$2:$I$3',
                              'values': '=Discrimination!$J$2:$J$3',
                              'data_labels': {'value': True, 'percentage': True}
                              })
            chart_dc.set_title({'name': dsText.resultText['result_test_discrimination_title']})
            # chart_dc.set_rotation(90)
            chart_dc.set_style(10)
            worksheet_dc.insert_chart('I4', chart_dc, {'x_offset': 5, 'y_offset': 5})

        # 인지 결과 Sheet
        if len(dsTestID.id_results) > 1:
            worksheet_id = workbook.add_worksheet("Identification")
            row = 0
            m_col = 0 # 메인 시트
            for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                    in dsTestID.id_results:
                worksheet_id.write(row, 0, index)
                worksheet_id.write(row, 1, answer)
                worksheet_id.write(row, 2, choice_response)
                worksheet_id.write(row, 3, is_choice_correct)
                row += 1
                # 메인 시트
                worksheet_main.write(30, m_col, index, format_table)
                worksheet_main.write(31, m_col, answer, format_table)
                worksheet_main.write(32, m_col, choice_response, format_table)
                worksheet_main.write(33, m_col, dsUtils.isCorrectToOX(is_choice_correct), format_table)
                m_col += 1
            # 점수 정보 넣기
            worksheet_id.write('F1', dsText.resultText['result_test_identification_title'])
            worksheet_id.write('F2', dsText.resultText['result_test_identification_correct'])
            worksheet_id.write('G2', '=COUNTIF(D:D, 1)')
            worksheet_id.write('F3', dsText.resultText['result_test_identification_incorrect'])
            worksheet_id.write('G3', '=12-G2')
            # 차트 만들기
            chart_id = workbook.add_chart({'type': 'pie'})
            chart_id.add_series({'name': dsText.resultText['result_test_identification_title'],
                              'categories': '=Identification!$F$2:$F$3',
                              'values': '=Identification!$G$2:$G$3',
                              'data_labels': {'value': True, 'percentage': True}
                              })
            chart_id.set_title({'name': dsText.resultText['result_test_identification_title']})
            # chart_id.set_rotation(90)
            chart_id.set_style(10)
            worksheet_id.insert_chart('F4', chart_id, {'x_offset': 5, 'y_offset': 5})

        # 닫기
        workbook.close()

    def saveDataResultsTemp(self):
        self.setTestsScores()
        if len(dsTestTH.th_results) > 1 or \
                len(dsTestDC.dc_results) > 1 or \
                len(dsTestID.id_results) > 1:
            print("saveDataResultsTemp")
        else:
            return
        # 데이터 폴더 만들기
        if not os.path.isdir(dsText.reportText['report_data_temp_path']):
            os.mkdir(dsText.reportText['report_data_temp_path'])
        now = datetime.now()
        save_file = '%s\\' + dsText.reportText['report_data_temp_path'] + '\\%s_%s세_%s_%04d년%02d월%02d일_%02d시%02d분_종합결과.xlsx' % (
            os.getcwd(), self.name, self.age, self.gender, now.year, now.month, now.day, now.hour, now.minute)
        workbook = xlsxwriter.Workbook(save_file)

        # 엑셀
        worksheet_main = workbook.add_worksheet(dsText.reportText['report_sheet'])
        worksheet_main.set_column('A:M', 5.4) # 엑셀 셀 크기

        # 셀 포맷
        format_title = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
        format_small_title = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'left', 'valign': 'vcenter'})
        format_small_table_title = workbook.add_format({'bold': True, 'font_size': 11, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_score = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'right', 'valign': 'vcenter'})
        format_score_base = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'left', 'valign': 'vcenter'})
        format_table = workbook.add_format({'font_size': 9, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'shrink': True})

        # 메인 시트 일반 정보
        worksheet_main.write('G1', dsText.reportText['report_title'], format_title)
        worksheet_main.write('A3', dsText.reportText['report_reg_num'], format_small_title)
        worksheet_main.write('A4', dsText.reportText['report_date'], format_small_title)
        worksheet_main.write('C4', '%04d년%02d월%02d일_%02d시%02d분' % (now.year, now.month, now.day, now.hour, now.minute))
        worksheet_main.write('A5', dsText.reportText['report_name'], format_small_title)
        worksheet_main.write('B5', self.name)
        worksheet_main.write('C5', dsText.reportText['report_gender'], format_small_title)
        worksheet_main.write('D5', self.gender)
        worksheet_main.write('E5', dsText.reportText['report_age'], format_small_title)
        worksheet_main.write('F5', self.age)
        worksheet_main.write('A6', dsText.reportText['report_both_nostrils'], format_small_title)
        worksheet_main.write('C6', dsText.reportText['report_right_nostril'], format_small_title)
        worksheet_main.write('E6', dsText.reportText['report_left_nostril'], format_small_title)

        worksheet_main.merge_range('G3:I3', dsText.reportText['report_ammonia'], format_small_table_title)
        worksheet_main.merge_range('G4:I5', '', format_small_table_title) # 빈칸
        worksheet_main.merge_range('J3:K3', dsText.reportText['report_total_score'], format_small_table_title)
        worksheet_main.merge_range('J4:K5', '%d'%(dsTest.TDI_score), format_small_table_title)
        worksheet_main.merge_range('L3:M3', dsText.reportText['report_nomosmia'], format_small_table_title)
        worksheet_main.merge_range('L4:M4', dsText.reportText['report_hyposmia'], format_small_table_title)
        worksheet_main.merge_range('L5:M5', dsText.reportText['report_anosmia'], format_small_table_title)
        
        # 메인 시트 점수 정보
        worksheet_main.write('A8', dsText.resultText['result_test_threshold_title'], format_small_title)
        worksheet_main.write('E8', dsText.resultText['result_test_threshold_time'] + ':  %s' % dsUtils.hmsFormFromCounts(dsTestTH.th_time_count))
        worksheet_main.write('K8', dsText.resultText['result_test_threshold_point'] + ':', format_score)
        worksheet_main.write('L8', '%.1f'%(dsTestTH.T_score), format_score)
        worksheet_main.write('M8', '/' + dsText.resultText['result_test_threshold_range'], format_score_base)
        
        worksheet_main.write('A24', dsText.resultText['result_test_discrimination_title'], format_small_title)
        worksheet_main.write('E24', dsText.resultText['result_test_discrimination_time'] + '  %s' % dsUtils.hmsFormFromCounts(dsTestDC.dc_time_count))
        worksheet_main.write('K24', dsText.resultText['result_test_discrimination_point'] + ':', format_score)
        worksheet_main.write('L24', '%d'%(dsTestDC.D_score), format_score)
        worksheet_main.write('M24', '/' + dsText.resultText['result_test_discrimination_range'], format_score_base)
        
        worksheet_main.write('A30', dsText.resultText['result_test_identification_title'], format_small_title)
        worksheet_main.write('E30', dsText.resultText['result_test_identification_time'] + ':  %s' % dsUtils.hmsFormFromCounts(dsTestID.id_time_count))
        worksheet_main.write('K30', dsText.resultText['result_test_identification_point'] + ':', format_score)
        worksheet_main.write('L30', '%d'%(dsTestID.I_score), format_score)
        worksheet_main.write('M30', '/' + dsText.resultText['result_test_identification_range'], format_score_base)
        
        worksheet_main.write('A36', dsText.reviewText['review_test_title'], format_small_title)
        worksheet_main.write('K36', dsText.reviewText['review_test_score'] + ':', format_score)
        worksheet_main.write('L36', str(self.ui_test_results_review_dlg.hs_review.value()/10), format_score)
        worksheet_main.write('M36', '/' + dsText.reviewText['review_test_range'], format_score_base)
        worksheet_main.merge_range('A37:M39', self.ui_test_results_review_dlg.te_review.toPlainText(), format_table)

        # 역치 결과 Sheet
        if len(dsTestTH.th_results) > 1:
            worksheet_th = workbook.add_worksheet(dsText.reportText['report_sheet_threshold'])
            row = 0
            for index, threshold, current_level, answer, response, is_correct, is_node, node_num \
                    in dsTestTH.th_results:
                worksheet_th.write(row, 0, index)
                worksheet_th.write(row, 1, threshold)
                worksheet_th.write(row, 2, current_level)
                worksheet_th.write(row, 3, answer)
                worksheet_th.write(row, 4, response)
                worksheet_th.write(row, 5, is_correct)
                worksheet_th.write(row, 6, is_node)
                worksheet_th.write(row, 7, node_num)
                row += 1
            # 점수 정보 넣기
            worksheet_th.write('J1', dsText.resultText['result_test_threshold_title'])
            worksheet_th.write('J2', dsText.resultText['result_test_threshold_score'])
            worksheet_th.write('K2', '%.1f'%(dsTestTH.T_score))
            # 차트 만들기
            chart_th = workbook.add_chart({'type': 'line'})
            chart_th.add_series({'name': '=Threshold!$B$1',
                              'categories': '=Threshold!$A$2:$A%d' % row,
                              'values': '=Threshold!$C$2:$C$%d' % row,
                              'marker': {'type': 'automatic'}
                              })
            chart_th.set_title({'name': dsText.resultText['result_test_threshold_title']})
            chart_th.set_x_axis({'name': dsText.resultText['result_test_threshold_seq']})
            chart_th.set_y_axis({'name': dsText.resultText['result_test_threshold_density']})
            chart_th.set_style(10)
            worksheet_th.insert_chart('J3', chart_th, {'x_offset': 5, 'y_offset': 5})
            # 메인 시트 차트
            m_chart_th = workbook.add_chart({'type': 'line'})
            m_chart_th.add_series({#'name': '=Threshold!$B$1', # 이름 안보이게
                              'categories': '=Threshold!$A$2:$A%d' % row,
                              'values': '=Threshold!$C$2:$C$%d' % row,
                              'marker': {'type': 'automatic'}
                              })
            # m_chart_th.set_title({'name': '역치검사 결과'})
            m_chart_th.set_x_axis({'name': dsText.resultText['result_test_threshold_seq']})
            m_chart_th.set_y_axis({'name': dsText.resultText['result_test_threshold_density']})
            m_chart_th.set_legend({'none': True}) # 범례 안보이게
            m_chart_th.set_style(10)
            worksheet_main.insert_chart('B9', m_chart_th, {'x_offset': 0, 'y_offset': 5})

        # 식별 결과 Sheet
        if len(dsTestDC.dc_results) > 1:
            worksheet_dc = workbook.add_worksheet("Discrimination")
            row = 0
            m_col = 0 # 메인 시트
            for index, scent_no1, scent_no2, scent_no3, answer, response, is_correct \
                    in dsTestDC.dc_results:
                worksheet_dc.write(row, 0, index)
                worksheet_dc.write(row, 1, scent_no1)
                worksheet_dc.write(row, 2, scent_no2)
                worksheet_dc.write(row, 3, scent_no3)
                worksheet_dc.write(row, 4, answer)
                worksheet_dc.write(row, 5, response)
                worksheet_dc.write(row, 6, is_correct)
                row += 1
                # 메인 시트
                worksheet_main.write(24, m_col, index, format_table)
                worksheet_main.write(25, m_col, answer, format_table)
                worksheet_main.write(26, m_col, response, format_table)
                worksheet_main.write(27, m_col, dsUtils.isCorrectToOX(is_correct), format_table)
                m_col += 1
            # 점수 정보 넣기
            worksheet_dc.write('I1', dsText.resultText['result_test_discrimination_title'])
            worksheet_dc.write('I2', dsText.resultText['result_test_discrimination_correct'])
            worksheet_dc.write('J2', '=COUNTIF(G:G, 1)')
            worksheet_dc.write('I3', dsText.resultText['result_test_discrimination_incorrect'])
            worksheet_dc.write('J3', '=12-J2')
            # 차트 만들기
            chart_dc = workbook.add_chart({'type': 'pie'})
            chart_dc.add_series({'name': dsText.resultText['result_test_discrimination_title'],
                              'categories': '=Discrimination!$I$2:$I$3',
                              'values': '=Discrimination!$J$2:$J$3',
                              'data_labels': {'value': True, 'percentage': True}
                              })
            chart_dc.set_title({'name': dsText.resultText['result_test_discrimination_title']})
            # chart_dc.set_rotation(90)
            chart_dc.set_style(10)
            worksheet_dc.insert_chart('I4', chart_dc, {'x_offset': 5, 'y_offset': 5})

        # 인지 결과 Sheet
        if len(dsTestID.id_results) > 1:
            worksheet_id = workbook.add_worksheet("Identification")
            row = 0
            m_col = 0 # 메인 시트
            for index, answer, choice_response, is_choice_correct, str_response, is_str_correct \
                    in dsTestID.id_results:
                worksheet_id.write(row, 0, index)
                worksheet_id.write(row, 1, answer)
                worksheet_id.write(row, 2, choice_response)
                worksheet_id.write(row, 3, is_choice_correct)
                row += 1
                # 메인 시트
                worksheet_main.write(30, m_col, index, format_table)
                worksheet_main.write(31, m_col, answer, format_table)
                worksheet_main.write(32, m_col, choice_response, format_table)
                worksheet_main.write(33, m_col, dsUtils.isCorrectToOX(is_choice_correct), format_table)
                m_col += 1
            # 점수 정보 넣기
            worksheet_id.write('F1', dsText.resultText['result_test_identification_title'])
            worksheet_id.write('F2', dsText.resultText['result_test_identification_correct'])
            worksheet_id.write('G2', '=COUNTIF(D:D, 1)')
            worksheet_id.write('F3', dsText.resultText['result_test_identification_incorrect'])
            worksheet_id.write('G3', '=12-G2')
            # 차트 만들기
            chart_id = workbook.add_chart({'type': 'pie'})
            chart_id.add_series({'name': dsText.resultText['result_test_identification_title'],
                              'categories': '=Identification!$F$2:$F$3',
                              'values': '=Identification!$G$2:$G$3',
                              'data_labels': {'value': True, 'percentage': True}
                              })
            chart_id.set_title({'name': dsText.resultText['result_test_identification_title']})
            # chart_id.set_rotation(90)
            chart_id.set_style(10)
            worksheet_id.insert_chart('F4', chart_id, {'x_offset': 5, 'y_offset': 5})

        # 닫기
        workbook.close()

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''




    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Main 함수
if __name__ == '__main__':
    """Main"""
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    # excepthook = sys.excepthook
    # sys.excepthook = lambda t, val, tb: excepthook(t, val, tb)

    # 폰트를 로딩한다.
    # QFontDatabase.addApplicationFont("./ui/font/PAYBOOCBOLD.TTF")
    # app.setFont(QFont("PAYBOOCBOLD"))
    
    # 다이얼로그를 모두 생성한다.
    uiDlg = UiDlg()
    uiDlg.uiDlgStart()
    sys.exit(app.exec())