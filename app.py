from time import sleep
from tkinter import *
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.util import toHexString
from tkinter.font import Font
 

import getData
#import getSerial
from PIL import ImageTk, Image
import mydb
 
import serial
import configparser
 
config = configparser.RawConfigParser()
config.read('app-config.ini')
serialport=config.get('HOSxP','serialport')
 
# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    def __init__(self,cid,sysValue,diaValue,pulseVvalue,sysInfo,serialport,baudrate):
        self.observer = ConsoleCardConnectionObserver()
        config = configparser.RawConfigParser()
        config.read('app-config.ini')
        serialport=config.get('HOSxP','serialport')

        self.cid = cid
        self.sysValue = sysValue
        self.diaValue = diaValue
        self.pulseVvalue = pulseVvalue
        self.sysInfo = sysInfo
        self.baud_rate = '9600'
        self.serialport = serialport

        self.sysInfo.set("-- กรุณาเสียบบัตรประจำตัวประชาชน --")
        

    def open_serial_port(self):
        try:
            self.serial = serial.Serial(serialport, 9600, timeout=1)
        # Rest of your code
        except Exception as e:
            print("Error opening serial port:", str(e))
        #self.serial = serial.Serial(serialport, 9600, timeout=1)
        self.serial.close()
        try:
            if not self.serial.is_open:
                self.serial.open()
                print("Serial port opened.")
            else:
                print("Serial port is already open.")


        except Exception as e:
            print("Error opening serial port:", str(e))
            self.sysInfo.set(str(e))
            
        else:
            if self.serial.is_open:
            
                # Read data from the pressure gauge
                while True:
                    try:
                        data = self.serial.readline().decode().strip()
                    except Exception as e:
                        print("Error opening serial port:", str(e))
                    # Check if there is data
                    if data:
                        print("Received data:", data)

                    # Break the loop if 'q' is entered
                    if data == 'q':
                        break

                    # Split the data by comma
                    split_data = data.split(",")

                    # Remove any leading or trailing whitespace from each value
                    split_data = [value.strip() for value in split_data]
                    
                    print(len(split_data))
                    if len(split_data) >= 8:

                    # Extract the desired values
                        value1 = split_data[7]
                        value2 = split_data[8]
                        value3 = split_data[9]
                
            # Print the extracted values
                        print("Value 1:", value1)
                        print("Value 2:", value2)
                        print("Value 2:", value3)
                        return split_data


    





    def close_serial_port(self):
        if self.serial.is_open:
            self.serial.close()
            print("Serial port closed.")
        else:
            print("Serial port is already closed.")

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
            self.sysInfo.set("--กำลังอ่านข้อมูลจากบัตร--")

            cid=getData.checkCard()

            if len(cid)==13:
                self.sysInfo.set("--กรุณาสอดแขนเข้าเครื่องวัดความดัน--")
                dataResult =self.open_serial_port()
                #dataResult =returnDataUSB()
                
                if len(dataResult) >= 8:
                    sysValue = dataResult[7]
                    diaValue = dataResult[8]
                    pulseVvalue = dataResult[9]
                    update_opdscreen(cid,sysValue,diaValue,pulseVvalue)
                else:
                    print("Err")

                

            #self.cid.set(cid)
            self.sysValue.set(sysValue)
            self.diaValue.set(diaValue)
            self.pulseVvalue.set(pulseVvalue)
            self.sysInfo.set("-- วัดความดันเรียบร้อยแล้ว --")
            

        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            mydb.updateCardStatus(False)
            self.sysValue.set("")
            self.diaValue.set("")
            self.pulseVvalue.set("")
            self.sysInfo.set("-- กรุณาเสียบบัตรประจำตัวประชาชน --")
            break


 

def update_opdscreen(cid,bps,bpd,pulse):
    sql = "SELECT vn FROM ovst o INNER JOIN patient p on p.hn = o.hn WHERE p.cid =%s AND o.vstdate =date(NOW()) \
        ORDER BY o.vn desc LIMIT 1"
  
    vn=""
    try:
        connection = mydb.getConnection()
        connection.autocommit(True)
        cursor = connection.cursor()
        cursor.execute(sql, (cid))# 1 row.
        results = cursor.fetchall()
        for row in results:
            vn = row['vn']
        print("VN :"+vn)
                  
    except:
        print("Not Found Database")
        exit
   
    else:
        sql_update = "UPDATE opdscreen SET bps=%s,bpd=%s,pulse=%s,pulse_regulation_type_id=1 WHERE vn=%s"
        sql_get_serial="select get_serialnumber('opdscreen_bp_id') as cc"
        sql_opsscreen_bp = "select * from opdscreen_bp where vn=%s"
        sql_delete ="delete from opdscreen_bp where vn=%s"
        sql_insert ="insert into opdscreen_bp (opdscreen_bp_id,vn,screen_date,screen_time,staff,bps,bpd,hos_guid,depcode,rr,pulse,o2sat,temperature,bfr,vp,dp,ufr,vol_remove,nursing_care_text,opdscreen_bp_loc_type_id,opdscreen_bp_ret_type_id) VALUES (%s,%s,date(now()),time(now()),NULL,%s,%s,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)"
        if vn!="":
            cursor.execute(sql_update, (bps,bpd,pulse,vn))# 1 row.
            cursor.execute(sql_get_serial)# 1 row.       
            results_id = cursor.fetchall()
            for row in results_id:
                opdscreenbp_id = row['cc']
            print(opdscreenbp_id)
            cursor.execute(sql_delete,(vn))# 1 row.
            cursor.execute(sql_insert, (opdscreenbp_id,vn,bps,bpd))# 1 row.        
            print("Successful Update")
        else:
            print("UnSuccessful Update Not Found VN")      
    finally:  
        cursor.close()
        connection.close()
    return



def gui():
    
    root = Tk()
    root.geometry('1300x600')
    root['bg']='#235D3A'
    root.title("smartBP | ระบบส่งข้อมูลเครื่องวัดความดัน")
    root.iconbitmap('heartbeats.ico')

    cid = StringVar()
    ptName = StringVar()
    ptBirth = StringVar()
    sysValue = StringVar()
    diaValue = StringVar()
    pulseVvalue = StringVar()
    sysInfo = StringVar()
    serialport = StringVar()
    baudrate = StringVar()

    big_digit_font1 = Font(family="Helvetica", size=40, weight="bold")
    big_digit_font2 = Font(family="Tahoma", size=60, weight="bold")
    big_digit_font3 = Font(family="Tahoma", size=40, weight="bold")

    labelframe = LabelFrame(root, text="ข้อมูลบัตรประชาชน",font=("Tahoma",12),width='300',height='190')
    #labelframe.grid(row=1,column=0,sticky="NSEW",padx=10,pady=10,rowspan=5)

    #Title
    label_title = Label(root,textvariable=sysInfo,font=big_digit_font1,bg='#235D3A',fg='#FFEDF6')
    label_title.place(x=270,y=20)

    label_cid = Label(root, text="เลขบัตรประชาชน",font=("Tahoma", 14),anchor='e')
    #label_cid.grid(row=2,column=0,sticky="W",padx=15)

    label_name = Label(root, text="ชื่อ-นามสกุล",font=("Tahoma", 14),anchor='e')
    #label_name.grid(row=3,column=0,sticky="W",padx=15)

    label_birth = Label(root, text="อายุ",font=("Tahoma", 14),anchor='e')
    #label_birth.grid(row=4,column=0,sticky="W",padx=15)

    lbl_cid = Label(root, width=20, textvariable=cid,font=("Tahoma", 14),anchor='w')
    #lbl_cid.grid(row=2,column=0,padx=100)

    lbl_name = Label(root, width=20, textvariable=ptName,font=("Tahoma", 10),anchor='w')
    #lbl_name.grid(row=3,column=0,padx=100)

    lbl_birth = Label(root, width=20, textvariable=ptBirth,font=("Tahoma", 10),anchor='w')
    #lbl_birth.grid(row=4,column=0,padx=100)


     

    label_sys = Label(root, text="SYS",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    label_sys.place(x=750,y=150)
    label_mmhg = Label(root, text="mmHg",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg.place(x=785,y=210)

    label_dia = Label(root, text="DIA",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    label_dia.place(x=750,y=300)
    label_mmhg1 = Label(root, text="mmHg",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg1.place(x=785,y=360)

    label_dia = Label(root, text="PULSE",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    label_dia.place(x=680,y=450)
    label_mmhg2 = Label(root, text="/min",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg2.place(x=790,y=510)

     
    label_sysResult = Label(root, width=5, textvariable=sysValue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_sysResult.place(x=870,y=150)

    label_diaResult = Label(root, width=5, textvariable=diaValue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_diaResult.place(x=870,y=300)


    label_pulseResult = Label(root, width=5, textvariable=pulseVvalue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_pulseResult.place(x=870,y=450)



    image_path = "card_image.png"
    tk_image = ImageTk.PhotoImage(file=image_path)

    # Create a label and display the image
    image_label = Label(root, image=tk_image)
    image_label.place(x=100,y=150)


    print("Insert or remove a smartcard in the system.")
    print("This program will exit in 10 seconds")
    print("")
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver(cid,sysValue,diaValue,pulseVvalue,sysInfo,serialport,baudrate)
    cardmonitor.addObserver(cardobserver)
    
    root.mainloop()
    
if __name__ == '__main__':
    gui()
    