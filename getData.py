# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:34:10 2022

@author: BT
"""
import mydb
from smartcard.Exceptions import NoCardException
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.sw.SWExceptions import SWException, WarningProcessingException
 
import pymysql
import logging

#ตัวเก็บข้อมูลทุกอย่างไว้ใน list
count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
monthThai = ['null','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
monthEng = ['null','January','February','March','April','May','June','July','August','September','October','November','December']
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

try :
    SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08] # Check card
    THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d] # CID
    CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64] # TH Fullname
    CMD_ENFULLNAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64] # EN Fullname
    CMD_BIRTH = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08] # Date of birth
    CMD_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01] # Gender
    CMD_ISSUER = [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64] # Card Issuer
    CMD_ISSUE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08] # Issue Date
    CMD_EXPIRE = [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08] # Expire Date
    CMD_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64] # Address 

    # Photo_Part1/20
    CMD_PHOTO1 = [0x80, 0xb0, 0x01, 0x7B, 0x02, 0x00, 0xFF]

    # Photo_Part2/20
    CMD_PHOTO2 = [0x80, 0xb0, 0x02, 0x7A, 0x02, 0x00, 0xFF]

    # Photo_Part3/20
    CMD_PHOTO3 = [0x80, 0xb0, 0x03, 0x79, 0x02, 0x00, 0xFF]

    # Photo_Part4/20
    CMD_PHOTO4 = [0x80, 0xb0, 0x04, 0x78, 0x02, 0x00, 0xFF]

    # Photo_Part5/20
    CMD_PHOTO5 = [0x80, 0xb0, 0x05, 0x77, 0x02, 0x00, 0xFF]

    # Photo_Part6/20
    CMD_PHOTO6 = [0x80, 0xb0, 0x06, 0x76, 0x02, 0x00, 0xFF]

    # Photo_Part7/20
    CMD_PHOTO7 = [0x80, 0xb0, 0x07, 0x75, 0x02, 0x00, 0xFF]

    # Photo_Part8/20
    CMD_PHOTO8 = [0x80, 0xb0, 0x08, 0x74, 0x02, 0x00, 0xFF]

    # Photo_Part9/20
    CMD_PHOTO9 = [0x80, 0xb0, 0x09, 0x73, 0x02, 0x00, 0xFF]

    # Photo_Part10/20
    CMD_PHOTO10 = [0x80, 0xb0, 0x0A, 0x72, 0x02, 0x00, 0xFF]

    # Photo_Part11/20
    CMD_PHOTO11 = [0x80, 0xb0, 0x0B, 0x71, 0x02, 0x00, 0xFF]

    # Photo_Part12/20
    CMD_PHOTO12 = [0x80, 0xb0, 0x0C, 0x70, 0x02, 0x00, 0xFF]

    # Photo_Part13/20
    CMD_PHOTO13 = [0x80, 0xb0, 0x0D, 0x6F, 0x02, 0x00, 0xFF]

    # Photo_Part14/20
    CMD_PHOTO14 = [0x80, 0xb0, 0x0E, 0x6E, 0x02, 0x00, 0xFF]

    # Photo_Part15/20
    CMD_PHOTO15 = [0x80, 0xb0, 0x0F, 0x6D, 0x02, 0x00, 0xFF]

    # Photo_Part16/20
    CMD_PHOTO16 = [0x80, 0xb0, 0x10, 0x6C, 0x02, 0x00, 0xFF]

    # Photo_Part17/20
    CMD_PHOTO17 = [0x80, 0xb0, 0x11, 0x6B, 0x02, 0x00, 0xFF]

    # Photo_Part18/20
    CMD_PHOTO18 = [0x80, 0xb0, 0x12, 0x6A, 0x02, 0x00, 0xFF]

    # Photo_Part19/20
    CMD_PHOTO19 = [0x80, 0xb0, 0x13, 0x69, 0x02, 0x00, 0xFF]

    # Photo_Part20/20
    CMD_PHOTO20 = [0x80, 0xb0, 0x14, 0x68, 0x02, 0x00, 0xFF]
except:
    pass 

def thai2unicode(data):
    result = ''
    result = bytes(data).decode('tis-620')
    return result.strip()#strip()หมายถึงไม่เอา string ที่ไม่ต้องการ

def getData(cmd, req = [0x00, 0xc0, 0x00, 0x00]):
    r = readers()
    print ("Available readers:", r)
    reader = r[0]
    connection = reader.createConnection()
    connection.connect()
    atr = connection.getATR()
    try:
        data, sw1, sw2 = connection.transmit(cmd)
        data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
   
    except SWException as e:
        print(str(e))  
        connection.disconnect()  
        print("ERR")
    return [data, sw1, sw2];

# define the APDUs used in this script
# https://github.com/chakphanu/ThaiNationalIDCard/blob/master/APDU.md


def checkCard():
    cid=""
    TH=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                
                connection.connect()
                
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                     # CID
                    data = getData(CMD_CID, req)
                    cid = thai2unicode(data[0])
                     
                    print ("เลขประจำตัวประชาชน: " + cid)
                    return cid
                
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 170'+str(e))
                
def getENFullname():
    EN=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                      

                    # EN Fullname
                    data = getData(CMD_ENFULLNAME, req)
                    EN = thai2unicode(data[0])
                    count.append(EN)
                    EN = EN.replace('#', ' ')
                    print ("Name-LastName: " + EN)
                
                    
                    return EN
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 213'+str(e))


def getTHFullname():
    TH=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                      

                    # EN Fullname
                    data = getData(CMD_THFULLNAME, req)
                    TH = thai2unicode(data[0])
                    count.append(TH)
                    TH = TH.replace('#', ' ')
                    print ("Name-LastName: " + TH)
                
                    
                    return TH
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 257'+str(e))
                    return

def getAddress():
    TH=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                      

                    # EN Fullname
                    data = getData(CMD_ADDRESS, req)
                    address = thai2unicode(data[0])
                    count.append(address)
                    address = address.replace('#', ' ')
                    print ("address: " + address)
                
                    
                    return address
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 300'+str(e))

def getDateofbirth():
    date_birth=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                      

                    # EN Fullname
                    data = getData(CMD_BIRTH, req)
                    date_birth = thai2unicode(data[0])
                    count.append(date_birth)
                    x1 = list(thai2unicode(data[0]))
                    a = []
                    num = x1[4]+x1[5]
                    for i in  range(12):
                        if i == int(num):
                            a.append(monthThai[i])
                            a.append(monthEng[i])
                        else:
                            pass
                        
                    DATE_B = x1[-2]+x1[-1]+' '+a[0]+' '+x1[0]+x1[1]+x1[2]+x1[3]
                    a.append(int(x1[0]+x1[1]+x1[2]+x1[3])-543)
                    count.append(DATE_B)
                    print( "เกิดวันที่: " +DATE_B)

                    date_birth = date_birth.replace('#', ' ')
                    print ("Name-LastName: " + date_birth)
                
                    
                    return DATE_B
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 358'+str(e))
                    return
                                       

def getPhoto(cid):
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                     
                    print(req)
                    print(sw1)
                    print(sw2)

                    if sw1 == 0x61:
                        photo = getData(CMD_PHOTO20, req)[0]
                    
                        print(photo)
                        data = bytearray(photo)
                        print(data)

                    try:
                        data = bytearray(photo)
                        print(data)
                        with open(cid + ".png", "wb") as f:
                            f.write(data)
                            f.close()
                    except SWException as e:
                        print(str(e))
                        logging.error('Line 407'+str(e))
                        return
                
                    
                    
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))
                    logging.error('Line 413'+str(e))
                    return          
  
def getMobilePhone(cid):
    try:
        connection = mydb.getConnection()
        cursor = connection.cursor()
        sql = "SELECT REPLACE(p.hometel,'-','') as hometel FROM patient p WHERE p.cid =%s"
        cursor.execute(sql, (cid))
        
    except pymysql.InternalError as error:
        print("[ Wanning ] No Connecttion Database!!!")
    
    else:
        results = cursor.fetchall()
        if results != None:
            for row in results:
                hometel = row['hometel']
                return hometel

def getHn(cid):
    try:
        connection = mydb.getConnection()
        cursor = connection.cursor()
        sql = "SELECT REPLACE(p.hn,'-','') as hn FROM patient p WHERE p.cid =%s"
        cursor.execute(sql, (cid))
        
    except pymysql.InternalError as error:
        print("[ Wanning ] No Connecttion Database!!!")
    
    else:
        results = cursor.fetchall()
        if results != None:
            for row in results:
                hn = row['hn']
                return hn



#getPhoto('test')