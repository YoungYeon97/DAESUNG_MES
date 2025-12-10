#-*- coding:utf-8 -*-
from DAESUNG_MES import *

comboStyle_no = "QComboBox::drop-down{width: 0px;}"
comboStyle_25 = "QComboBox::drop-down{background-image: url(./img/dropDown_25.png);}"
comboStyle_30 = "QComboBox::drop-down{background-image: url(./img/dropDown_30.png);}"
#-------------------------------------------------------------------------------------------------------------------------------------------
l_checkStyle = """QCheckBox::indicator{border: 2px solid #c8c8c8; border-radius: 5px; width: 50px; height: 50px; background: #ffffff;}
                  QCheckBox::indicator:checked{border:3px solid #0bc597; background-image: url(./img/check.png); background-repeat: no-repeat; background-position: center;}"""
s_checkStyle = """QCheckBox::indicator{background-position: center; background-repeat: no-reperat;}
                  QCheckBox::indicator:checked{background-image: url(./img/setting_check.png); background-position: center; background-repeat: no-reperat;}"""
t_checkStyle = """QCheckBox::indicator{margin-left: 3px; width:38px; height:38px; background-color: none; border: 3px solid #dcdcdc; border-radius: 5px;}
                  QCheckBox::indicator:checked{border: 3px solid #0bc597; background-image: url(./img/check.png); background-repeat: no-repeat; background-position: center;}"""
#-------------------------------------------------------------------------------------------------------------------------------------------
stateBtnStyle = "background-repeat: no-repeat; background-position: center; border-radius:5px;"
selectBtnStyle = "background: #ffffff; border-bottom: none; color: #3f444a;"
#-------------------------------------------------------------------------------------------------------------------------------------------
tableStyle = """QTableWidget{border: 1px solid #c2c6c9; border-bottom: 2px solid #c2c6c9; gridline-color: #dddddd; background: #ffffff; color:#595b5f; outline: 0; alternate-background-color: #F1F6FD; selection-background-color: rgba(220, 224, 233, 160); selection-color: #383838;}
                QHeaderView::section{height: 50px; color: #3f444a; background: #f1f1f1; border-width: 0px 0px 2px 0px; border-style: solid; border-color: #c2c6c9;}"""
#-------------------------------------------------------------------------------------------------------------------------------------------
calStyle = """QCalendarWidget QToolButton{height: 40px; color: white; font-size: 24px; icon-size: 30px, 30px;}
              QCalendarWidget QMenu{width: 74px; left: 20px; color: white; font-size: 18px; background-color: #3D4B6C;}
              QCalendarWidget QSpinBox{width: 80px; font-size:24px; color: white; background-color: #3D4B6C; selection-background-color: #1C64E8; selection-color: rgb(255, 255, 255);}
              QCalendarWidget QSpinBox::up-button{subcontrol-origin: border; subcontrol-position: top right;  width:50px;}
              QCalendarWidget QSpinBox::down-button{subcontrol-origin: border; subcontrol-position: bottom right;  width:50px;}
              QCalendarWidget QSpinBox::up-arrow{width:40px; height:50px;}
              QCalendarWidget QSpinBox::down-arrow{width:40px; height:50px;}
              QCalendarWidget QWidget{alternate-background-color: #F7F7FA; border: 2px solid #3D5A9D;}
              QCalendarWidget QAbstractItemView{background-color: #F7F7FA; padding: 0px; margin:0px; selection-background-color: #bed4fc; selection-color: #0855e2; font: bold 20px;}
              QCalendarWidget QWidget#qt_calendar_navigationbar{background-color: #3D5A9D; font: bold 28px;}"""

class DaesungFunctions(QDialog):
    def replaceDate(self):
        self.reload_num = 0 #DB실시간 로드 FLAG
        self.s_date = self.date_btn.text().replace(' ', '').replace('-', '') #조회일자
        try:
            self.result_data.setText('')
            self.QR_INPUT.setText('')
            self.LENX_INPUT.setText('')
            self.WIDX_INPUT.setText('')
            self.EDGE_INPUT.setText('')
        except: pass
        try: self.th_rowCount.terminate()
        except: pass
        self.DBload() #DB로드

    def calendar(self):
        if self.calendar_flag == False:
            DaesungFunctions.showCalendar(self)
            self.calendar_flag = True
        elif self.calendar_flag == True:
            self.calender.hide()
            self.calendar_flag = False
    
    def showCalendar(self):
        try:
            s_date = self.date_btn.text().replace(' ', '').replace('-', '')
            YY = int(s_date[:4])
            mm = int(s_date[4:6])
            dd = int(s_date[6:8])
            self.calender = QCalendarWidget(self)
            self.calender.resize(500, 400)
            date = self.calender.selectedDate()
            date.setDate(YY,mm,dd)
            self.calender.setSelectedDate(date)
            self.calender.setVerticalHeaderFormat(0)
            self.calender.clicked[QDate].connect(self.showDate)
            self.calender.move(10, 60)
            self.calender.setFont(QtGui.QFont("맑은 고딕"))
            self.calender.setStyleSheet(calStyle)
            self.calender.show()
        except: pass
    
    #----------------------------------------------------------------------------
    def topData(self):
        self.tableWidget.scrollToTop()
        
    def prevData(self):
        scrollBar = self.tableWidget.verticalScrollBar()
        scrollBar.setValue(scrollBar.value() - scrollBar.pageStep())
        
    def nextData(self):
        scrollBar = self.tableWidget.verticalScrollBar()
        scrollBar.setValue(scrollBar.value() + scrollBar.pageStep())

    def bottomData(self):
        self.tableWidget.scrollToBottom()
    
    #---------------------------------------------------------------------------- 
    def clickable(self, widget, edit):
        class Filter(QObject):
            clicked = pyqtSignal()
            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                                self.clicked.emit()
                                global edit_name
                                edit_name = edit
                                return True
                return False
        filt = Filter(widget)
        widget.installEventFilter(filt)
        return filt.clicked
    
    def clickLogin(self, edit):
        global edit_name
        edit_name = edit
    
    def NumClicked(self, state, button):
        try:
            state = state
            input_num = edit_name.text()
            clicked_num = button.text()
            edit_name.setText(input_num + clicked_num)
        except: pass
    
    def NumDeleted(self):
        try:
            input_num = edit_name.text()
            input_num = input_num[:-1]
            edit_name.setText(input_num)
        except: pass
        
    def openUrl(self):
        url = "https://www.whelper.co.kr/client/main.do"
        webbrowser.open(url)
        
    def closeWindow(self):
        self.close()
    
    #----------------------------------------------------------------------------
    def setStyle(self, flag, wc, proc):
        if flag == 'login':
            self.DB_flag = 0 #DB연결 FLAG
            self.empl_combo.setStyleSheet(comboStyle_30)
            self.wc_combo.setStyleSheet(comboStyle_30)
            self.proc_combo.setStyleSheet(comboStyle_30)
            self.pwd_check.setStyleSheet(l_checkStyle)
        elif flag == 'set':
            if wc == '02':
                self.setFixedSize(1215, 730)
                self.plc_frame.hide()
            else:
                self.printer2_frame.hide()
                self.printer3_frame.hide()
                if proc == '0117' or proc == '0120':
                    self.setFixedSize(1215, 660)
                    self.plc_stackedWidget.setCurrentWidget(self.plc_edge_page)
                elif wc == '09':
                    self.setFixedSize(1215, 660)
                    self.plc_stackedWidget.setCurrentWidget(self.plc_frame_page)
                else:
                    self.setFixedSize(1215, 825)
                    self.plc_stackedWidget.setCurrentWidget(self.plc_cnc_page)
                    self.printer_count_input.hide() 
            self.scanner_check.setStyleSheet(s_checkStyle)
            self.scanner_check2.setStyleSheet(s_checkStyle)
            self.plc_check.setStyleSheet(s_checkStyle)
            self.printer_check.setStyleSheet(s_checkStyle)
            self.printer_mode_check.setStyleSheet(s_checkStyle)
            self.printer_po_check.setStyleSheet(s_checkStyle)
            self.printer2_check.setStyleSheet(s_checkStyle)
            self.printer2_mode_check.setStyleSheet(s_checkStyle)
            self.printer2_po_check.setStyleSheet(s_checkStyle)
            self.printer3_check.setStyleSheet(s_checkStyle)
            self.printer3_mode_check.setStyleSheet(s_checkStyle)
            self.printer3_po_check.setStyleSheet(s_checkStyle)
            self.sensor_check.setStyleSheet(s_checkStyle)
            self.light_check.setStyleSheet(s_checkStyle)
    
    def setComboStyle(self, date, WC_CODE, PROC_CODE, PROC_NAME, PROC):
        self.DB_flag, self.reload_num, self.calendar_flag = 0, 0, False #DB연결 FLAG, DB실시간 로드 FLAG, 달력 열림/닫힘 FLAG
        self.check_flag, self.set_check = False, [] #체크박스 선택 FLAG
        self.ORDER, self.W_DATA = 'MJAKUP.REG_NO', '' #SQL 정렬 구문, SQL WHERE절 구문
        self.state_group = QButtonGroup()
        self.date_btn.setText(date)
        self.c_date = time.strftime('%Y%m%d') #현재일자
        self.tableWidget.setStyleSheet(tableStyle)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.aproc_combo.setStyleSheet(comboStyle_25)
        if PROC != '':
            for i in range(len(PROC)):
                self.aproc_combo.addItem(PROC[i]['PROC_CODE'] + " " + PROC[i]['PROC_NAME'])
                if PROC[i]['PROC_CODE'] == PROC_CODE: index = i
            self.aproc_combo.setCurrentIndex(index)
        else:
            self.aproc_combo.addItem(PROC_CODE + " " + PROC_NAME)
            self.aproc_combo.setEnabled(False)
            self.aproc_combo.setStyleSheet(comboStyle_no)
        #----------------------------------------------------------------
        if WC_CODE == '04':
            self.state2_group = QButtonGroup()
            self.flag_combo.setStyleSheet(comboStyle_25)
            for i in [8, 9]: self.tableWidget.hideColumn(i)
            self.jackup_set_btn.hide()
        elif PROC_CODE != '0120':
            for h in [0, 1, 2]: self.tableWidget.hideColumn(h)
            self.flag_combo.setStyleSheet(comboStyle_25)
            self.tableWidget.hideColumn(9)
            self.tableWidget.hideColumn(10)
            if WC_CODE == '02':
                self.make_array = [QButtonGroup(), QButtonGroup(), QButtonGroup()]
                #self.tableWidget.hideColumn(8)
                self.stackedWidget.setCurrentWidget(self.s_page)
                self.ORDER = 'MJAKUP.REG_DATE DESC, MJAKUP.JAKUP_APPR_TIME DESC' #SQL 정렬 구문
            elif WC_CODE == '19':
                self.stackedWidget.setCurrentWidget(self.s_page)
                self.print_btn.hide()
                self.print_status.hide()
                self.flag_radio.hide()
                self.tableWidget.hideColumn(3)
                self.reload_btn.hide()
            else:
                self.stackedWidget.setCurrentWidget(self.m_page)
                self.flag_radio.hide()
                self.tableWidget.hideColumn(3)
                self.reload_btn.hide()
        else: self.p_data = 0
    
    def setDetailStyle(self, date, WC_CODE, PROC_CODE, GUBUN, LOT, REG_NO):
        self.DB_flag, self.reload_num, self.check_flag = 0, 0, False #DB연결 FLAG, DB실시간 로드 FLAG, 체크박스 선택 FLAG
        self.REG_NO = REG_NO
        if GUBUN == '시판': self.flag = '1'
        else: self.flag = '2'
        self.lot_title.setText("LOT {0} / {1}".format(LOT, GUBUN))
        self.state_group, self.select_group = QButtonGroup(), QButtonGroup()
        self.date_btn.setText(date)
        self.c_date = time.strftime('%Y%m%d') #현재일자
        self.s_date = self.date_btn.text().replace(' ', '').replace('-', '') #조회일자
        self.qty_frame.hide()
        self.tableWidget.setStyleSheet(tableStyle)
        self.tableWidget.horizontalHeader().setVisible(True)
        #----------------------------------------------------------------
        if WC_CODE == '04':
            self.buyer_combo.setStyleSheet(comboStyle_25)
            self.tableWidget.hideColumn(9) #SEQ_QTY
        elif WC_CODE == '05' or WC_CODE == '08' or WC_CODE == '09' or WC_CODE == '16':
            self.prt_group = QButtonGroup()
            self.tableWidget.hideColumn(10) #발행
            self.tableWidget.hideColumn(11) #바코드
        elif WC_CODE == '19':
            for h in [3, 5, 9]: self.tableWidget.hideColumn(h)
        else:
            self.tableWidget.hideColumn(6) #거래처
            self.tableWidget.hideColumn(14) #바코드
            self.t_text = ['심재', '판재', '엣지', '선택', 'SEQ', '납기', '거래처', '품목', '타입', '규격', 'ABS폭', 'ABS길이', '수량', '발행', 'BAR_CODE']
            self.col = ['', '', '', 'CHECK', 'REG_SEQ', 'HOPE_DATE', 'BUYER_NAME', 'ITEM_TEXT', 'SPCL_NAME', 'KYU', 'ABS_LENX', 'ABS_WIDX', 'QTY_NO_ALL', 'PRT_FLAG', 'SEQ_QTY']
            self.label_combo.setStyleSheet(comboStyle_25)
            self.make_array = [QButtonGroup(), QButtonGroup(), QButtonGroup()]
            self.label_flag = 0
            #----------------------------------------------------------------
            if WC_CODE == '02':
                for h in [8, 10, 11]: self.tableWidget.hideColumn(h)
            else:
                for h in [0, 1, 2]: self.tableWidget.hideColumn(h)
                if PROC_CODE == '0103':
                    self.t_text[12] = 'ABS수량'
                    if PROC_CODE == '0103' and WC_CODE == '01': self.label_combo.hide()
                else:
                    for h in [8, 10, 11]: self.tableWidget.hideColumn(h)
                    if PROC_CODE != '0101':
                        self.print_frame.hide()
                        self.label_combo.hide()
                        self.tableWidget.hideColumn(3)
            self.tableWidget.setHorizontalHeaderLabels(self.t_text)
    
    def setAutoStyle(self, date, PROC_CODE, PROC_NAME):
        self.DB_flag, self.reload_num, self.calendar_flag = 0, 0, False #DB연결 FLAG, DB실시간 로드 FLAG, 달력 열림/닫힘 FLAG
        self.state_group = QButtonGroup()
        self.date_btn.setText(date)
        self.c_date = time.strftime('%Y%m%d') #현재일자
        self.tableWidget.setStyleSheet(tableStyle)
        self.tableWidget.horizontalHeader().setVisible(True)
        if PROC_CODE == 'MAKE':
            self.s_flag, self.t_text = 'PACK(A)', '생산된 데이터가 없습니다.'
            self.tableWidget.hideColumn(8)
        else:
            self.aproc_name.setText(PROC_CODE + " " + PROC_NAME)
            if PROC_CODE == '0110' or PROC_CODE == '0115':
                self.c_data, self.r_data = 0, []
                for t in [0, 9, 10]: self.tableWidget.hideColumn(t)
                if PROC_CODE == '0110':
                    self.plc_tableWidget.setStyleSheet(tableStyle)
                    self.plc_tableWidget.hideColumn(2)
                    self.edgeCode_btn.hide()
                elif PROC_CODE == '0115':
                    self.light_btn.hide()
                    self.plc_frame.hide()
                    self.edgeCodeLoad()
            elif PROC_CODE == '0117':
                self.state_group2 = QButtonGroup()
                for t in [self.tableWidget, self.tableWidget2]: t.hideColumn(7)
                
    def setFrameStyle(self, date, PROC_CODE, PROC_NAME):
        self.DB_flag, self.reload_num, self.calendar_flag = 0, 0, False #DB연결 FLAG, DB실시간 로드 FLAG, 달력 열림/닫힘 FLAG
        self.state_group, self.prt_group = QButtonGroup(), QButtonGroup()
        self.date_btn.setText(date)
        self.c_date = time.strftime('%Y%m%d') #현재일자
        self.tableWidget.setStyleSheet(tableStyle)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.aproc_name.setText(PROC_CODE + " " + PROC_NAME)
        #----------------------------------------------------------------
        if PROC_CODE == '0903':
            self.s_date = self.date_btn.text().replace(' ', '').replace('-', '') #조회일자
            self.s_time = time.strftime('%H%M%S') #현재시간
            self.db_seq, self.db_array = ['', '', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '', '']
            self.PLC_btn.hide()
            self.tableWidget.hideColumn(5) #LOTID
            self.tableWidget.setColumnWidth(0, 120) #길리
            self.tableWidget.setColumnWidth(1, 120) #바 너비
            self.tableWidget.setColumnWidth(2, 120) #래치홀
            self.tableWidget.setColumnWidth(3, 120) #보강재
            self.tableWidget.setColumnWidth(4, 160) #구분
            self.tableWidget.setColumnWidth(6, 210) #색상
            self.tableWidget.setColumnWidth(7, 210) #업체명
        else:
            self.check_flag = False #체크박스 선택 FLAG
            self.WIDX, self.W_DATA = '', ''
            self.select_group = QButtonGroup()
            self.widx_combo.setStyleSheet(comboStyle_25)
            self.search_combo.setStyleSheet(comboStyle_25)
            self.tableWidget.hideColumn(9)
    
    #----------------------------------------------------------------------------
    #작업지시서 인쇄
    def jackupPrint(self, wc, proc, lot, empl, flag):
        if (wc == '02' or wc == '03') and proc != '0101': 
            empl = '&EMPL_CODE=%s'%empl
            url = 'http://namuip.com/wood/door_ds/ordr_jakup_master_j.php?e_date={0}&wc_code={1}{2}&proc_code={3}&take_bcode=&lot_numb={4}'.format(self.s_date, wc, empl, proc, lot)
        elif wc == '05' or wc == '08' or wc == '09' or wc == '16':
            url = 'http://namuip.com/wood/door_ds/ordr_jakup_master_f.php?e_date={0}&wc_code={1}&proc_code={2}&take_bcode=&lot_numb={3}&mes_prt_flag_btn={4}'.format(self.s_date, wc, proc, lot, flag)
        elif wc == '04':
            if flag == 'set': url = 'http://namuip.com/wood/door_ds/ordr_jakup_master_m.php?e_date={0}&wc_code={1}&proc_code={2}{3}'.format(self.s_date, '05', '', lot)
            else: url = 'http://namuip.com/wood/door_ds/ordr_jakup_master_m.php?e_date={0}&wc_code={1}&proc_code={2}{3}'.format(self.s_date, wc, '', lot)
        elif wc == '19': url = 'http://namuip.com/wood/door_ds/ordr_jakup_master_if.php?e_date={0}&wc_code={1}&proc_code={2}&take_bcode=&lot_numb={3}'.format(self.s_date, wc, proc, lot)
        else: url = 'http://namuip.com/wood/door_ds/ordr_jakup_master.php?e_date={0}&wc_code={1}&proc_code={2}&take_bcode=&lot_numb={3}'.format(self.s_date, wc, proc, lot)
        webbrowser.open(url)
    
    # Spcl Page -----------------------------------------------------------------      
    def dataListReset(self):
        self.kyus, self.jangb, self.tikxs, self.spcls = [], [], [], []
        self.set1, self.set2 = [], [] #컷팅정보, 남은컷팅정보
        self.janglenx, self.jangwidx = [], []
        self.spclname, self.jangbar = [], []
        self.cutbar, self.setcnt = 0, 0   #컷팅후 자투리, 양방향 상하 컷팅시 카운팅
        self.lwflag, self.set34 = '', ''  #좌우상하구분(1.좌우 2.상하), 셋트마감구분(3.3면 4.4면)

    def datalist(self, j_len, tikx, spcl, jangbar):
        self.janglenx.append(j_len) #장바L
        self.jangwidx.append(tikx) #장바W공
        self.spclname.append(spcl)
        self.jangbar.append(jangbar)
    
    def kyulist(self, set34, lenx, widx, qty):
        for row in range(qty):
            row = row
            if self.qty == 2:
                for i in [lenx, widx]: self.kyus.append(i)
            else:
                for j in [lenx, lenx, widx]: self.kyus.append(j)
                if set34 == 4: self.kyus.append(widx)
            self.kyus.sort()
            
    def setlist1(self, set34, lenx, widx):
        if self.qty == 2:
            for i in [lenx, widx]: self.set1.append(i)
        else:
            for j in [lenx, lenx, widx]: self.set1.append(j)
            if set34 == 4: self.set1.append(widx)
        self.set1.sort()
        
    def setlist2(self, set1):
        self.set2.clear()
        for row in range(len(set1)): self.set2.append(set1[row])
    
    #----------------------------------------------------------------------------
    def tableWidth(self, code, count, len):
        if code == 'LOT':
            if count == '02':
                self.tableWidget.setColumnWidth(6, 540)
                self.tableWidget.setColumnWidth(8, 90)
                if len <= 8:
                    self.tableWidget.setColumnWidth(3, 74)
                    self.tableWidget.setColumnWidth(4, 110)
                    self.tableWidget.setColumnWidth(5, 210)
                    self.tableWidget.setColumnWidth(7, 110)
                else:
                    self.tableWidget.setColumnWidth(3, 70)
                    self.tableWidget.setColumnWidth(4, 100)
                    self.tableWidget.setColumnWidth(5, 200)
                    self.tableWidget.setColumnWidth(7, 100)
            elif count == '04':
                self.tableWidget.setColumnWidth(0, 65)
                self.tableWidget.setColumnWidth(1, 90)
                self.tableWidget.setColumnWidth(2, 165)
                self.tableWidget.setColumnWidth(5, 90)
                self.tableWidget.setColumnWidth(6, 68)
                self.tableWidget.setColumnWidth(7, 60)
                if len <= 8:
                    self.tableWidget.setColumnWidth(3, 320)
                    self.tableWidget.setColumnWidth(4, 290)
                else:
                    self.tableWidget.setColumnWidth(3, 290)
                    self.tableWidget.setColumnWidth(4, 270)
            else:
                self.tableWidget.setColumnWidth(4, 120)
                self.tableWidget.setColumnWidth(6, 579)
                self.tableWidget.setColumnWidth(8, 90)
                if len <= 8:
                    self.tableWidget.setColumnWidth(5, 220)
                    self.tableWidget.setColumnWidth(7, 125)
                else:
                    self.tableWidget.setColumnWidth(5, 205)
                    self.tableWidget.setColumnWidth(7, 110)
        elif code == 'Auto':
            self.tableWidget.setColumnWidth(1, 180)
            self.tableWidget.setColumnWidth(2, 300)
            self.tableWidget.setColumnWidth(3, 200)
            self.tableWidget.setColumnWidth(4, 200)
            self.tableWidget.setColumnWidth(5, 90)
            self.tableWidget.setColumnWidth(6, 94)
            self.tableWidget.setColumnWidth(7, 100)
            self.tableWidget.setColumnWidth(8, 90)
        elif code == 'EDGE':
            self.tableWidget.setColumnWidth(0, 110)
            self.tableWidget.setColumnWidth(1, 185)
            self.tableWidget.setColumnWidth(2, 105)
            self.tableWidget.setColumnWidth(3, 300)
            self.tableWidget.setColumnWidth(4, 250)
            self.tableWidget.setColumnWidth(5, 104)
            self.tableWidget.setColumnWidth(6, 100)
            self.tableWidget.setColumnWidth(8, 100)
            self.tableWidget2.setColumnWidth(0, 110)
            self.tableWidget2.setColumnWidth(1, 185)
            self.tableWidget2.setColumnWidth(2, 105)
            self.tableWidget2.setColumnWidth(3, 300)
            self.tableWidget2.setColumnWidth(4, 250)
            self.tableWidget2.setColumnWidth(5, 104)
            self.tableWidget2.setColumnWidth(6, 100)
            self.tableWidget2.setColumnWidth(8, 100)
        elif count == '19':
            self.tableWidget.setColumnWidth(0, 80)
            self.tableWidget.setColumnWidth(1, 100)
            self.tableWidget.setColumnWidth(2, 100)
            self.tableWidget.setColumnWidth(4, 450)
            self.tableWidget.setColumnWidth(6, 180)
            self.tableWidget.setColumnWidth(7, 120)
            self.tableWidget.setColumnWidth(8, 50)
        elif code.find('PACK') >= 0:
            if code == 'PACK':
                if len <= 7: heix = 95
                else: heix = 83
                self.tableWidget.setColumnWidth(0, 124)
                self.tableWidget.setColumnWidth(1, 205)
                self.tableWidget.setColumnWidth(2, 455)
                self.tableWidget.setColumnWidth(3, heix)
                self.tableWidget.setColumnWidth(4, heix)
                self.tableWidget.setColumnWidth(5, heix)
                self.tableWidget.setColumnWidth(6, heix)
                self.tableWidget.setColumnWidth(7, heix)
            elif code == 'PACK(A)' or code == 'PACK(C)':
                if len <= 7: heix = 95
                else: heix = 82
                self.tableWidget.setColumnWidth(0, 120)
                self.tableWidget.setColumnWidth(1, 190)
                self.tableWidget.setColumnWidth(2, 446)
                self.tableWidget.setColumnWidth(3, heix)
                self.tableWidget.setColumnWidth(4, heix)
                self.tableWidget.setColumnWidth(5, heix)
                self.tableWidget.setColumnWidth(6, heix)
                self.tableWidget.hideColumn(7)
            elif code == 'PACK(P)':
                if len <= 7:
                    self.tableWidget.setColumnWidth(0, 120)
                    self.tableWidget.setColumnWidth(1, 190)
                    self.tableWidget.setColumnWidth(2, 418)
                    self.tableWidget.setColumnWidth(3, 82)
                    self.tableWidget.setColumnWidth(4, 82)
                    self.tableWidget.setColumnWidth(5, 82)
                    self.tableWidget.setColumnWidth(6, 82)
                    self.tableWidget.setColumnWidth(7, 85)
                else:
                    self.tableWidget.setColumnWidth(0, 100)
                    self.tableWidget.setColumnWidth(1, 160)
                    self.tableWidget.setColumnWidth(2, 406)
                    self.tableWidget.setColumnWidth(3, 80)
                    self.tableWidget.setColumnWidth(4, 80)
                    self.tableWidget.setColumnWidth(5, 80)
                    self.tableWidget.setColumnWidth(6, 80)
                    self.tableWidget.setColumnWidth(7, 82)
                self.tableWidget.showColumn(7)
        elif code == 'FRAME':
            if count == 'L':
                self.tableWidget.setColumnWidth(0, 65) #구분
                self.tableWidget.setColumnWidth(4, 510) #품목
                self.tableWidget.setColumnWidth(8, 85) #수량
                if len <= 8:
                    self.tableWidget.setColumnWidth(2, 190) #LOT
                    self.tableWidget.setColumnWidth(11, 78)
                    self.tableWidget.setColumnWidth(12, 78)
                    self.tableWidget.setColumnWidth(13, 78)
                    self.tableWidget.setColumnWidth(14, 78)
                else:
                    self.tableWidget.setColumnWidth(2, 170) #LOT
                    self.tableWidget.setColumnWidth(11, 70)
                    self.tableWidget.setColumnWidth(12, 70)
                    self.tableWidget.setColumnWidth(13, 70)
                    self.tableWidget.setColumnWidth(14, 65)
            else:
                self.tableWidget.setColumnWidth(4, 300) #품목
                self.tableWidget.setColumnWidth(5, 150) #규격
                self.tableWidget.setColumnWidth(8, 75) #수량
                if len <= 8:
                    self.tableWidget.setColumnWidth(2, 180) #LOT-SEQ
                    self.tableWidget.setColumnWidth(3, 200) #거래처
                    self.tableWidget.setColumnWidth(6, 80) #식기유무
                    self.tableWidget.setColumnWidth(7, 160) #색상
                else:
                    self.tableWidget.setColumnWidth(2, 175) #LOT-SEQ
                    self.tableWidget.setColumnWidth(3, 180) #거래처
                    self.tableWidget.setColumnWidth(6, 70) #식기유무
                    self.tableWidget.setColumnWidth(7, 150) #색상
        elif code == 'SPCL':
            self.tableWidget.setColumnWidth(0, 300)
            self.tableWidget.setColumnWidth(1, 150)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)
        elif count == '02':
            self.tableWidget.setColumnWidth(3, 70)
            self.tableWidget.setColumnWidth(12, 100)
            self.tableWidget.setColumnWidth(13, 70)
            if len <= 8:
                self.tableWidget.setColumnWidth(0, 73) #심재
                self.tableWidget.setColumnWidth(1, 73) #판재
                self.tableWidget.setColumnWidth(2, 73) #엣지
                self.tableWidget.setColumnWidth(4, 90)
                self.tableWidget.setColumnWidth(5, 100)
                self.tableWidget.setColumnWidth(7, 300)
                self.tableWidget.setColumnWidth(9, 205)
            else:
                self.tableWidget.setColumnWidth(0, 70) #심재
                self.tableWidget.setColumnWidth(1, 70) #판재
                self.tableWidget.setColumnWidth(2, 70) #엣지
                self.tableWidget.setColumnWidth(4, 85)
                self.tableWidget.setColumnWidth(5, 95)
                self.tableWidget.setColumnWidth(7, 290)
                self.tableWidget.setColumnWidth(9, 180)
        elif code == '0101':
            self.tableWidget.setColumnWidth(3, 75)
            self.tableWidget.setColumnWidth(7, 415)
            self.tableWidget.setColumnWidth(12, 110)
            self.tableWidget.setColumnWidth(13, 75)
            if len <= 8:
                self.tableWidget.setColumnWidth(4, 105)
                self.tableWidget.setColumnWidth(5, 124)
                self.tableWidget.setColumnWidth(9, 225)
            else:
                self.tableWidget.setColumnWidth(4, 100)
                self.tableWidget.setColumnWidth(5, 120)
                self.tableWidget.setColumnWidth(9, 210)
        elif code == '0103':
            self.tableWidget.setColumnWidth(7, 250)
            self.tableWidget.setColumnWidth(8, 120)
            self.tableWidget.setColumnWidth(9, 200)
            if len <= 8:
                self.tableWidget.setColumnWidth(3, 70)
                self.tableWidget.setColumnWidth(4, 85)
                self.tableWidget.setColumnWidth(5, 100)
                self.tableWidget.setColumnWidth(10, 85)
                self.tableWidget.setColumnWidth(11, 85)
                self.tableWidget.setColumnWidth(12, 85)
                self.tableWidget.setColumnWidth(13, 75)
            else:
                self.tableWidget.setColumnWidth(3, 65)
                self.tableWidget.setColumnWidth(4, 80)
                self.tableWidget.setColumnWidth(5, 95)
                self.tableWidget.setColumnWidth(10, 75)
                self.tableWidget.setColumnWidth(11, 75)
                self.tableWidget.setColumnWidth(12, 75)
                self.tableWidget.setColumnWidth(13, 70)
        elif count == '04':
            self.tableWidget.setColumnWidth(0, 70)
            self.tableWidget.setColumnWidth(1, 90)
            self.tableWidget.setColumnWidth(2, 95)
            self.tableWidget.setColumnWidth(5, 120)
            self.tableWidget.setColumnWidth(6, 95)
            self.tableWidget.setColumnWidth(7, 68)
            self.tableWidget.setColumnWidth(8, 60)
            if len <= 8:
                self.tableWidget.setColumnWidth(3, 315)
                self.tableWidget.setColumnWidth(4, 235)
            else:
                self.tableWidget.setColumnWidth(3, 290)
                self.tableWidget.setColumnWidth(4, 210)
        elif count == '05' or count == '08' or count == '09' or count == '16':
            self.tableWidget.setColumnWidth(0, 62) #선택
            self.tableWidget.setColumnWidth(3, 270) #품목
            self.tableWidget.setColumnWidth(4, 150) #타입
            if len <= 8:
                self.tableWidget.setColumnWidth(1, 80) #SEQ
                self.tableWidget.setColumnWidth(2, 175) #거래처
                self.tableWidget.setColumnWidth(5, 145) #규격
                self.tableWidget.setColumnWidth(6, 75) #수량
                self.tableWidget.setColumnWidth(7, 65) #진행
                self.tableWidget.setColumnWidth(8, 65) #진행
                self.tableWidget.setColumnWidth(9, 60) #진행
            else:
                self.tableWidget.setColumnWidth(1, 80) #SEQ
                self.tableWidget.setColumnWidth(2, 155) #거래처
                self.tableWidget.setColumnWidth(5, 130) #규격
                self.tableWidget.setColumnWidth(6, 75) #수량
                self.tableWidget.setColumnWidth(7, 63) #진행
                self.tableWidget.setColumnWidth(8, 63) #진행
                self.tableWidget.setColumnWidth(9, 60) #진행
        else:
            self.tableWidget.setColumnWidth(7, 435)
            self.tableWidget.setColumnWidth(9, 235)
            self.tableWidget.setColumnWidth(13, 75)
            if len <= 8:
                self.tableWidget.setColumnWidth(4, 125)
                self.tableWidget.setColumnWidth(5, 135)
                self.tableWidget.setColumnWidth(12, 124)
            else:
                self.tableWidget.setColumnWidth(4, 110)
                self.tableWidget.setColumnWidth(5, 120)
                self.tableWidget.setColumnWidth(12, 110)

