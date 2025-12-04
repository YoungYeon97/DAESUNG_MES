#-*- coding:utf-8 -*-
from DAESUNG_MES import *

COMP_CODE = '001'

#SQL Column명으로 가져위한 함수
def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]
    def createRow(*args):
        return dict(zip(columnNames, args))
    return createRow

#DB연결 해제
def closeDB():
    try:
        cursor_item.close()
        logging.debug("closeDB : DB(cursor_item) 연결해제 성공")
    except: logging.debug("closeDB : DB(cursor_item) 연결해제 실패")
    try:
        db.close()
        logging.debug("closeDB : DB 연결해제 성공")
    except: logging.debug("closeDB : DB 연결해제 실패")

class DaesungQuery(QDialog):
    
    #DB연결
    def connectDB(self, host, port, User, name):
        global db, cursor_item
        try: db.close()
        except: pass
        try:
            db = pymysql.connect(host=host, port=port, user=User, password="doorerp1!", db = name, charset = 'utf8', cursorclass = pymysql.cursors.DictCursor)
            cursor_item = db.cursor()
            flag = "success"
        except: flag = "failed"
        
        return flag
    
    def DBCommit(self):
        try:
            db.commit()
            result = 1
        except:
            db.rollback()
            result = 2
            
        return result
    
    #작업자 조회
    def selectEmpl(self):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT EMPL.EMPL_CODE, EMPL.EMPL_NAME
            FROM((BA_EMPL EMPL INNER JOIN BA_DEPT DEPT ON EMPL.COMP_CODE = DEPT.COMP_CODE AND EMPL.DEPT_CODE = DEPT.DEPT_CODE)
                  LEFT OUTER JOIN  BA_LESS LESS ON EMPL.COMP_CODE = LESS.COMP_CODE AND EMPL.DEPT_CODE = LESS.DEPT_CODE AND EMPL.LESS_CODE = LESS.LESS_CODE)
            WHERE EMPL.COMP_CODE = '{COMP_CODE}'
              AND EMPL.DEPT_CODE LIKE '%'
              AND EMPL.MES_PASS_WORD IS NOT NULL
              AND EMPL.OUT_FLAG LIKE '%0'""".format(COMP_CODE = COMP_CODE)
            cursor_item.execute(sql_item)
            E_rows = cursor_item.fetchall()
        except: E_rows = 'failed'
            
        return E_rows
    
    #작업장 조회
    def selectWc(self, EMPL_CODE):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT DISTINCT PROC.WC_CODE, WC.WC_NAME, EP.EMPL_CODE
            FROM ((BP_PROC PROC INNER JOIN BP_WC WC ON PROC.WC_CODE = WC.WC_CODE) 
                  INNER JOIN BA_EMPL_PROC EP ON PROC.PROC_CODE = EP.PROC_CODE AND EP.EMPL_CODE = '{EMPL_CODE}')
            WHERE PROC.USED_FLAG = '1'
              AND EP.EMPL_CODE = '{EMPL_CODE}'""".format(EMPL_CODE = EMPL_CODE)
            cursor_item.execute(sql_item)
            W_rows = cursor_item.fetchall()
        except: W_rows = 'failed'
    
        return W_rows
    
    #공정 조회
    def selectProc(self, EMPL_CODE, WC_CODE, PROC_CODE):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT PROC.PROC_CODE, PROC.PROC_NAME, EP.EMPL_CODE
            FROM ((BP_PROC PROC INNER JOIN BP_WC WC ON PROC.WC_CODE = WC.WC_CODE) 
                  INNER JOIN BA_EMPL_PROC EP ON PROC.PROC_CODE = EP.PROC_CODE AND EP.EMPL_CODE = '{EMPL_CODE}')
            WHERE PROC.USED_FLAG = '1'
              AND EP.EMPL_CODE = '{EMPL_CODE}'
              AND PROC.WC_CODE LIKE '{WC_CODE}'
              {PROC_CODE}""".format(EMPL_CODE = EMPL_CODE, WC_CODE = WC_CODE, PROC_CODE = PROC_CODE)
            cursor_item.execute(sql_item)
            P_rows = cursor_item.fetchall()
        except: P_rows = 'failed'
    
        return P_rows
    
    def checkPassword(self, EMPL_CODE, MES_PASS_WORD):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT COMP.HEAD_BRAN_FLAG, COMP.COMP_CODE, COMP.COMP_NAME, COMP.COMP_NUMB, COMP.MAIL_ADDR, COMP.TEL_NUMB, COMP.FAX_NUMB, COMP.DESIGN_COLOR, 
                   DEPT.DEPT_CODE, DEPT.DEPT_NAME, LESS.LESS_CODE, LESS.LESS_NAME, 
                   EMPL.EMPL_CODE, EMPL.EMPL_NAME, NVL(EMPL.OUT_FLAG, '0') OUT_FLAG, NVL(EMPL.ADMIN_FLAG, '0')  ADMIN_FLAG
            FROM(((BA_EMPL EMPL INNER JOIN BA_COMP COMP ON EMPL.COMP_CODE = COMP.COMP_CODE) 
                    LEFT OUTER JOIN BA_DEPT DEPT ON EMPL.COMP_CODE = DEPT.COMP_CODE AND EMPL.DEPT_CODE = DEPT.DEPT_CODE) 
                    LEFT OUTER JOIN BA_LESS LESS ON EMPL.COMP_CODE = LESS.COMP_CODE AND EMPL.DEPT_CODE = LESS.DEPT_CODE AND EMPL.LESS_CODE = LESS.LESS_CODE) 
            WHERE EMPL.EMPL_CODE = '{EMPL_CODE}'
              AND EMPL.MES_PASS_WORD = '{MES_PASS_WORD}'""".format(EMPL_CODE = EMPL_CODE, MES_PASS_WORD = MES_PASS_WORD)
            cursor_item.execute(sql_item)
            PWD = cursor_item.fetchall()
        except: PWD = 'failed'
    
        return PWD
    
    def selectConnBigo(self, REG_NO, REG_SEQ):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT FN_CONN_CPROC_NAME_BIGO('JAKUP', '{COMP_CODE}', '{REG_NO}', '{REG_SEQ}') CONN_CPROC_NAME_BIGO FROM AA_DUAL
        """.format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ)
        cursor_item.execute(sql_item)
        PWD = cursor_item.fetchall()

        return PWD
    
    #LOT/DETAIL #####################################################################################################################
    #LOT > LOT COUNT 조회
    def selectLotCount(self, PROC_CODE, s_date, PRT_FLAG, JAKUP_APPR_FLAG, W_DATA):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MAX(MJAKUP.JAKUP_APPR_TIME) JAKUP_APPR_TIME
        FROM((((
            FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                    LEFT OUTER JOIN BC_ITEM ITEM_MA ON ITEM_MA.ITEM_LEVEL = 2 AND MJAKUP.ITEM_LA_CODE = ITEM_MA.ITEM_LA_CODE AND MJAKUP.ITEM_MA_CODE = ITEM_MA.ITEM_MA_CODE)
                    INNER JOIN FD_JAKUP_MASTER_PROC MPJAKUP ON MJAKUP.COMP_CODE = MPJAKUP.COMP_CODE AND MJAKUP.REG_NO = MPJAKUP.REG_NO AND {PROC_CODE})
                    INNER JOIN (SELECT COMP_CODE, REG_NO, CASE MIN(PRT_FLAG) WHEN '0' THEN IF(MAX(PRT_FLAG) = '0', '0', '2') ELSE '1' END LK_PRT_FLAG
                                FROM FD_JAKUP_BAR_CODE
                                WHERE COMP_CODE = '{COMP_CODE}'
                                GROUP BY COMP_CODE, REG_NO) BJAKUP ON MJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND MJAKUP.REG_NO = BJAKUP.REG_NO)
        WHERE DJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.HOPE_DATE BETWEEN  '{s_date}' AND '{s_date}'
          AND MJAKUP.JAKUP_APPR_FLAG LIKE '{JAKUP_APPR_FLAG}'  /*지시승인 */
          AND BJAKUP.LK_PRT_FLAG LIKE '{PRT_FLAG}'
          {W_DATA}
        GROUP BY MJAKUP.COMP_CODE, MJAKUP.REG_NO, MJAKUP.LOT_NUMB
        ORDER BY JAKUP_APPR_TIME DESC""".format(COMP_CODE = COMP_CODE, PROC_CODE = PROC_CODE, s_date = s_date, PRT_FLAG = PRT_FLAG, JAKUP_APPR_FLAG = JAKUP_APPR_FLAG, W_DATA = W_DATA)
        cursor_item.execute(sql_item)
        LC_rows = cursor_item.fetchall()
    
        return LC_rows
    
    #LOT > LOT 리스트 조회
    def selectLotList(self, PROC_CODE, s_date, PRT_FLAG, JAKUP_APPR_FLAG, ORDER, W_DATA):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                MJAKUP.LK_MAKE_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO) ITEM_TEXT,
                SUM(DJAKUP.QTY) QTY,
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG,
                MJAKUP.JAKUP_APPR_TIME
            FROM((((
                FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                        LEFT OUTER JOIN BC_ITEM ITEM_MA ON ITEM_MA.ITEM_LEVEL = 2 AND MJAKUP.ITEM_LA_CODE = ITEM_MA.ITEM_LA_CODE AND MJAKUP.ITEM_MA_CODE = ITEM_MA.ITEM_MA_CODE)
                        INNER JOIN FD_JAKUP_MASTER_PROC MPJAKUP ON MJAKUP.COMP_CODE = MPJAKUP.COMP_CODE AND MJAKUP.REG_NO = MPJAKUP.REG_NO AND {PROC_CODE})
                        INNER JOIN (SELECT COMP_CODE, REG_NO, CASE MIN(PRT_FLAG) WHEN '0' THEN IF(MAX(PRT_FLAG) = '0', '0', '2') ELSE '1' END LK_PRT_FLAG
                                    FROM FD_JAKUP_BAR_CODE
                                    WHERE COMP_CODE = '{COMP_CODE}'
                                    GROUP BY COMP_CODE, REG_NO) BJAKUP ON MJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND MJAKUP.REG_NO = BJAKUP.REG_NO)
            WHERE DJAKUP.COMP_CODE = '{COMP_CODE}'
              AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
              AND MJAKUP.JAKUP_APPR_FLAG LIKE '{JAKUP_APPR_FLAG}'  /*지시승인 */
              AND BJAKUP.LK_PRT_FLAG LIKE '{PRT_FLAG}'
              {W_DATA}
            GROUP BY MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO),
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG,
                MJAKUP.JAKUP_APPR_TIME
            ORDER BY {ORDER}""".format(COMP_CODE = COMP_CODE, PROC_CODE = PROC_CODE, s_date = s_date, PRT_FLAG = PRT_FLAG, JAKUP_APPR_FLAG = JAKUP_APPR_FLAG, ORDER = ORDER, W_DATA = W_DATA)
            print(sql_item)
            cursor_item.execute(sql_item)
            S_rows = cursor_item.fetchall()
        except: S_rows = 'failed'
        
        return S_rows
    
    #DETAIL > DETAIL 리스트 조회
    def selectDetailList(self, REG_NO, REG_SEQ, SEQ_QTY, s_date, PROC_CODE, ORDER):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.REG_NO,
                MJAKUP.REG_DATE,
                MJAKUP.JAKUP_FLAG,
                MJAKUP.LOT_NUMB,
                DJAKUP.REG_SEQ,
                PJAKUP.SORT_KEY,
                DJAKUP.MES_PRT_FLAG,
                DJAKUP.HOPE_DATE,  /*희낭납기일*/
                DJAKUP.KYU,
                DJAKUP.LENX,
                DJAKUP.WIDX,
                DJAKUP.TIKX,
                DJAKUP.ABS_LENX,
                DJAKUP.ABS_WIDX,
                DJAKUP.ABS_QTY,
                DJAKUP.QTY,
                DJAKUP.HOLE_FLAG,
                DJAKUP.HOLE_VALUE,
                DJAKUP.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                CASE WHEN DJAKUP.EDGE_FLAG = '1' THEN '일면'
                     WHEN DJAKUP.EDGE_FLAG = '2' THEN '일면2'
                     WHEN DJAKUP.EDGE_FLAG = '3' THEN '양면' 
                     ELSE '-' END AS EDGE_NAME,
                DJAKUP.CONN_CPROC_NAME,
                DJAKUP.SET_FLAG,
                DJAKUP.CPROC_BIGO,
                DJAKUP.LABEL_BIGO,
                DJAKUP.BIGO,
                CONCAT(FORMAT(ROW_NUMBER() OVER (PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ ORDER BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ, BJAKUP.SEQ_QTY), 0), '/',
                FORMAT(COUNT(1) OVER(PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ), 0)) QTY_NO_ALL,  /*수량텍스트*/
                BJAKUP.SEQ_QTY,
                BJAKUP.PRT_FLAG,  /*출력유무*/
                ITEM.ITEM_MA_NAME,
                ITEM.ITEM_NAME,
                CONCAT(ITEM.ITEM_MA_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
                SPCL.SPCL_NAME,
                GLAS.GLAS_NAME,
                TRANS.TRANS_FLAG_NAME,
                BUYER.BUYER_NAME,
                BJAKUP.BAR_CODE,
                IF(IFNULL(DORDR.FSET_SEQ, '') = '', '일반품', 'SET') FSET_FLAG_NAME,
                (SELECT IFNULL((SELECT BAR_CODE FROM FG_MAKE_BAR_CODE WHERE PROC_CODE = '{PROC_CODE}' AND BAR_CODE = BJAKUP.BAR_CODE LIMIT 1), '0') AS BAR_CODE
                FROM FG_MAKE_BAR_CODE LIMIT 1) AS BAR_FLAG,
                PMAKE.PROC_CODE P_PROC_CODE,
                PMAKE.LK_MAKE_FLAG P_LK_MAKE_FLAG,
                CASE WHEN INSTR(ITEM.ITEM_NAME,'행거') > 0 OR INSTR(ITEM.ITEM_NAME,'후시마') > 0 THEN 'Y' ELSE 'N' END BT_YN, /* 하부옵션Y = H바에 -35해서 컷팅*/
                CASE WHEN 
                INSTR(ITEM.ITEM_NAME,'행거')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '326') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '327') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '328') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '375')
                > 0 THEN  'Y' ELSE 'N' END DR1_YN, /* 보강규칙 #1 행거용 (5) */
                
                CASE WHEN 
                INSTR(ITEM.ITEM_NAME,'후시마')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '051')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '067') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '229') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '378') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '379') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '382') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '383')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '427')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '428')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '444')
                > 0 THEN  'Y' ELSE 'N' END DR3_YN, /* 보강규칙 #3 후시마 (10) */
                    
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '048')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '049') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '453') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '454') 
                > 0 THEN  'Y' ELSE 'N' END DR4_YN, /* 보강규칙 #4 윈드컷 (4) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '043')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '400') 
                > 0 THEN  'Y' ELSE 'N' END DR5_YN, /* 보강규칙 #5 도어체크 (2) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '102')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '103') 
                > 0 THEN  'Y' ELSE 'N' END DR6_YN, /* 보강규칙 #6 바람막이 (2) */
                
                CASE WHEN 
                (CASE WHEN DJAKUP.LENX >= 2400 THEN 1 ELSE 0 END)   /* 길이 2400이상 */
                + (CASE WHEN DJAKUP.WIDX >= 1200 THEN 1 ELSE 0 END)   /* 폭 1200이상 */
                + INSTR(DJAKUP.CONN_CPROC_CODE, '039')
                > 0 THEN  'Y' ELSE 'N' END DR7_YN, /* 보강규칙 #7 4면보강 (1)*/
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '405')
                > 0 THEN  'Y' ELSE 'N' END DR8_YN, /* 보강규칙 #8 2면보강(=상하보강) (1) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '053')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '054')
                > 0 THEN  'Y' ELSE 'N' END DR9_YN, /* 보강규칙 #9 노출행거 (2) */
                
                CASE WHEN 
                -- (CASE WHEN DJAKUP.LENX >= 1970 THEN 1 ELSE 0 END)   /* 길이 1970이상 */
                CASE WHEN IFNULL(DJAKUP.CAL_HOLE_VALUE, 0) = 0 THEN 0
                 ELSE (CASE WHEN DJAKUP.CAL_HOLE_VALUE > (DJAKUP.LENX/2)+150 OR DJAKUP.CAL_HOLE_VALUE < (DJAKUP.LENX/2)-150 THEN 1 ELSE 0 END) END /* 상부값+150||-150외 범위 */ 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '040')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '628') /*1면보강(다대L33)*/
                > 0 THEN  'Y' ELSE 'N' END DR10_YN, /* 보강규칙 #10 일자손잡이보강 (1)*/
                    
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '042')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '050') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '093') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '094') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '096') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '274') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '276') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '278') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '457') 
                > 0 THEN  'Y' ELSE 'N' END DR11_YN, /* 보강규칙 #11 모티스레버 (9) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '109')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '445') 
                > 0 THEN  'Y' ELSE 'N' END DR12_YN, /* 보강규칙 #12 현관보조 잠금장치작업 (2) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '114')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '115') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '118') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '119') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '120')     
                + INSTR(DJAKUP.CONN_CPROC_CODE, '121') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '122') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '123') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '124') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '125') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '224')     
                + INSTR(DJAKUP.CONN_CPROC_CODE, '225') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '226')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '322') 
                + INSTR(DJAKUP.CONN_CPROC_CODE, '325')
                > 0 THEN  'Y' ELSE 'N' END DR13_YN, /* 보강규칙 #13 미서기잠금 (17) */
                    
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '407')
                > 0 THEN  'Y' ELSE 'N' END DR14_YN, /* 보강규칙 #14 보조잠금장치 (1) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '041')
                > 0 THEN  'Y' ELSE 'N' END DR15_YN, /* 보강규칙 #15 전자키보강 (1) */
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '075')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '206')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '429')
                > 0 THEN  'Y' ELSE 'N' END DR16_YN, /* 보강규칙 #16 연동호차 (3)*/
                
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '045')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '046')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '047')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '181')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '182')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '183')
                > 0 THEN  'Y' ELSE 'N' END DR17_YN, /* 보강규칙 #17 오도시 (6) */
                
                CASE WHEN 
                (CASE WHEN DJAKUP.TIKX = 45 THEN 1 ELSE 0 END) /* 규격-두께값 45mm */
                + INSTR(DJAKUP.CONN_CPROC_CODE, '003')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '297')
                > 0 THEN  'Y' ELSE 'N' END DR18_YN, /* 보강규칙 #18 두께 45mm (2) */
                
                CASE WHEN 
                INSTR(ITEM.ITEM_NAME,'히든')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '081')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '082')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '083')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '084')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '085')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '221')
                + INSTR(DJAKUP.CONN_CPROC_CODE, '447')
                > 0 THEN  'Y' ELSE 'N' END DR19_YN, /* 보강규칙 #19 히든도어 (7) */
                    
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '252') /* 좌우보강 */
                + INSTR(DJAKUP.CONN_CPROC_CODE, '627') /* 2면보강(다대 L33)) */
                > 0 THEN  'Y' ELSE 'N' END DR20_YN, /* 보강규칙 #20 좌우손잡이보강 (1) */
                    
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '363')  /* [ 363 손잡이타카고정(X) ] = 중앙타카N */
                > 0 THEN  'N' ELSE 'Y' END TK_YN, /* 그외 조건 - 중앙타카유무 */
                
                CASE WHEN
                INSTR(DJAKUP.CONN_CPROC_CODE, '108') /* [ 108 상부요꼬자석매립 ] = 수동보강Y */
                > 0 THEN 'Y' ELSE 'N' END MN_YN,  /* 그외 조건 - 수동보강유무 */
                    
                /* CASE WHEN DJAKUP.WIDX > 1220 || DJAKUP.LENX > 2420 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END NO_YN /* 작업불가 사이즈 */
                
                /* 시트지컬러유무 N(필름X,백골) Y(필름O) */     
                CASE WHEN      
                    (CASE WHEN
                        (CASE WHEN DJAKUP.CONN_CPROC_CODE = '' THEN 1 ELSE 0 END)
                        + INSTR(SPCL.SPCL_CODE, '177')
                     + INSTR(SPCL.SPCL_CODE, '373')        
                        + INSTR(SPCL.SPCL_CODE, '977')
                     + INSTR(SPCL.SPCL_CODE, '877')    
                        + INSTR(SPCL.SPCL_CODE, 'A77')
                     + INSTR(SPCL.SPCL_CODE, '277')                        
                     > 0 THEN  'N' ELSE 'Y' END) = 'N' THEN
                     CASE WHEN DJAKUP.WIDX > 1260 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름X,백골 */
                 ELSE
                     CASE WHEN DJAKUP.WIDX > 1220 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름O */
                 END NO_YN
                    
        FROM((((((((((
            FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                    INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
                    LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
                    LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                    LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                    LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
                    LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                    INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON DJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND DJAKUP.REG_NO = BJAKUP.REG_NO AND DJAKUP.REG_SEQ = BJAKUP.REG_SEQ)
                    LEFT OUTER JOIN DD_ORDR_DETAIL DORDR ON DJAKUP.COMP_CODE = DORDR.COMP_CODE AND DJAKUP.LK_ORDR_NO = DORDR.REG_NO AND DJAKUP.LK_ORDR_SEQ = DORDR.REG_SEQ)
                    INNER JOIN (SELECT PJAKUP.COMP_CODE,
                                     PJAKUP.REG_NO,
                                     PJAKUP.REG_SEQ,
                                     PJAKUP.SORT_KEY,
                                     PJAKUP.END_PROC_FLAG,
                                     PJAKUP.LK_PUT_FLAG,
                                     PJAKUP.LK_PUT_QTY,
                                     PJAKUP.LK_MAKE_QTY,
                                     PJAKUP.LK_MAKE_DATE,
                                     GROUP_CONCAT(PJAKUP.PROC_CODE ORDER BY PJAKUP.PROC_CODE) AS PROC_CODE,
                                     GROUP_CONCAT(PJAKUP.LK_MAKE_FLAG ORDER BY PJAKUP.PROC_CODE) AS LK_MAKE_FLAG,
                                     GROUP_CONCAT(PROC.PROC_NAME) AS PROC_NAME
                                FROM FD_JAKUP_PROC PJAKUP LEFT OUTER JOIN BP_PROC PROC ON PJAKUP.PROC_CODE = PROC.PROC_CODE
                               WHERE PJAKUP.COMP_CODE = '{COMP_CODE}'
                                 AND PJAKUP.REG_NO LIKE '{REG_NO}'
                                 AND PJAKUP.REG_SEQ LIKE '{REG_SEQ}'
                            GROUP BY PJAKUP.REG_SEQ
                            ORDER BY PJAKUP.COMP_CODE, PJAKUP.REG_NO, PJAKUP.REG_SEQ, PJAKUP.SORT_KEY) PMAKE on MJAKUP.COMP_CODE = PMAKE.COMP_CODE AND MJAKUP.REG_NO = PMAKE.REG_NO and DJAKUP.REG_SEQ = PMAKE.REG_SEQ)
        WHERE DJAKUP.JAKUP_APPR_FLAG ='2'   /*작업지시승인유무 0.대기 2.승인 9.취소*/
          AND DJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.REG_NO LIKE '{REG_NO}'
          AND DJAKUP.REG_SEQ LIKE '{REG_SEQ}'
          AND BJAKUP.SEQ_QTY LIKE '{SEQ_QTY}'
          AND DJAKUP.HOPE_DATE = '{s_date}'
          AND PJAKUP.PROC_CODE = '{PROC_CODE}'
        ORDER BY {ORDER} DJAKUP.REG_NO, DJAKUP.REG_SEQ, BJAKUP.SEQ_QTY
        """.format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ, SEQ_QTY = SEQ_QTY, s_date = s_date, PROC_CODE = PROC_CODE, ORDER = ORDER)
        cursor_item.execute(sql_item)
        D_rows = cursor_item.fetchall()
        
        return D_rows
    
    #DETAIL > DETAIL 개별전표 조회
    def selectDetailItem(self, DATE, LOT_NUMB, REG_NO, REG_SEQ):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT  MJAKUP.REG_NO,
                DJAKUP.REG_SEQ,
                MJAKUP.LOT_NUMB,
                ITEM.ITEM_NAME,
                DJAKUP.KYU,
                DJAKUP.LENX,
                DJAKUP.WIDX,
                DJAKUP.QTY,
                PJAKUP.LK_MAKE_QTY,
                SPCL.SPCL_CODE,
                DPUT.ITEM_CODE DITEM_CODE,
                DPUT.TIKX,
                BITEM.ITEM_NAME DITEM_NAME
        FROM (((((((
              FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
              INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
              LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
              LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
              LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
              LEFT OUTER JOIN FF_PUT_DETAIL DPUT ON DJAKUP.REG_NO = DPUT.LK_JAKUP_NO AND DJAKUP.REG_SEQ = DPUT.LK_JAKUP_SEQ)      
              LEFT OUTER JOIN BC_ITEM BITEM ON DPUT.ITEM_CODE = BITEM.ITEM_CODE)
        WHERE MJAKUP.COMP_CODE = '001'
          AND IFNULL(MJAKUP.JAKUP_APPR_FLAG, '%') LIKE '2' /* 지시승인유무 2.승인 */
          AND DJAKUP.HOPE_DATE = '{DATE}'
          AND MJAKUP.ITEM_LA_CODE IN ('04', '16')
          AND MJAKUP.LOT_NUMB LIKE '{LOT_NUMB}'
          AND MJAKUP.REG_NO LIKE '{REG_NO}'
          AND DJAKUP.REG_SEQ LIKE '{REG_SEQ}'
          AND (CASE WHEN (CASE WHEN (CASE WHEN DJAKUP.CONN_CPROC_CODE = '' THEN 1 ELSE 0 END)
                                                    + INSTR(SPCL.SPCL_CODE, '177')
                                                    + INSTR(SPCL.SPCL_CODE, '373')        
                                                    + INSTR(SPCL.SPCL_CODE, '977')
                                                    + INSTR(SPCL.SPCL_CODE, '877')    
                                                    + INSTR(SPCL.SPCL_CODE, 'A77')
                                                    + INSTR(SPCL.SPCL_CODE, '277') > 0 THEN  'N' ELSE 'Y' END) = 'N'                
                        THEN CASE WHEN DJAKUP.WIDX > 1260 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름X,백골 */
                        ELSE CASE WHEN DJAKUP.WIDX > 1220 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름O */
                        END) = 'N'
          AND INSTR(DJAKUP.CONN_CPROC_CODE, '003') < 1
          AND PJAKUP.PROC_CODE LIKE '0101'
          AND (BITEM.ITEM_NAME LIKE '%신형 사각바%' OR BITEM.ITEM_CODE LIKE '1700%') /*BOM 사각바*/
          AND DPUT.TIKX <> '42' /*구형사각바 42 자동공정 제외*/
        ORDER BY DJAKUP.WIDX, DJAKUP.LENX""".format(DATE = DATE, LOT_NUMB = LOT_NUMB, REG_NO = REG_NO, REG_SEQ = REG_SEQ)
        cursor_item.execute(sql_item)
        I_rows = cursor_item.fetchall()
    
        return I_rows
    
    #자동화(접착, 테노너) #################################################################################################################
    #자동화(접착, 테노너) > 메인 리스트 조회
    def selectAutoList(self, PROC_CODE, MES_FLAG, s_date):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT BMAKE.COMP_CODE,
                BMAKE.REG_NO,
                BMAKE.REG_SEQ,
                BMAKE.MES_SEQ, /*순번*/
                DMAKE.LK_JAKUP_NO,
                DMAKE.LK_JAKUP_SEQ,
                DMAKE.LOT_NUMB,
                DMAKE.LENX,
                DMAKE.WIDX,
                BMAKE.QTY,
                DMAKE.HOLE_VALUE,
                DMAKE.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                DMAKE.EDGE_FLAG,
                CASE WHEN DMAKE.EDGE_FLAG = '1' THEN '일면'
                     WHEN DMAKE.EDGE_FLAG = '2' THEN '일면2'
                     WHEN DMAKE.EDGE_FLAG = '3' THEN '양면' 
                     ELSE '-' END AS EDGE_NAME,
                CONCAT(ITEM.ITEM_MA_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
                SPCL.SPCL_NAME,
                BJAKUP.MES_FLAG,
                BMAKE.BAR_CODE,
                SJAKUP.SEQ
            FROM(((((
                FG_MAKE_BAR_CODE BMAKE INNER JOIN FG_MAKE_DETAIL DMAKE ON BMAKE.COMP_CODE = DMAKE.COMP_CODE AND BMAKE.REG_NO = DMAKE.REG_NO AND BMAKE.REG_SEQ = DMAKE.REG_SEQ)
                        INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON BMAKE.BAR_CODE = BJAKUP.BAR_CODE)
                        LEFT OUTER JOIN BC_ITEM ITEM ON DMAKE.ITEM_CODE = ITEM.ITEM_CODE)
                        LEFT OUTER JOIN BC_SPCL SPCL ON DMAKE.SPCL_CODE = SPCL.SPCL_CODE)
                        INNER JOIN fd_jakup_seq SJAKUP ON BMAKE.BAR_CODE = SJAKUP.BAR_CODE)
            WHERE BMAKE.COMP_CODE = '{COMP_CODE}'
              AND SJAKUP.MES_FLAG = '{MES_FLAG}'
              AND BMAKE.REG_DATE = '{s_date}'
              AND BMAKE.PROC_CODE = '{PROC_CODE}'
              AND BMAKE.BAR_CODE LIKE '%'
              AND BMAKE.BADN_QTY = '0'
            ORDER BY BMAKE.MES_SEQ DESC
            LIMIT 3""".format(COMP_CODE = COMP_CODE, MES_FLAG = MES_FLAG, s_date = s_date, PROC_CODE = PROC_CODE)
            cursor_item.execute(sql_item)
            A_rows = cursor_item.fetchall()
        except: A_rows = 'failed'

        return A_rows
    
    #자동화(엣지) #######################################################################################################################
    #자동화(엣지) > 메인 리스트 조회
    def selectAutoEdgeList(self, MES_FLAG, s_date, BAR_CODE, PUT_FLAG, LIMIT):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT BMAKE.COMP_CODE,
                BMAKE.REG_NO,
                BMAKE.REG_SEQ,
                SJAKUP.SEQ,
                DMAKE.LK_JAKUP_NO,
                DMAKE.LK_JAKUP_SEQ,
                DMAKE.LOT_NUMB,
                DMAKE.HOLE_FLAG,
                DMAKE.HOLE_VALUE,
                DMAKE.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                DMAKE.EDGE_FLAG,
                CASE WHEN DMAKE.EDGE_FLAG = '1' THEN '일면'
                     WHEN DMAKE.EDGE_FLAG = '2' THEN '일면2'
                     WHEN DMAKE.EDGE_FLAG = '3' THEN '양면' 
                     ELSE '-' END AS EDGE_NAME,
                DMAKE.CONN_CPROC_CODE,
                CONCAT(ITEM.ITEM_NAME, '/', DMAKE.KYU) ITEM_TEXT,
                SPCL.SPCL_CODE,
                SPCL.SPCL_NAME,
                BUYER.BUYER_NAME,
                CASE WHEN SJAKUP.PUT_FLAG = '1' THEN '대기'
                     WHEN SJAKUP.PUT_FLAG = '2' THEN '진행'
                     WHEN SJAKUP.PUT_FLAG = '3' THEN '대기' 
                     WHEN SJAKUP.PUT_FLAG = '4' THEN '진행' 
                     ELSE '통과' END AS PUT_FLAG,
                SJAKUP.BAR_CODE
            FROM ((((((
               FG_MAKE_BAR_CODE BMAKE INNER JOIN FG_MAKE_DETAIL DMAKE ON BMAKE.COMP_CODE = DMAKE.COMP_CODE AND BMAKE.REG_NO = DMAKE.REG_NO AND BMAKE.REG_SEQ = DMAKE.REG_SEQ)
                       INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON BMAKE.BAR_CODE = BJAKUP.BAR_CODE)
                       INNER JOIN FD_JAKUP_SEQ SJAKUP ON BJAKUP.BAR_CODE = SJAKUP.BAR_CODE)
                       LEFT OUTER JOIN BC_ITEM ITEM ON DMAKE.ITEM_CODE = ITEM.ITEM_CODE)
                       LEFT OUTER JOIN BC_SPCL SPCL ON DMAKE.SPCL_CODE = SPCL.SPCL_CODE)
                       LEFT OUTER JOIN BE_BUYER BUYER ON DMAKE.BUYER_CODE = BUYER.BUYER_CODE)
            WHERE BMAKE.COMP_CODE = '{COMP_CODE}'
              AND SJAKUP.MES_FLAG = '{MES_FLAG}'
              AND BMAKE.REG_DATE = '{s_date}'
              AND BMAKE.PROC_CODE = '0117'
              AND BMAKE.BAR_CODE LIKE '{BAR_CODE}'
              AND BMAKE.BADN_QTY = '0'
              AND SJAKUP.PUT_FLAG IN ({PUT_FLAG})
            ORDER BY SJAKUP.PUT_FLAG, BMAKE.MES_SEQ DESC
            {LIMIT}""".format(COMP_CODE = COMP_CODE, MES_FLAG = MES_FLAG, s_date = s_date, BAR_CODE = BAR_CODE, PUT_FLAG = PUT_FLAG, LIMIT = LIMIT)
            cursor_item.execute(sql_item)
            A_rows = cursor_item.fetchall()
        except: A_rows = 'failed'
    
        return A_rows
    
    #포장검수 ##########################################################################################################################
    #포장검수 > 메인 리스트 조회
    def selectPackList(self, MES_FLAG, s_date, LIMIT):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT GROUP_CONCAT(BMAKE.PROC_CODE ORDER BY BMAKE.PROC_CODE) AS PROC_CODE,
                    DMAKE.LK_JAKUP_NO,
                    DMAKE.LK_JAKUP_SEQ,
                    DMAKE.LOT_NUMB,
                    DMAKE.CONN_CPROC_CODE,
                    DMAKE.HOLE_VALUE,
                    DMAKE.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                    CASE WHEN DMAKE.EDGE_FLAG = '1' THEN '일면'
                         WHEN DMAKE.EDGE_FLAG = '2' THEN '일면2'
                         WHEN DMAKE.EDGE_FLAG = '3' THEN '양면' 
                         ELSE '-' END AS EDGE_NAME,
                    DMAKE.QTY,
                    DMAKE.KYU,
                    CONCAT(BUYER.BUYER_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
                    SPCL.SPCL_NAME,
                    SJAKUP.SEQ,
                    SJAKUP.BAR_CODE,
                    SJAKUP.PUT_FLAG
            FROM(((((
                    FD_JAKUP_SEQ SJAKUP INNER JOIN FG_MAKE_BAR_CODE BMAKE ON SJAKUP.BAR_CODE = BMAKE.BAR_CODE)
                            INNER JOIN FG_MAKE_DETAIL DMAKE ON BMAKE.COMP_CODE = DMAKE.COMP_CODE AND BMAKE.REG_NO = DMAKE.REG_NO AND BMAKE.REG_SEQ = DMAKE.REG_SEQ)
                            LEFT OUTER JOIN BC_ITEM ITEM ON DMAKE.ITEM_CODE = ITEM.ITEM_CODE)
                            LEFT OUTER JOIN BC_SPCL SPCL ON DMAKE.SPCL_CODE = SPCL.SPCL_CODE)
                            LEFT OUTER JOIN BE_BUYER BUYER ON DMAKE.BUYER_CODE = BUYER.BUYER_CODE)
            WHERE BMAKE.COMP_CODE = '{COMP_CODE}'
              AND SJAKUP.MES_FLAG = '{MES_FLAG}'
              AND BMAKE.REG_DATE = '{s_date}'
              AND SJAKUP.BAR_CODE <> ''
              AND BMAKE.PROC_CODE BETWEEN '0110' AND '0120'
              AND BMAKE.BADN_QTY = '0'
            GROUP BY SJAKUP.BAR_CODE
            ORDER BY cast(SJAKUP.SEQ as unsigned) DESC
            {LIMIT}""".format(COMP_CODE = COMP_CODE, MES_FLAG = MES_FLAG, s_date = s_date, LIMIT = LIMIT)
            cursor_item.execute(sql_item)
            P_rows = cursor_item.fetchall()
        except: P_rows = 'failed'
    
        return P_rows
    
    def selectCproc(self):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT GROUP_CONCAT(CPROC_CODE) AS CPROC_CODE
        FROM BC_CPROC
        WHERE USED_FLAG = '1' AND CPROC_FLAG = '3' /* 옵션구분(3.심재보강) */
        GROUP BY CPROC_FLAG"""
        cursor_item.execute(sql_item)
        C_rows = cursor_item.fetchall()
    
        return C_rows
    
    #몰딩부 ###########################################################################################################################
    #몰딩부 > LOT 리스트 조회
    def selectMoldingLotList(self, s_date, PRT_FLAG):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                MJAKUP.LK_MAKE_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO) ITEM_TEXT,
                CASE WHEN COUNT(DISTINCT DJAKUP.BUYER_CODE) = 1
                     THEN BUYER.BUYER_NAME
                     ELSE CONCAT((SELECT BUYER2.BUYER_NAME
                                  FROM (FD_JAKUP_DETAIL DJAKUP2 LEFT OUTER JOIN BE_BUYER BUYER2 ON DJAKUP2.BUYER_CODE = BUYER2.BUYER_CODE)
                                  WHERE DJAKUP2.REG_NO = MJAKUP.REG_NO
                                  ORDER BY DJAKUP2.REG_SEQ LIMIT 1), '/외 ', COUNT(DISTINCT DJAKUP.BUYER_CODE) - 1, '건')
                     END AS BUYER_TEXT,
                SUM(DJAKUP.QTY) QTY,
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG,
                MJAKUP.JAKUP_APPR_TIME
            FROM(((((
                FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                        LEFT OUTER JOIN BC_ITEM ITEM_MA ON ITEM_MA.ITEM_LEVEL = 2 AND MJAKUP.ITEM_LA_CODE = ITEM_MA.ITEM_LA_CODE AND MJAKUP.ITEM_MA_CODE = ITEM_MA.ITEM_MA_CODE)
                        LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                        INNER JOIN FD_JAKUP_MASTER_PROC MPJAKUP ON MJAKUP.COMP_CODE = MPJAKUP.COMP_CODE AND MJAKUP.REG_NO = MPJAKUP.REG_NO AND MPJAKUP.PROC_CODE = '0404')
                        INNER JOIN (SELECT COMP_CODE, REG_NO, CASE MIN(PRT_FLAG) WHEN '0' THEN IF(MAX(PRT_FLAG) = '0', '0', '2') ELSE '1' END LK_PRT_FLAG
                                    FROM FD_JAKUP_BAR_CODE
                                    WHERE COMP_CODE = '{COMP_CODE}'
                                    GROUP BY COMP_CODE, REG_NO) BJAKUP ON MJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND MJAKUP.REG_NO = BJAKUP.REG_NO)
            WHERE DJAKUP.COMP_CODE = '{COMP_CODE}'
              AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
              AND MJAKUP.JAKUP_APPR_FLAG IN ('2','9')  /*지시승인 */
              AND BJAKUP.LK_PRT_FLAG LIKE '{PRT_FLAG}'
              AND (MJAKUP.ITEM_LA_CODE = '14' OR MJAKUP.ITEM_LA_CODE = '20')
            GROUP BY MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO),
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG,
                MJAKUP.JAKUP_APPR_TIME
            ORDER BY MJAKUP.REG_NO""".format(COMP_CODE = COMP_CODE, s_date = s_date, PRT_FLAG = PRT_FLAG)
            cursor_item.execute(sql_item)
            S_rows = cursor_item.fetchall()
        except: S_rows = 'failed'
        
        return S_rows
    
    #몰딩부 > LOT 라벨 데이터 조회
    def selectMoldingLotLabel(self, s_date, REG_NO):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT MJAKUP.REG_NO,
                   MJAKUP.LOT_NUMB,
                   MJAKUP.REG_DATE,
                   MJAKUP.HOPE_DATE,
                   
                   BUYER.BUYER_NAME,
                   BUYER.BUYER_CODE,
                   
                   GROUP_CONCAT(DJAKUP.REG_SEQ ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') REG_SEQ,
                   GROUP_CONCAT(DJAKUP.BIGO ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') BIGO,
                   GROUP_CONCAT(DJAKUP.LABEL_BIGO ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') LABEL_BIGO,
                   GROUP_CONCAT(SPCL.SPCL_NAME ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') SPCL_NAMES,
                   GROUP_CONCAT(ITEM.ITEM_NAME ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') ITEM_NAMES,
                   GROUP_CONCAT(DJAKUP.KYU ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') KYUS,
                   GROUP_CONCAT(DJAKUP.QTY ORDER by DJAKUP.REG_SEQ SEPARATOR ', ') QTYS,
                   
                   PJAKUP.SORT_KEY
            FROM(((((
                 FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                 INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
                 LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                 LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                 LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
            WHERE DJAKUP.JAKUP_APPR_FLAG IN ('2','9')   /*작업지시승인유무 0.대기 2.승인 9.취소*/
                  AND DJAKUP.COMP_CODE = '{COMP_CODE}'
                  AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
                  AND PJAKUP.PROC_CODE = '0404'
                  AND IFNULL(MJAKUP.MES_PRT_FLAG, '0') LIKE '%'
                  AND DJAKUP.REG_NO LIKE '{REG_NO}'
            GROUP BY DJAKUP.BUYER_CODE
            ORDER BY DJAKUP.REG_SEQ
            """.format(COMP_CODE = COMP_CODE, s_date = s_date, REG_NO = REG_NO)
            cursor_item.execute(sql_item)
            S_rows = cursor_item.fetchall()
        except: S_rows = 'failed'
        
        return S_rows
    
    #몰딩부 > DETAIL 리스트 조회
    def selectMoldingDetailList(self, REG_NO, REG_SEQ, SEQ_QTY, BUYER_CODE, s_date):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.REG_NO,
               MJAKUP.REG_DATE,
               MJAKUP.JAKUP_FLAG,
               MJAKUP.LOT_NUMB,
               
               DJAKUP.REG_SEQ,
               PJAKUP.SORT_KEY,
               DJAKUP.MES_PRT_FLAG,
               DJAKUP.MES_PRT_AUTO_FLAG,
               DJAKUP.HOPE_DATE,
               DJAKUP.KYU,
               DJAKUP.LENX,
               DJAKUP.WIDX,
               DJAKUP.TIKX,
               DJAKUP.ABS_LENX,
               DJAKUP.ABS_WIDX,
               DJAKUP.ABS_QTY,
               DJAKUP.ABS_APPR_FLAG,
               
               DJAKUP.QTY,
               DJAKUP.LK_MAKE_QTY,
               DJAKUP.HOLE_FLAG,
               ROUND(DJAKUP.HOLE_VALUE,0) HOLE_VALUE,
               ROUND(DJAKUP.CAL_HOLE_VALUE,0) CAL_HOLE_VALUE,  /*하부값 OR 상부값*/
               DJAKUP.EDGE_FLAG,
               CASE WHEN DJAKUP.EDGE_FLAG = '1' THEN '일면'
                    WHEN DJAKUP.EDGE_FLAG = '2' THEN '일면2'
                    WHEN DJAKUP.EDGE_FLAG = '3' THEN '양면' 
                    ELSE '-' END AS EDGE_NAME,
               
               DJAKUP.CONN_CPROC_NAME,
               CONCAT(FORMAT(ROW_NUMBER() OVER (PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ ORDER BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ, BJAKUP.SEQ_QTY), 0), '/',
                      FORMAT(COUNT(1) OVER(PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ), 0)) QTY_NO_ALL,  /*수량텍스트*/
               
               DJAKUP.CPROC_BIGO,
               DJAKUP.LABEL_BIGO,
               DJAKUP.BIGO,
               IF(IFNULL(DORDR.FSET_SEQ, '') = '', '일반품', 'SET') FSET_FLAG_NAME,
                      
               BJAKUP.SEQ_QTY,
               BJAKUP.PRT_FLAG, /*출력유무*/
               BJAKUP.BAR_CODE,
               
               ITEM.ITEM_MA_NAME,
               ITEM.ITEM_NAME,
               CONCAT(ITEM.ITEM_MA_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
               SPCL.SPCL_NAME,
               GLAS.GLAS_NAME,
               TRANS.TRANS_FLAG_NAME,
               BUYER.BUYER_NAME,
               BUYER.BUYER_CODE
        FROM ((((((((((((
              FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
              INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
              LEFT OUTER JOIN DD_ORDR_DETAIL DORDR ON DJAKUP.COMP_CODE = DORDR.COMP_CODE AND DJAKUP.LK_ORDR_NO = DORDR.REG_NO AND DJAKUP.LK_ORDR_SEQ = DORDR.REG_SEQ)
              INNER JOIN BP_PROC PROC ON PJAKUP.PROC_CODE = PROC.PROC_CODE)
              INNER JOIN BP_WC WC ON PROC.WC_CODE = WC.WC_CODE)
              LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
              LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
              LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
              LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
              LEFT OUTER JOIN BC_UNIT UNIT ON DJAKUP.UNIT_CODE = UNIT.UNIT_CODE)
              LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
              INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON DJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND DJAKUP.REG_NO = BJAKUP.REG_NO AND DJAKUP.REG_SEQ = BJAKUP.REG_SEQ)
        WHERE DJAKUP.JAKUP_APPR_FLAG IN ('2','9')   /*작업지시승인유무 0.대기 2.승인 9.취소*/
          AND DJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
          AND PJAKUP.PROC_CODE  IN ('0404', '0501')
          AND IFNULL(MJAKUP.MES_PRT_FLAG, '0') LIKE '%'
          AND DJAKUP.REG_NO LIKE '{REG_NO}'
          AND DJAKUP.REG_SEQ LIKE '{REG_SEQ}'
          AND BJAKUP.SEQ_QTY LIKE '{SEQ_QTY}'
          AND DJAKUP.BUYER_CODE LIKE '{BUYER_CODE}'
        """.format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ, SEQ_QTY = SEQ_QTY, BUYER_CODE = BUYER_CODE, s_date = s_date)
        cursor_item.execute(sql_item)
        D_rows = cursor_item.fetchall()
        
        return D_rows
    
    #문틀부 ###########################################################################################################################
    #문틀부 > LOT 리스트 조회
    def selectFrameLotList(self, s_date):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                MJAKUP.LK_MAKE_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO) ITEM_TEXT,
                SUBSTRING(CONCAT(MIN(CONCAT(LPAD(DJAKUP.SORT_KEY, 6), ITEM_MA.ITEM_MA_NAME, ' ', ITEM.ITEM_NAME)), CASE WHEN SIGN(COUNT(1) - 1) = 1 THEN CONCAT(' /외 ', CONCAT(CONCAT(COUNT(1) - 1),'건')) ELSE '' END), 7) HOPE_TEXT,
                SUM(DJAKUP.LK_MAKE_QTY) LK_MAKE_QTY,
                SUM(DJAKUP.QTY) QTY,
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG MES_PRT_FLAG_ALL, /*수동자동 출력구분 (0.대기 1.완료 2.진행) */  
                (SELECT SUM(CASE WHEN IFNULL(MES_PRT_FLAG,'0') = '1' THEN 1 ELSE 0 END) MES_PRT_FLAG_CNT FROM FD_JAKUP_DETAIL WHERE REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE) MES_PRT_FLAG_CNT,
                (SELECT SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '1' THEN 1 ELSE 0 END) MES_PRT_AUTO_FLAG_CNT FROM FD_JAKUP_DETAIL WHERE REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE) MES_PRT_AUTO_FLAG_CNT,
                (SELECT SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '2' THEN 1 ELSE 0 END) MES_PRT_AUTO_FLAG_CNT FROM FD_JAKUP_DETAIL WHERE REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE) MES_PRT_AUTO_FLAG_CNT2,
                
                (SELECT SUM(QTY) MES_PRT_FLAG_QTY FROM FD_JAKUP_DETAIL WHERE COMP_CODE = MJAKUP.COMP_CODE AND REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE AND IFNULL(MES_PRT_FLAG,'0') = '1') MES_PRT_FLAG_QTY,
                (SELECT SUM(QTY) MES_PRT_AUTO_FLAG_QTY FROM FD_JAKUP_DETAIL WHERE COMP_CODE = MJAKUP.COMP_CODE AND REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE AND IFNULL(MES_PRT_AUTO_FLAG,'0') = '1') MES_PRT_AUTO_FLAG_QTY,
                (SELECT SUM(QTY) MES_PRT_AUTO_FLAG_QTY FROM FD_JAKUP_DETAIL WHERE COMP_CODE = MJAKUP.COMP_CODE AND REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE AND IFNULL(MES_PRT_AUTO_FLAG,'0') = '2') MES_PRT_AUTO_FLAG_QTY2,
                 
                (SELECT CASE WHEN SUM(CASE WHEN IFNULL(MES_PRT_FLAG,'0') = '0' OR TRIM(MES_PRT_FLAG) = '' THEN 1 ELSE 0 END) = SUM(1) THEN '0'
                             WHEN SUM(CASE WHEN IFNULL(MES_PRT_FLAG,'0') = '1' THEN 1 ELSE 0 END) = SUM(1) THEN '1'
                             ELSE '2' END MES_PRT_FLAG FROM FD_JAKUP_DETAIL WHERE REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE) MES_PRT_FLAG, /*수동 출력구분 (0.대기 1.완료 2.진행) */                
                
                (SELECT CASE WHEN SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '0' OR TRIM(MES_PRT_AUTO_FLAG) = '' THEN 1 ELSE 0 END) = SUM(1) THEN '0'
                             WHEN SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '1' THEN 1 ELSE 0 END) = SUM(1) THEN '1'
                             ELSE '2' END MES_PRT_AUTO_FLAG FROM FD_JAKUP_DETAIL WHERE REG_NO = DJAKUP.REG_NO AND HOPE_DATE = DJAKUP.HOPE_DATE) MES_PRT_AUTO_FLAG, /*자동 출력구분 (0.대기 1.완료 2.진행) */    
                             
                MJAKUP.JAKUP_APPR_TIME,
                BJAKUP.LK_PRT_FLAG
            FROM(((((
                FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                        LEFT OUTER JOIN BC_ITEM ITEM_MA ON ITEM_MA.ITEM_LEVEL = 2 AND MJAKUP.ITEM_LA_CODE = ITEM_MA.ITEM_LA_CODE AND MJAKUP.ITEM_MA_CODE = ITEM_MA.ITEM_MA_CODE)
                        INNER JOIN FD_JAKUP_MASTER_PROC MPJAKUP ON MJAKUP.COMP_CODE = MPJAKUP.COMP_CODE AND MJAKUP.REG_NO = MPJAKUP.REG_NO AND MPJAKUP.PROC_CODE IN ('0501', '0801', '0901', '1601'))
                        INNER JOIN (SELECT COMP_CODE, REG_NO, CASE MIN(PRT_FLAG) WHEN '0' THEN IF(MAX(PRT_FLAG) = '0', '0', '2') ELSE '1' END LK_PRT_FLAG
                                    FROM FD_JAKUP_BAR_CODE
                                    WHERE COMP_CODE = '001'
                                    GROUP BY COMP_CODE, REG_NO) BJAKUP ON MJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND MJAKUP.REG_NO = BJAKUP.REG_NO)
                        LEFT OUTER JOIN BC_ITEM ITEM ON  DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
            WHERE DJAKUP.COMP_CODE = '{COMP_CODE}'
              AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
              AND MJAKUP.JAKUP_APPR_FLAG = '2'  /*지시승인 */
              AND BJAKUP.LK_PRT_FLAG LIKE '%'
            GROUP BY MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.LOT_NUMB,
                MJAKUP.JAKUP_FLAG,
                CONCAT(ITEM_MA.ITEM_MA_NAME, ' ', MJAKUP.JUKYO),
                BJAKUP.LK_PRT_FLAG,
                MJAKUP.MES_PRT_FLAG,
                MJAKUP.JAKUP_APPR_TIME
            ORDER BY MJAKUP.REG_NO""".format(COMP_CODE = COMP_CODE, s_date = s_date)
            cursor_item.execute(sql_item)
            M_rows = cursor_item.fetchall()
        except: M_rows = 'failed'
            
        return M_rows
    
    #문틀부 > 개별 리스트 조회
    def selectFrameList(self, s_date, PROC_CODE, WIDX, BUYER):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT MJAKUP.COMP_CODE,
                MJAKUP.REG_NO,
                MJAKUP.REG_DATE,
                MJAKUP.LOT_NUMB,
                DJAKUP.REG_SEQ,
                BJAKUP.SEQ_QTY,
                DJAKUP.KYU,
                DJAKUP.LENX,     
                DJAKUP.WIDX,
                DJAKUP.TIKX,
                DJAKUP.QTY,
                DJAKUP.QTY QTY_NO_ALL,
                DJAKUP.HOLE_FLAG,
                DJAKUP.HOLE_VALUE,
                DJAKUP.CAL_HOLE_VALUE,
                DJAKUP.EDGE_FLAG,
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '042')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '050')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '093')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '094')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '096')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '274')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '276')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '278')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '457')
                    > 0 THEN  'Y' ELSE 'N' END DR11_YN, /* 보강규칙 #11 모티스레버 */
                DJAKUP.CONN_CPROC_CODE,
                DJAKUP.CONN_CPROC_NAME,
                DJAKUP.SET_FLAG,
                MESF.WIDX FWIDX,
                MESF.LENX FLENX,
                PJAKUP.LK_MAKE_QTY,
                PJAKUP.SORT_KEY PSORT_KEY,
                ITEM.ITEM_NAME,
                ITEM.ITEM_CODE,
                ITEM.BG_LENX_VALUE,
                ITEM.BG_WIDX_VALUE,
                BOM.STRC_KYU_COMM, /*규격계산식*/
                SPCL.SPCL_NAME,
                BUYER.BUYER_NAME,
                BUYER.ANCHOR_FLAG,
                BJAKUP.BAR_CODE,
                (SELECT IFNULL((SELECT BAR_CODE FROM FG_MAKE_BAR_CODE WHERE PROC_CODE = '0901' AND BAR_CODE = BJAKUP.BAR_CODE LIMIT 1), '0') AS BAR_CODE        
                 FROM FG_MAKE_BAR_CODE LIMIT 1) AS BAR_FLAG
            FROM(((((((((
                FD_JAKUP_MASTER MJAKUP LEFT OUTER JOIN BA_EMPL EMPL ON MJAKUP.EMPL_CODE = EMPL.EMPL_CODE)
                       INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                       INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '0901')
                       LEFT OUTER JOIN BJ_ITEM_BOM BOM on DJAKUP.ITEM_CODE = BOM.ITEM_CODE)
                       LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                       LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                       LEFT OUTER JOIN BC_MES_FRAME MESF ON MESF.ITEM_CODE = ITEM.ITEM_CODE)
                       LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                       INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON DJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND DJAKUP.REG_NO = BJAKUP.REG_NO AND DJAKUP.REG_SEQ = BJAKUP.REG_SEQ)
            WHERE MJAKUP.COMP_CODE = '001'
              AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
              AND DJAKUP.MES_PRT_AUTO_FLAG = '1'
              AND ITEM.ITEM_MA_CODE = '1201'
              AND IFNULL(MJAKUP.JAKUP_APPR_FLAG, '%') LIKE '2' /* 지시승인유무 2.승인 */
              AND BOM.STRC_KYU_COMM IS NOT NULL
              {WIDX} {BUYER}
            ORDER BY MESF.WIDX, SPCL.SPCL_CODE, MJAKUP.REG_NO, DJAKUP.REG_SEQ, BJAKUP.SEQ_QTY
            """.format(COMP_CODE = COMP_CODE, s_date = s_date, PROC_CODE = PROC_CODE, WIDX = WIDX, BUYER = BUYER)
            cursor_item.execute(sql_item)
            M_rows = cursor_item.fetchall()
        except: M_rows = 'failed'
            
        return M_rows
    
    #문틀부 > DETAIL 리스트 조회
    def selectFrameDetailList(self, REG_NO, s_date, PROC_CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.LOT_NUMB,
            MJAKUP.REG_NO,
            DJAKUP.REG_SEQ,
            MJAKUP.JAKUP_FLAG,
            DJAKUP.MES_PRT_FLAG,
            PJAKUP.SORT_KEY,
            DJAKUP.HOPE_DATE,
            DJAKUP.MES_PRT_AUTO_FLAG,
            BUYER.BUYER_NAME,
            ITEM.ITEM_MA_NAME,
            ITEM.ITEM_NAME,
            CONCAT(ITEM.ITEM_MA_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
            DJAKUP.LK_MAKE_QTY,
            DJAKUP.QTY,
            DJAKUP.KYU,
            DJAKUP.LENX,
            DJAKUP.WIDX,
            -- DJAKUP.ABS_LENX,
            -- DJAKUP.ABS_WIDX,
            -- DJAKUP.ABS_QTY,
            -- DJAKUP.ABS_APPR_FLAG,
            -- DJAKUP.EDGE_FLAG,
            DJAKUP.HOLE_FLAG,
            ROUND(DJAKUP.HOLE_VALUE,0) HOLE_VALUE,
            ROUND(DJAKUP.CAL_HOLE_VALUE,0) CAL_HOLE_VALUE,  /*하부값 OR 상부값*/
            DJAKUP.MES_PRT_FLAG,
            BJAKUP.LK_PRT_FLAG,
            SPCL.SPCL_NAME,
            GLAS.GLAS_NAME,
            TRANS.TRANS_FLAG_NAME
        FROM (((((((((((
              FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
              INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
              INNER JOIN BP_PROC PROC ON PJAKUP.PROC_CODE = PROC.PROC_CODE)
              INNER JOIN BP_WC WC ON PROC.WC_CODE = WC.WC_CODE)
              
              INNER JOIN (SELECT COMP_CODE, REG_NO, CASE MIN(PRT_FLAG) WHEN '0' THEN IF(MAX(PRT_FLAG) = '0', '0', '2') ELSE '1' END LK_PRT_FLAG
                                    FROM FD_JAKUP_BAR_CODE
                                    WHERE COMP_CODE = '001'
                                    GROUP BY COMP_CODE, REG_NO) BJAKUP ON MJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND MJAKUP.REG_NO = BJAKUP.REG_NO)  
                                    
              LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
              LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
              LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
              LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
              LEFT OUTER JOIN BC_UNIT UNIT ON DJAKUP.UNIT_CODE = UNIT.UNIT_CODE)
              LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
        WHERE DJAKUP.JAKUP_APPR_FLAG ='2'   /*작업지시승인유무 0.대기 2.승인 9.취소*/
          AND DJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
          AND PJAKUP.PROC_CODE  IN ('0501', '0801', '0901', '1601')
          AND IFNULL(MJAKUP.MES_PRT_FLAG, '0') LIKE '%'
          AND DJAKUP.REG_NO LIKE '{REG_NO}'
        """.format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, s_date = s_date, PROC_CODE = PROC_CODE)
        cursor_item.execute(sql_item)
        D_rows = cursor_item.fetchall()
        
        return D_rows
    
    #문틀부 > DETAIL BARCODE별 리스트 조회
    def selectFrameDetaiBarcodelList(self, REG_NO, REG_SEQ, s_date, PROC_CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.LOT_NUMB,
            MJAKUP.REG_NO,
            DJAKUP.REG_SEQ,
            BJAKUP.SEQ_QTY,
            DJAKUP.REG_DATE,
            MJAKUP.JAKUP_FLAG,
            DJAKUP.MES_PRT_FLAG,
            PJAKUP.SORT_KEY,
            DJAKUP.HOPE_DATE,
            DJAKUP.MES_PRT_AUTO_FLAG,
            BUYER.BUYER_CODE,
            BUYER.BUYER_NAME,
            ITEM.ITEM_MA_NAME,
            ITEM.ITEM_NAME,
            CONCAT(ITEM.ITEM_MA_NAME, '/', ITEM.ITEM_NAME) ITEM_TEXT,
            DJAKUP.LK_MAKE_QTY,
            DJAKUP.QTY,
            CONCAT(FORMAT(ROW_NUMBER() OVER (PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ ORDER BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ, BJAKUP.SEQ_QTY), 0), '/',
            FORMAT(COUNT(1) OVER(PARTITION BY BJAKUP.COMP_CODE, BJAKUP.REG_NO, BJAKUP.REG_SEQ), 0)) QTY_NO_ALL,  /*수량텍스트*/
            DJAKUP.KYU,
            DJAKUP.LENX,
            DJAKUP.WIDX,
            -- DJAKUP.ABS_LENX,
            -- DJAKUP.ABS_WIDX,
            -- DJAKUP.ABS_QTY,
            -- DJAKUP.ABS_APPR_FLAG,
            -- DJAKUP.EDGE_FLAG,
            DJAKUP.HOLE_FLAG,
            ROUND(DJAKUP.HOLE_VALUE,0) HOLE_VALUE,
            ROUND(DJAKUP.CAL_HOLE_VALUE,0) CAL_HOLE_VALUE,  /*하부값 OR 상부값*/
            DJAKUP.LABEL_BIGO,
            DJAKUP.MES_PRT_FLAG,
            BJAKUP.PRT_FLAG,  /*출력유무*/
            SPCL.SPCL_NAME,
            GLAS.GLAS_NAME,
            TRANS.TRANS_FLAG_NAME,
            PJAKUP.PROC_CODE,
            BJAKUP.BAR_CODE
        FROM (((((((((((
              FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
              INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ)
              INNER JOIN BP_PROC PROC ON PJAKUP.PROC_CODE = PROC.PROC_CODE)
              INNER JOIN BP_WC WC ON PROC.WC_CODE = WC.WC_CODE)
              LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
              LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
              LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
              LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
              LEFT OUTER JOIN BC_UNIT UNIT ON DJAKUP.UNIT_CODE = UNIT.UNIT_CODE)
              LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
              INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON DJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND DJAKUP.REG_NO = BJAKUP.REG_NO AND DJAKUP.REG_SEQ = BJAKUP.REG_SEQ)
        WHERE DJAKUP.JAKUP_APPR_FLAG ='2'   /*작업지시승인유무 0.대기 2.승인 9.취소*/
          AND DJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
          AND PJAKUP.PROC_CODE IN ('0501', '0801', '0901', '1601')
          AND IFNULL(MJAKUP.MES_PRT_FLAG, '0') LIKE '%'
          AND DJAKUP.REG_NO LIKE '{REG_NO}'
          AND DJAKUP.REG_SEQ LIKE '{REG_SEQ}'
        """.format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ, s_date = s_date, PROC_CODE = PROC_CODE)
        cursor_item.execute(sql_item)
        D_rows = cursor_item.fetchall()
        
        return D_rows
    
    #문틀부 > 출력 FLAG 조회
    def selectFramePrtFlag(self, REG_NO):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT CASE WHEN DJAKUP.MES_PRT_FLAG_0_CNT = DJAKUP.TOTAL_CNT AND DJAKUP.MES_PRT_AUTO_FLAG_0_CNT = DJAKUP.TOTAL_CNT THEN '0' 
                    WHEN DJAKUP.MES_PRT_FLAG_1_CNT + DJAKUP.MES_PRT_AUTO_FLAG_1_CNT = DJAKUP.TOTAL_CNT THEN '1'
                    ELSE '2' END MES_PRT_FLAG /*출력구분 (0.대기 1.완료 2.진행) */
        FROM(SELECT /* 수동출력구분 */
                   SUM(CASE WHEN IFNULL(MES_PRT_FLAG,'0') = '0' OR TRIM(MES_PRT_FLAG) = '' THEN 1 ELSE 0 END) MES_PRT_FLAG_0_CNT,
                   SUM(CASE WHEN IFNULL(MES_PRT_FLAG,'0') = '1' THEN 1 ELSE 0 END) MES_PRT_FLAG_1_CNT,
                   /* 자동출력구분 */
                   SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '0' OR TRIM(MES_PRT_AUTO_FLAG) = '' THEN 1 ELSE 0 END) MES_PRT_AUTO_FLAG_0_CNT,
                   SUM(CASE WHEN IFNULL(MES_PRT_AUTO_FLAG,'0') = '1' THEN 1 ELSE 0 END) MES_PRT_AUTO_FLAG_1_CNT,
                   /* 전체건수 */
                   SUM(1) TOTAL_CNT
             FROM FD_JAKUP_DETAIL
             WHERE REG_NO = '{REG_NO}') DJAKUP""".format(REG_NO = REG_NO)
        cursor_item.execute(sql_item)
        PRT_FLAG = cursor_item.fetchone()
            
        return PRT_FLAG
    
    #문틀부 > MASTER 출력 FLAG UPDATE
    def updateFrameFlag(self, PRT_FLAG, PRT_DATE, PRT_TIME, PRT_EMPL_CODE, REG_NO):
        sql_item ="""
        UPDATE FD_JAKUP_MASTER
        SET MES_PRT_FLAG = '{PRT_FLAG}', MES_PRT_DATE = '{PRT_DATE}', MES_PRT_TIME = '{PRT_TIME}', MES_PRT_EMPL_CODE = '{PRT_EMPL_CODE}'
        WHERE REG_NO = '{REG_NO}'
        """.format(PRT_FLAG = PRT_FLAG, PRT_DATE = PRT_DATE, PRT_TIME = PRT_TIME, PRT_EMPL_CODE = PRT_EMPL_CODE, REG_NO = REG_NO)
        try:
            cursor_item.execute(sql_item.encode('utf-8'))
            db.commit()
            result = 1
        except:
            db.rollback()
            result = 2
            
        return result
    
    #문틀부 > DETAIL 출력 FLAG UPDATE
    def updateFrameDetailFlag(self, MES_PRT_FLAG, MES_PRT_AUTO_FLAG, REG_NO, REG_SEQ, PRT_DATE, PRT_TIME, PRT_EMPL_CODE):
        sql_item ="""
        UPDATE FD_JAKUP_DETAIL
        SET MES_PRT_FLAG = '{MES_PRT_FLAG}', MES_PRT_AUTO_FLAG = '{MES_PRT_AUTO_FLAG}',
            MES_PRT_DATE = '{PRT_DATE}', MES_PRT_TIME = '{PRT_TIME}', MES_PRT_EMPL_CODE = '{PRT_EMPL_CODE}'
        WHERE REG_NO = '{REG_NO}' AND REG_SEQ = '{REG_SEQ}'
        """.format(MES_PRT_FLAG = MES_PRT_FLAG, MES_PRT_AUTO_FLAG = MES_PRT_AUTO_FLAG, PRT_DATE = PRT_DATE, PRT_TIME = PRT_TIME, PRT_EMPL_CODE = PRT_EMPL_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ)
        try: cursor_item.execute(sql_item.encode('utf-8'))
        except: db.rollback()
    
    #문틀부 > 아이템 정보 조회
    def selectItemList(self, REG_NO, DATE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MESF.WIDX FWIDX
        FROM((((FD_JAKUP_MASTER MJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                   INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '0901')
                   LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                   LEFT OUTER JOIN BC_MES_FRAME MESF ON MESF.ITEM_CODE = ITEM.ITEM_CODE)
        WHERE MJAKUP.COMP_CODE = '001'
          AND DJAKUP.HOPE_DATE BETWEEN '{DATE}' AND '{DATE}'
          AND MJAKUP.REG_NO LIKE '{REG_NO}'
          AND ITEM.ITEM_LA_CODE = '12'
          AND IFNULL(MJAKUP.JAKUP_APPR_FLAG, '%') LIKE '2' /* 지시승인유무 2.승인 */
        GROUP BY MESF.WIDX""".format(REG_NO = REG_NO, DATE = DATE)
        cursor_item.execute(sql_item)
        Q_rows = cursor_item.fetchall()
            
        return Q_rows
    
    #문틀부 > 색상 정보 조회
    def selectSpclList(self, s_date, W_DATA, MESF):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.COMP_CODE,
            MJAKUP.REG_NO,
            MJAKUP.REG_DATE,
            MJAKUP.LOT_NUMB,
            DJAKUP.REG_SEQ,
            DJAKUP.KYU,
            DJAKUP.LENX,     
            DJAKUP.WIDX,
            DJAKUP.TIKX,
            DJAKUP.QTY,
            DJAKUP.HOLE_FLAG,
            DJAKUP.HOLE_VALUE,
            DJAKUP.CAL_HOLE_VALUE,
            DJAKUP.EDGE_FLAG,
            DJAKUP.CONN_CPROC_CODE,
            DJAKUP.CONN_CPROC_NAME,
            DJAKUP.SET_FLAG,
            MESF.WIDX FWIDX,
            MESF.LENX FLENX,
            PJAKUP.LK_MAKE_QTY,
            PJAKUP.SORT_KEY PSORT_KEY,
            ITEM.ITEM_NAME,
            ITEM.ITEM_CODE,
            ITEM.BG_LENX_VALUE,
            ITEM.BG_WIDX_VALUE,
            BOM.STRC_KYU_COMM, /*규격계산식*/
            SPCL.SPCL_NAME,
            BUYER.BUYER_NAME
        FROM((((((((
            FD_JAKUP_MASTER MJAKUP LEFT OUTER JOIN BA_EMPL EMPL ON MJAKUP.EMPL_CODE = EMPL.EMPL_CODE)
                   INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                   INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '0901')
                   LEFT OUTER JOIN BJ_ITEM_BOM BOM on DJAKUP.ITEM_CODE = BOM.ITEM_CODE)
                   LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                   LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                   LEFT OUTER JOIN BC_MES_FRAME MESF ON MESF.ITEM_CODE = ITEM.ITEM_CODE)
                   LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
        WHERE MJAKUP.COMP_CODE = '{COMP_CODE}'
          AND DJAKUP.HOPE_DATE BETWEEN '{s_date}' AND '{s_date}'
          AND MJAKUP.REG_NO LIKE '%'
          AND DJAKUP.REG_SEQ LIKE '%'
          AND DJAKUP.MES_PRT_AUTO_FLAG = '1'
          AND ITEM.ITEM_MA_CODE = '1201'
          AND IFNULL(MJAKUP.JAKUP_APPR_FLAG, '%') LIKE '2' /* 지시승인유무 2.승인 */
          AND BOM.STRC_KYU_COMM IS NOT NULL
          {W_DATA}
          {MESF}
        ORDER BY MESF.WIDX, SPCL.SPCL_CODE
        """.format(COMP_CODE = COMP_CODE, s_date = s_date, W_DATA = W_DATA, MESF = MESF)
        cursor_item.execute(sql_item)
        S_rows = cursor_item.fetchall()
    
        return S_rows
    
    #보강재 부착 ########################################################################################################################
    #보강재 > 보강재 리스트 조회
    def selectBogangList(self, MES_FLAG, REG_DATE, REG_TIME):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT *
FROM FD_JAKUP_SEQ_FRAME
WHERE MES_FLAG LIKE '1'
  AND REG_DATE = '20250804'
  AND REG_TIME < 144643
ORDER BY SEQ DESC
limit 10;""".format(MES_FLAG = MES_FLAG, REG_DATE = REG_DATE, REG_TIME = REG_TIME)
        cursor_item.execute(sql_item)
        L_rows = cursor_item.fetchall()
    
        return L_rows
    
    #보강재 > 보강재 데이터 조회
    def selectBogangData(self, BAR_CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MJAKUP.COMP_CODE,
            MJAKUP.REG_NO,
            MJAKUP.REG_DATE,
            MJAKUP.LOT_NUMB,
            DJAKUP.REG_SEQ,
            BJAKUP.SEQ_QTY,
            DJAKUP.LENX,     
            DJAKUP.WIDX,
            DJAKUP.TIKX,
            DJAKUP.HOLE_VALUE,
            DJAKUP.CAL_HOLE_VALUE,
            DJAKUP.CONN_CPROC_CODE,
            DJAKUP.CONN_CPROC_NAME,
            MESF.WIDX FWIDX,
            MESF.LENX FLENX,
            SPCL.SPCL_NAME,
            BUYER.BUYER_NAME
        FROM(((((((((
            FD_JAKUP_MASTER MJAKUP LEFT OUTER JOIN BA_EMPL EMPL ON MJAKUP.EMPL_CODE = EMPL.EMPL_CODE)
                   INNER JOIN FD_JAKUP_DETAIL DJAKUP ON MJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND MJAKUP.REG_NO = DJAKUP.REG_NO)
                   INNER JOIN FD_JAKUP_PROC PJAKUP ON DJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND DJAKUP.REG_NO = PJAKUP.REG_NO AND DJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '0901')
                   LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                   LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                   LEFT OUTER JOIN BJ_ITEM_BOM BOM on DJAKUP.ITEM_CODE = BOM.ITEM_CODE)
                   LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                   LEFT OUTER JOIN BC_MES_FRAME MESF ON MESF.ITEM_CODE = ITEM.ITEM_CODE)
                   INNER JOIN FD_JAKUP_BAR_CODE BJAKUP ON DJAKUP.COMP_CODE = BJAKUP.COMP_CODE AND DJAKUP.REG_NO = BJAKUP.REG_NO AND DJAKUP.REG_SEQ = BJAKUP.REG_SEQ)
        WHERE MJAKUP.COMP_CODE = '{COMP_CODE}' AND BJAKUP.BAR_CODE = '{BAR_CODE}'
        """.format(COMP_CODE = COMP_CODE, BAR_CODE = BAR_CODE)
        cursor_item.execute(sql_item)
        S_rows = cursor_item.fetchall()
    
        return S_rows
    
    #################################################################################################################################
    #라벨 데이터 조회
    def selectCNClabel(self, PROC_CODE, BAR_CODE):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT BJAKUP.COMP_CODE,
                BJAKUP.REG_DATE,
                BJAKUP.REG_NO,
                BJAKUP.REG_SEQ,
                BJAKUP.LOT_NUMB,
                BJAKUP.SEQ_QTY,
                DJAKUP.HOPE_DATE,  /*희낭납기일*/
                PJAKUP.SORT_KEY,
                PJAKUP.LK_MAKE_QTY,
                DJAKUP.LENX,
                DJAKUP.WIDX,
                DJAKUP.TIKX,
                DJAKUP.KYU,
                DJAKUP.QTY,
                DJAKUP.HOLE_FLAG,
                DJAKUP.HOLE_VALUE,
                DJAKUP.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                DJAKUP.EDGE_FLAG,
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '042')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '047') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '050') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '093') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '094') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '096')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '109')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '110') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '111') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '114')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '115') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '118') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '119') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '120')     
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '121') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '122') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '123') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '124') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '125') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '224')     
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '225') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '226')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '261')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '274') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '276') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '278')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '322') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '325')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '407')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '457')
                    > 0 THEN  'Y' ELSE 'N' END DR11_YN, /* 보강규칙 #11 모티스레버 */
                ITEM.ITEM_MA_NAME,
                ITEM.ITEM_NAME,
                CONCAT(ITEM.ITEM_MA_NAME, ' ', ITEM.ITEM_NAME) ITEM_TEXT,
                SPCL.SPCL_CODE,
                SPCL.SPCL_NAME,
                GLAS.GLAS_NAME,
                TRANS.TRANS_FLAG_NAME,
                BUYER.BUYER_NAME,
                ADDRESS1,
                CASE WHEN DJAKUP.EDGE_FLAG = '1' THEN '일면'
                     WHEN DJAKUP.EDGE_FLAG = '2' THEN '일면2'
                     WHEN DJAKUP.EDGE_FLAG = '3' THEN '양면' 
                     ELSE '-' END AS EDGE_NAME,
                DJAKUP.CONN_CPROC_NAME,
                DJAKUP.CONN_CPROC_CODE,
                DJAKUP.CPROC_BIGO,
                DJAKUP.LABEL_BIGO,
                DJAKUP.BIGO,
                IF(IFNULL(DORDR.FSET_SEQ, '') = '', '일반품', 'SET') FSET_FLAG_NAME,
                BJAKUP.BAR_CODE,
                /* 시트지컬러유무 N(필름X,백골) Y(필름O) */     
                CASE WHEN      
                    (CASE WHEN
                        (CASE WHEN DJAKUP.CONN_CPROC_CODE = '' THEN 1 ELSE 0 END)
                        + INSTR(SPCL.SPCL_CODE, '177')
                     + INSTR(SPCL.SPCL_CODE, '373')        
                        + INSTR(SPCL.SPCL_CODE, '977')
                     + INSTR(SPCL.SPCL_CODE, '877')    
                        + INSTR(SPCL.SPCL_CODE, 'A77')
                     + INSTR(SPCL.SPCL_CODE, '277')                        
                     > 0 THEN  'N' ELSE 'Y' END) = 'N' THEN
                     CASE WHEN DJAKUP.WIDX > 1260 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름X,백골 */
                 ELSE
                     CASE WHEN DJAKUP.WIDX > 1220 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름O */
                 END NO_YN
            FROM((((((((
                FD_JAKUP_BAR_CODE BJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON BJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND BJAKUP.REG_NO = DJAKUP.REG_NO AND BJAKUP.REG_SEQ = DJAKUP.REG_SEQ)
                        INNER JOIN FD_JAKUP_PROC PJAKUP ON BJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND BJAKUP.REG_NO = PJAKUP.REG_NO AND BJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '{PROC_CODE}')
                        LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
                        LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                        LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                        LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
                        LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                        LEFT OUTER JOIN DD_ORDR_DETAIL DORDR ON DJAKUP.COMP_CODE = DORDR.COMP_CODE AND DJAKUP.LK_ORDR_NO = DORDR.REG_NO AND DJAKUP.LK_ORDR_SEQ = DORDR.REG_SEQ)
            WHERE BJAKUP.BAR_CODE = '{BAR_CODE}'""".format(PROC_CODE = PROC_CODE, BAR_CODE = BAR_CODE)
            cursor_item.execute(sql_item)
            QR_rows = cursor_item.fetchall()
        except: QR_rows = 'failed'
    
        return QR_rows
    
    #라벨 데이터 조회
    def selectCNClabel_REG(self, PROC_CODE, REG_NO, REG_SEQ, SEQ_QTY):
        try:
            cursor_item.execute('RESET QUERY CACHE;')
            sql_item = """
            SELECT BJAKUP.COMP_CODE,
                BJAKUP.REG_DATE,
                BJAKUP.REG_NO,
                BJAKUP.REG_SEQ,
                BJAKUP.LOT_NUMB,
                BJAKUP.SEQ_QTY,
                DJAKUP.HOPE_DATE,  /*희낭납기일*/
                PJAKUP.SORT_KEY,
                DJAKUP.LENX,
                DJAKUP.WIDX,
                DJAKUP.TIKX,
                DJAKUP.KYU,
                DJAKUP.QTY,
                DJAKUP.HOLE_FLAG,
                DJAKUP.HOLE_VALUE,
                DJAKUP.CAL_HOLE_VALUE, /*하부값 OR 상부값*/
                DJAKUP.EDGE_FLAG,
                CASE WHEN 
                INSTR(DJAKUP.CONN_CPROC_CODE, '042')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '047') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '050') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '093') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '094') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '096')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '109')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '110') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '111') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '114')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '115') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '118')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '119')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '120')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '121')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '122')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '123')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '124')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '125')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '224')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '225')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '226')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '261')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '274') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '276') 
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '278')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '322')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '325')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '407')
                    + INSTR(DJAKUP.CONN_CPROC_CODE, '457')
                    > 0 THEN  'Y' ELSE 'N' END DR11_YN, /* 보강규칙 #11 모티스레버 */
                ITEM.ITEM_MA_NAME,
                ITEM.ITEM_NAME,
                CONCAT(ITEM.ITEM_MA_NAME, ' ', ITEM.ITEM_NAME) ITEM_TEXT,
                SPCL.SPCL_CODE,
                SPCL.SPCL_NAME,
                GLAS.GLAS_NAME,
                CASE WHEN DJAKUP.EDGE_FLAG = '1' THEN '일면'
                     WHEN DJAKUP.EDGE_FLAG = '2' THEN '일면2'
                     WHEN DJAKUP.EDGE_FLAG = '3' THEN '양면' 
                     ELSE '-' END AS EDGE_NAME,
                TRANS.TRANS_FLAG_NAME,
                BUYER.BUYER_NAME,
                ADDRESS1,
                DJAKUP.CONN_CPROC_NAME,
                DJAKUP.CONN_CPROC_CODE,
                DJAKUP.CPROC_BIGO,
                DJAKUP.LABEL_BIGO,
                DJAKUP.BIGO,
                IF(IFNULL(DORDR.FSET_SEQ, '') = '', '일반품', 'SET') FSET_FLAG_NAME,
                BJAKUP.BAR_CODE,
                CASE WHEN      
                    (CASE WHEN
                        (CASE WHEN DJAKUP.CONN_CPROC_CODE = '' THEN 1 ELSE 0 END)
                        + INSTR(SPCL.SPCL_CODE, '177')
                     + INSTR(SPCL.SPCL_CODE, '373')        
                        + INSTR(SPCL.SPCL_CODE, '977')
                     + INSTR(SPCL.SPCL_CODE, '877')    
                        + INSTR(SPCL.SPCL_CODE, 'A77')
                     + INSTR(SPCL.SPCL_CODE, '277')                        
                     > 0 THEN  'N' ELSE 'Y' END) = 'N' THEN
                     CASE WHEN DJAKUP.WIDX > 1260 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름X,백골 */
                 ELSE
                     CASE WHEN DJAKUP.WIDX > 1220 || DJAKUP.LENX > 2450 || DJAKUP.WIDX < 300 || DJAKUP.LENX < 1500 THEN 'Y' ELSE 'N' END /* 작업불가 사이즈 - 필름O */
                 END NO_YN
            FROM((((((((
                FD_JAKUP_BAR_CODE BJAKUP INNER JOIN FD_JAKUP_DETAIL DJAKUP ON BJAKUP.COMP_CODE = DJAKUP.COMP_CODE AND BJAKUP.REG_NO = DJAKUP.REG_NO AND BJAKUP.REG_SEQ = DJAKUP.REG_SEQ)
                        INNER JOIN FD_JAKUP_PROC PJAKUP ON BJAKUP.COMP_CODE = PJAKUP.COMP_CODE AND BJAKUP.REG_NO = PJAKUP.REG_NO AND BJAKUP.REG_SEQ = PJAKUP.REG_SEQ AND PJAKUP.PROC_CODE = '{PROC_CODE}')
                        LEFT OUTER JOIN BB_TRANS TRANS ON DJAKUP.TRANS_FLAG = TRANS.TRANS_FLAG)
                        LEFT OUTER JOIN BC_ITEM ITEM ON DJAKUP.ITEM_CODE = ITEM.ITEM_CODE)
                        LEFT OUTER JOIN BC_SPCL SPCL ON DJAKUP.SPCL_CODE = SPCL.SPCL_CODE)
                        LEFT OUTER JOIN BC_GLAS GLAS ON DJAKUP.GLAS_CODE = GLAS.GLAS_CODE)
                        LEFT OUTER JOIN BE_BUYER BUYER ON DJAKUP.BUYER_CODE = BUYER.BUYER_CODE)
                        LEFT OUTER JOIN DD_ORDR_DETAIL DORDR ON DJAKUP.COMP_CODE = DORDR.COMP_CODE AND DJAKUP.LK_ORDR_NO = DORDR.REG_NO AND DJAKUP.LK_ORDR_SEQ = DORDR.REG_SEQ)
            WHERE BJAKUP.REG_NO = '{REG_NO}'
              AND BJAKUP.REG_SEQ = '{REG_SEQ}'
              AND BJAKUP.SEQ_QTY = {SEQ_QTY}""".format(PROC_CODE = PROC_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ, SEQ_QTY = SEQ_QTY)
            cursor_item.execute(sql_item)
            QR_rows = cursor_item.fetchall()
        except: QR_rows = 'failed'
    
        return QR_rows
    
    #홀가공 불가옵션 조회
    def selectHoleFlag(self, CPROC_CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        /* 자동화 홀가공 불가옵션만 select */
        SELECT CPROC.CPROC_CODE,
              CPROC.CPROC_NAME,
              CPROC.SORT_KEY,
              CPROC.USED_FLAG,
              CPROC.CPROC_PRICE,
              CPROC.CPROC_FLAG,
              CPROC.CNC_FLAG,
              CPROC.BIGO,
              CPROC.IMAGE_PATH,
              CPROC.IMAGE_PATH BEF_IMAGE_PATH,  /*변경전 이미지*/
              '' CHNG_IMAGE_PATH  /*이미지 변경시 사용*/
        FROM BC_CPROC CPROC
        WHERE IFNULL(CPROC.CPROC_FLAG, '%') IN ('A', '9') /* 옵션구분(A.홀가공X, 9.보강,홀가공X) */
        AND CPROC.CPROC_CODE IN ({CPROC_CODE})""".format(CPROC_CODE = CPROC_CODE)
        cursor_item.execute(sql_item)
        H_rows = cursor_item.fetchone()
    
        return H_rows
    
    #################################################################################################################################
    #생산실적 조회 > REG_SEQ별
    def selectMakeRegData(self, PROC_CODE, LK_JAKUP_NO, LK_JAKUP_SEQ):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT COMP_CODE, REG_NO, REG_SEQ, REG_DATE
        FROM FG_MAKE_DETAIL
        WHERE COMP_CODE = '{COMP_CODE}'
          AND PROC_CODE = '{PROC_CODE}'
          AND LK_JAKUP_NO = '{LK_JAKUP_NO}'
          AND LK_JAKUP_SEQ = '{LK_JAKUP_SEQ}'
        LIMIT 1;""".format(COMP_CODE = COMP_CODE, PROC_CODE = PROC_CODE, LK_JAKUP_NO = LK_JAKUP_NO, LK_JAKUP_SEQ = LK_JAKUP_SEQ)
        cursor_item.execute(sql_item)
        M_rows = cursor_item.fetchall()
    
        return M_rows
    
    #생산실적 조회 > 바코드 별
    def selectMakeData(self, PROC_CODE, BAR_CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT BMAKE.COMP_CODE, BMAKE.REG_NO, BMAKE.REG_SEQ
        FROM FG_MAKE_BAR_CODE BMAKE
        WHERE BMAKE.COMP_CODE = '{COMP_CODE}'
          AND BMAKE.PROC_CODE = '{PROC_CODE}'
          AND BMAKE.BAR_CODE LIKE '{BAR_CODE}'
        LIMIT 1;""".format(COMP_CODE = COMP_CODE, PROC_CODE = PROC_CODE, BAR_CODE = BAR_CODE)
        cursor_item.execute(sql_item)
        M_rows = cursor_item.fetchall()
    
        return M_rows
    
    #심재 QR코드 밠행시 업데이트
    def LABEL_UPDATE_SQL(self, REG_NO, REG_SEQ, SEQ_QTY):
        sql_item ="""
        UPDATE FD_JAKUP_BAR_CODE
        SET PRT_FLAG = '1'
        WHERE COMP_CODE = '{COMP_CODE}'
          AND REG_NO = '{REG_NO}'
          AND REG_SEQ LIKE '{REG_SEQ}'
          AND SEQ_QTY LIKE '{SEQ_QTY}'""".format(COMP_CODE = COMP_CODE, REG_NO = REG_NO, REG_SEQ = REG_SEQ, SEQ_QTY = SEQ_QTY)
        try: cursor_item.execute(sql_item.encode('utf-8'))
        except: db.rollback()
    
    #################################################################################################################################
    #FD_JAKUP_SEQ 테이블 조회
    def selectJakupData(self, MES_FLAG, CODE):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT *
        FROM FD_JAKUP_SEQ
        WHERE MES_FLAG LIKE '{MES_FLAG}'
          AND BAR_CODE = '{CODE}'""".format(MES_FLAG = MES_FLAG, CODE = CODE)
        cursor_item.execute(sql_item)
        B_rows = cursor_item.fetchone()
    
        return B_rows
    
    #FD_JAKUP_SEQ 테이블 MAX SEQ 조회
    def selectEdgeMaxSeq(self, MES_FLAG, s_date):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT MAX(cast(SEQ as UNSIGNED)) AS SEQ
        FROM FD_JAKUP_SEQ
        WHERE MES_FLAG = '{MES_FLAG}'
          AND REG_DATE = '{s_date}00'""".format(MES_FLAG = MES_FLAG, s_date = s_date)
        cursor_item.execute(sql_item)
        SEQ = cursor_item.fetchone()
    
        return SEQ
    
    #FD_JAKUP_SEQ 테이블 조회
    def selectEdgeSeq(self, MES_FLAG, SEQ, s_date, FLAG):
        cursor_item.execute('RESET QUERY CACHE;')
        sql_item = """
        SELECT *
        FROM FD_JAKUP_SEQ
        WHERE MES_FLAG = '{MES_FLAG}'
          AND REG_DATE = '{s_date}00'
          AND SEQ = '{SEQ}'
          AND {FLAG}""".format(MES_FLAG = MES_FLAG, SEQ = SEQ, s_date = s_date, FLAG = FLAG)
        cursor_item.execute(sql_item)
        SEQ = cursor_item.fetchone()
    
        return SEQ
    
    #FD_JAKUP_SEQ 테이블 INSERT
    def insertEdgeSeq(self, FLAG, s_date, BAR_CODE, SEQ, PUT_FLAG):
        logging.debug('insertEdgeSeq : {0}, {1}, {2}, {3}, {4}'.format(FLAG, s_date, BAR_CODE, SEQ, PUT_FLAG))
        sql_item ="""
        INSERT INTO FD_JAKUP_SEQ(MES_FLAG, REG_DATE, BAR_CODE, SEQ, PUT_FLAG)
        VALUES('{FLAG}', '{s_date}00', '{BAR_CODE}', '{SEQ}', '{PUT_FLAG}')
        """.format(FLAG = FLAG, s_date = s_date, BAR_CODE = BAR_CODE, SEQ = SEQ, PUT_FLAG = PUT_FLAG)
        try:
            cursor_item.execute(sql_item.encode('utf-8'))
            db.commit()
        except:
            db.rollback()
    
    #FD_JAKUP_SEQ 테이블 UPDATE
    def updateEdgeSeq(self, PUT_FLAG, s_date, FLAG, BAR_CODE, SEQ):
        logging.debug('updateEdgeSeq : {0}, {1}, {2}, {3}, {4}'.format(PUT_FLAG, s_date, FLAG, BAR_CODE, SEQ))
        sql_item ="""
        UPDATE FD_JAKUP_SEQ
        SET {PUT_FLAG}
        WHERE MES_FLAG = '{FLAG}'
          AND REG_DATE = '{s_date}00'
          AND BAR_CODE = '{BAR_CODE}'
          AND SEQ = '{SEQ}'""".format(PUT_FLAG = PUT_FLAG, s_date = s_date, FLAG = FLAG, BAR_CODE = BAR_CODE, SEQ = SEQ)
        try:
            cursor_item.execute(sql_item.encode('utf-8'))
            db.commit()
            logging.debug('updateEdgeSeq : 성공')
        except:
            db.rollback()
            logging.debug('updateEdgeSeq : 실패')
    
    #################################################################################################################################
    #작업지시바코드 PROCEDURE
    def PR_SAVE_MAKE(self, GUBUN, GUBUN_SUB, EMPL_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, REG_DATE, QTY, BADN_QTY):
        oi_retn = cursor_item.callproc('PR_SAVE_MAKE', [0, 'MES', GUBUN, GUBUN_SUB, EMPL_CODE, COMP_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, REG_DATE, QTY, BADN_QTY, 0])
        if oi_retn[11] == 0:
            logging.debug("PR_SAVE_MAKE : 프로시져 성공")
        elif oi_retn[11] < 0:
            db.rollback()
            logging.debug("PR_SAVE_MAKE : 프로시져 실패")
    
    #작업지시바코드 PROCEDURE
    def PR_SAVE_MAKE_BAR_DETAIL(self, GUBUN, GUBUN_SUB, EMPL_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, BAR_CODE, REG_DATE, QTY, BADN_QTY):
        oi_retn = cursor_item.callproc('PR_SAVE_MAKE_BAR', (0, 'MES', GUBUN, GUBUN_SUB, EMPL_CODE, COMP_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, BAR_CODE, REG_DATE, QTY, BADN_QTY, 0))
        if oi_retn[13] == 0:
            logging.debug("PR_SAVE_MAKE_BAR_DETAIL : 프로시져 성공")
        elif oi_retn[13] < 0:
            db.rollback()
            logging.debug("PR_SAVE_MAKE_BAR_DETAIL : 프로시져 실패")
    
    #작업지시바코드 PROCEDURE
    def PR_SAVE_MAKE_BAR(self, GUBUN, GUBUN_SUB, EMPL_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, BAR_CODE, REG_DATE, QTY, BADN_QTY):
        oi_retn = cursor_item.callproc('PR_SAVE_MAKE_BAR', (0, 'MES', GUBUN, GUBUN_SUB, EMPL_CODE, COMP_CODE, JAKUP_NO, JAKUP_SEQ, JAKUP_SORT_KEY, BAR_CODE, REG_DATE, QTY, BADN_QTY, 0))
        if oi_retn[13] == 0:
            db.commit()
            logging.debug("PR_SAVE_MAKE_BAR : 프로시져 성공")
            result = 1
        elif oi_retn[13] < 0:
            db.rollback()
            logging.debug("PR_SAVE_MAKE_BAR : 프로시져 실패")
            result = 2
            
        return result
    
    #ERP 데이터 실시간 적용
    def SELECT_PR_PASS_JAKUP_MAKE(self):
        try:
            sql_item ="SELECT COUNT(1) MES_APPR FROM FG_MAKE_DETAIL WHERE MES_APPR_FLAG = '0'"
            cursor_item.execute(sql_item)
            MES_APPR = cursor_item.fetchone()
            #----------------------------------------------------------------------------
            if int(MES_APPR['MES_APPR']) > 0:
                sql_item ="SELECT DISTINCT LK_JAKUP_NO FROM FG_MAKE_DETAIL WHERE MES_APPR_FLAG = '0'"
                cursor_item.execute(sql_item)
                JAKUP_NO = cursor_item.fetchall()
                #----------------------------------------------------------------------------
                if JAKUP_NO != ():
                    for no in JAKUP_NO: oi_retn = cursor_item.callproc('PR_PASS_JAKUP_MAKE', (COMP_CODE, no['LK_JAKUP_NO'], '%', '%', 0))
                    if oi_retn[4] == 0:
                        db.commit()
                        logging.debug("PR_PASS_JAKUP_MAKE : db.commit()")
                    elif oi_retn[4] < 0:
                        raise('PR_PASS_JAKUP_MAKE')
        except:
            db.rollback()
            logging.debug("PR_PASS_JAKUP_MAKE : db.rollback()")

