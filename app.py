from time import sleep
from tkinter import *
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.util import toHexString
from tkinter.font import Font
from tkinter import ttk

import getData
#import getSerial
from PIL import ImageTk, Image
import mydb
import os
import serial
import configparser
import logging
import getImage
import threading

 
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')
 
config = configparser.RawConfigParser()
config.read('app-config.ini')
serialport=config.get('HOSxP','serialport')

class TimeoutError(Exception):
    pass
 
# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    def __init__(self,cid,sysValue,diaValue,pulseVvalue,sysInfo,serialport,baudrate,canvas,canvas_background,progress_bar,barcode_entry,canvas_bacode):
        self.observer = ConsoleCardConnectionObserver()
        config = configparser.RawConfigParser()
        config.read('app-config.ini')
        serialport=config.get('HOSxP','serialport')

        self.font1 = Font(family="Tahoma", size=10, weight="bold")
        self.font2 = Font(family="Tahoma", size=12, weight="bold")
        self.font3 = Font(family="Tahoma", size=30, weight="bold")

        self.cid = cid
        self.sysValue = sysValue
        self.diaValue = diaValue
        self.pulseVvalue = pulseVvalue
        self.sysInfo = sysInfo
        self.baud_rate = '9600'
        self.serialport = serialport
        #self.image_label = image_label
        self.canvas = canvas
        self.canvas_background = canvas_background
        global text_item_id 
        self.progressbar = progress_bar
        self.serial = None
        #self.sysInfo.set("-- กรุณาเสียบบัตรประจำตัวประชาชน --")
        self.text_item_id=self.canvas_background.create_text(750, 50, text="-- กรุณาเสียบบัตรประจำตัวประชาชน --",fill='#fff',font=self.font3)
        self.barcode_entry= barcode_entry
        self.canvas_bacode = canvas_bacode
    
    def open_serial_port(self):
        try:
            
            self.serial = serial.Serial(serialport, 9600, timeout=1)
            
        # Rest of your code
        except Exception as e:
            print("Error opening serial port:", str(e))
            logging.error('Line 68'+str(e))
         
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
            logging.error('Line 82'+str(e))
            
        else:
            if self.serial.is_open:
                
                # Read data from the pressure gauge
                while True:
                    try:
                        data = self.serial.readline().decode().strip()
                    except Exception as e:
                        print("Error opening serial port:", str(e))
                        logging.error('Line'+str(e))
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

######################## Run with timeount ##############################

    def run_with_timeout(self, func, timeout_seconds):
        # Create an event object to communicate between threads
        self.event = threading.Event()

        def timeout_func():
            self.event.wait(timeout_seconds)  # Wait for the specified timeout
            if not self.event.is_set():
                self.event.set()
                raise TimeoutError("Function timed out")

        # Create a thread for the timeout function
        self.timeout_thread = threading.Thread(target=timeout_func)

        try:
            self.timeout_thread.start()  # Start the timeout thread
            self.result = func()  # Run the function
            self.event.set()  # Set the event to indicate successful completion
            self.timeout_thread.join()  # Wait for the timeout thread to finish
            return self.result
        except TimeoutError:
            print("Function timed out")
            self.progressbar.place_forget()
            self.progressbar.stop()
            exit
            # Handle the timeout error as desired

############## Card Monitor ##############################################

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
            
            #Progress bar
            self.progressbar.place(x=100, y=450)
            self.progressbar.start()
             
            self.canvas_background.delete(self.text_item_id)
            self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- กำลังอ่านข้อมูลจากบัตร--",fill='#fff',font=self.font3)

            #insert image 
            self.canvas.delete('all')
            self.image_path = r"images/card_insert.png"
            self.image = Image.open(self.image_path)
            self.tk_image = ImageTk.PhotoImage(file=self.image_path)
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=NW, image=self.tk_image)
            
            #ลบ barcode_entry 

            self.barcode_entry.place_forget()
            self.canvas_bacode.place_forget()
            
            # Read CID
            try:
                cid = self.run_with_timeout(getData.checkCard, 10)
                print("Function completed successfully")
            except TimeoutError:
                print("Function execution exceeded the timeout")

                logging.error('CID 155'+str(e))
                self.progressbar.stop()
                self.progressbar.place_forget()
                self.canvas_background.delete(self.text_item_id)
                self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- ไม่สามารถอ่านข้อมูลจากบัตร --",fill='#fff',font=self.font3)
                break
                #self.canvas_background.delete(self.text_item_id)
                #self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- กรุณาเสียบบัตรประจำตัวประชาชน --",fill='#fff',font=self.font3)
        
            else:
                
                try:
                    TH_name=getData.getTHFullname()
                except Exception as e:
                    logging.error(str(e))
                    logging.error("Cannot get TH_name")
                    prefix_name = ""
                    first_name = ""
                    last_name = ""
                    logging.error(str(e))
                    self.progressbar.stop()
                    self.progressbar.place_forget()
                    self.canvas_background.delete(self.text_item_id)
                    self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- ไม่สามารถอ่านข้อมูลจากบัตร --",fill='#fff',font=self.font3)
                    break
                    
                else:
                    split_name = str(TH_name).split(" ")
                    if len(split_name) >= 2:
                        prefix_name = split_name[0]
                        first_name = split_name[1]
                        last_name = split_name[3]

                try:
                    date_birth = getData.getDateofbirth()
                except Exception as e:
                    logging.error('191 Date of birth'+str(e))
                    
                    date_birth = ""
                     
                    self.progressbar.stop()
                    self.progressbar.place_forget()
                    self.canvas_background.delete(self.text_item_id)
                    self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- ไม่สามารถอ่านข้อมูลจากบัตร --",fill='#fff',font=self.font3)
                    break
                    
                #resize image
                try:
                    getImage.photoCard("card_temp")
                except Exception as e:
                    logging.error(str(e))
                    logging.error("Cannot get Image")
                    logging.error(str(e))
                    self.progressbar.stop()
                    self.progressbar.place_forget()
                    self.canvas_background.delete(self.text_item_id)
                    self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="-- ไม่สามารถอ่านข้อมูลจากบัตร --",fill='#fff',font=self.font3)
                    break

                else:
                    check_image=getImage.resizeImg2("card_temp")
                    print(check_image)
                    if check_image =='Y':
                        self.image_path_card = r"images/card_temp.png"

                        self.image_card = Image.open(self.image_path_card)
                        self.tk_image_card = ImageTk.PhotoImage(file=self.image_path_card)
                        self.image_item_id=self.canvas.create_image(367, 178, image=self.tk_image_card)
                    else:

                        pass
                 
                
                if len(cid)==13:
                    self.canvas.create_text(320, 50, text=cid,fill='#000',font=self.font2)
                    #self.canvas.create_text(270, 75, text=TH_name,fill='#000',font=font2)
                    
                    self.canvas.create_text(170, 90, text=prefix_name,fill='#000',font=self.font1,anchor="w")
                    self.canvas.create_text(200, 90, text=first_name,fill='#000',font=self.font1,anchor="w")
                    self.canvas.create_text(200, 110, text=last_name,fill='#000',font=self.font1,anchor="w")
                    self.canvas.create_text(210, 130, text=date_birth,fill='#000',font=self.font1,anchor="w")

                    self.progressbar.place_forget()
                    self.progressbar.stop()

                    self.canvas_background.delete(self.text_item_id)
                    self.text_item_id=self.text_item_id=self.canvas_background.create_text(750, 50, text="--กรุณาสอดแขนเข้าเครื่องวัดความดัน--",fill='#fff',font=self.font3)

                    try:
                        dataResult =self.open_serial_port()
                    except Exception as e:
                        logging.error(str(e))
                    else:                   
                        if len(dataResult) >= 8:
                            sysValue = dataResult[7]
                            diaValue = dataResult[8]
                            pulseVvalue = dataResult[9]

                            update_opdscreen(cid,sysValue,diaValue,pulseVvalue)

                            #แสดงผลค่าความดัน
                            self.close_serial_port()
                            self.sysValue.set(sysValue)
                            self.diaValue.set(diaValue)
                            self.pulseVvalue.set(pulseVvalue)
                            #self.sysInfo.set("-- วัดความดันเรียบร้อยแล้ว --")
                            self.canvas_background.delete(self.text_item_id)
                            self.text_item_id=self.canvas_background.create_text(750, 50, text="-- วัดความดันเรียบร้อยแล้ว --",fill='#fff',font=self.font3)

                        else:
                            print("Err")
                            pass
                    

        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
             
            self.canvas.delete(self.image_item_id)

            #Insert card card_image
            self.image_path = r"images/card_image.png"
            self.image = Image.open(self.image_path)
            self.tk_image = ImageTk.PhotoImage(file=self.image_path)
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=NW, image=self.tk_image)
            
            #Insert canvas barcode
            #Barcodenimage
             
            canvas_bacode.place(x=100,y=601)
            canvas_bacode.create_image(0, 0, anchor=NW, image=tk_image_bacode)

            #Clear 
            self.sysValue.set("")
            self.diaValue.set("")
            self.pulseVvalue.set("")
            #self.sysInfo.set("-- กรุณาเสียบบัตรประจำตัวประชาชน --")
            self.canvas_background.delete(self.text_item_id)
            self.text_item_id=self.canvas_background.create_text(750, 50, text="-- กรุณาเสียบบัตรประจำตัวประชาชน --",fill='#fff',font=self.font3)
            self.barcode_entry.place(x=162,y=600)
             
             
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
                  
    except Exception as e:
        logging.error(str(e))
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
            logging.info("Update :"+vn)
        else:
            print("UnSuccessful Update Not Found VN")
            logging.error("Error in update :"+vn)      
    finally:  
        cursor.close()
        connection.close()
    return


def on_entry_click(event):
    if barcode_entry.get() == 'Enter barcode...':
        barcode_entry.delete(0, tk.END)
        barcode_entry.configure(fg='black')

def on_entry_leave(event):
    if barcode_entry.get() == '':
        barcode_entry.insert(0, 'Enter barcode...')
        barcode_entry.configure(fg='gray')

def on_barcode_change(*args):
    barcode = barcode_var.get()
    # Do something with the scanned barcode
    print("Scanned barcode:", barcode)
    

def toggle_visibility():
    if canvas_bacode.itemcget(image_id, "state") == "hidden":
        canvas_bacode.itemconfigure(image_id, state="normal")
    else:
        canvas_bacode.itemconfigure(image_id, state="hidden")
    canvas_bacode.after(500, toggle_visibility)  # Toggle visibility every 500 milliseconds

def gui():
    global barcode_entry,barcode_var,canvas_bacode,image_id,tk_image_bacode
    
    root = Tk()
    root.geometry('1300x600')
    #root.attributes('-fullscreen', True)
    root['bg']='#235D3A'
    root.title("smartBP | ระบบส่งข้อมูลเครื่องวัดความดัน")
    root.iconbitmap('images/heartbeats.ico')
    
    # Create a canvas to draw the gradient background
    canvas_background = Canvas(root, width=1600, height=1200)  # Adjust the size of the canvas as per your requirements
    canvas_background.pack()

     
# Define the colors for the gradient
    color1 = "#235D3A"  # Start color (white)
    color2 = "#c0c0c0"  # End color (light gray)

# Create the gradient background
    for y in range(1200):  # Adjust the range as per the height of the canvas
        # Calculate the intermediate color based on the y-coordinate
            r = int(color1[1:3], 16) + (int(color2[1:3], 16) - int(color1[1:3], 16)) * y // 1200
            g = int(color1[3:5], 16) + (int(color2[3:5], 16) - int(color1[3:5], 16)) * y // 1200
            b = int(color1[5:7], 16) + (int(color2[5:7], 16) - int(color1[5:7], 16)) * y // 1200

        # Convert the RGB values to hexadecimal
            color = f"#{r:02x}{g:02x}{b:02x}"

        # Create a rectangle with the calculated color
            canvas_background.create_rectangle(0, y, 1600, y + 1, fill=color, outline="")



# Quit the application when Esc key is pressed
    root.bind('<Escape>', lambda event: root.quit())

    cid = StringVar()
    ptName = StringVar()
    ptBirth = StringVar()
    sysValue = StringVar()
    diaValue = StringVar()
    pulseVvalue = StringVar()
    sysInfo = StringVar()
    serialport = StringVar()
    baudrate = StringVar()
    barcode_var = StringVar()

    big_digit_font1 = Font(family="Tahoma", size=40, weight="bold")
    big_digit_font2 = Font(family="Tahoma", size=60, weight="bold")
    big_digit_barcode = Font(family="Tahoma", size=40, weight="bold")



    #label_sys = Label(root, text="SYS",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    #label_sys.place(x=750,y=150)
    label_mmhg = Label(root, text="mmHg",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg.place(x=785,y=210)

    label_dia = Label(root, text="DIA",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    #label_dia.place(x=750,y=300)
    label_mmhg1 = Label(root, text="mmHg",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg1.place(x=785,y=360)

    label_dia = Label(root, text="PULSE",font=big_digit_font1,anchor='e',bg='#235D3A',fg='#fff')
    #label_dia.place(x=680,y=450)
    label_mmhg2 = Label(root, text="/min",font=("Tahoma", 16),anchor='e',bg='#235D3A',fg='#fff')
    label_mmhg2.place(x=790,y=510)

     
    label_sysResult = Label(root, width=5, textvariable=sysValue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_sysResult.place(x=870,y=150)

    label_diaResult = Label(root, width=5, textvariable=diaValue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_diaResult.place(x=870,y=300)

    label_pulseResult = Label(root, width=5, textvariable=pulseVvalue,font=big_digit_font2,bg='#74927A',fg='#fff',anchor='center')
    label_pulseResult.place(x=870,y=450)

    #ใส่รูปภาพ card_image
    image_path = r"images/card_image.png"
    image = Image.open(image_path)
    tk_image = ImageTk.PhotoImage(file=image_path)
    canvas = Canvas(root, width=image.width, height=image.height,highlightthickness=0, relief='ridge')

    canvas.place(x=100,y=150)
    canvas.create_image(0, 0, anchor=NW, image=tk_image)
    
    #Label ค่าความดัน
    canvas_background.create_text(800, 180, text="SYS",fill='#fff',font=big_digit_font1)
    canvas_background.create_text(800, 330, text="DIA",fill='#fff',font=big_digit_font1)
    canvas_background.create_text(760, 480, text="PULSE",fill='#fff',font=big_digit_font1)

    #Progress Bar
    progress_bar = ttk.Progressbar(root, mode="indeterminate" ,length=430)
    
    #Barcode Scan
    barcode_var.trace('w', on_barcode_change)
    barcode_entry = Entry(root,font=big_digit_barcode,width=10,textvariable=barcode_var)
    barcode_entry.place(x=162,y=600)
    barcode_entry.focus_set()

    #Barcodenimage
    image_path_bacode = r"images/scan_barcode_resize.png"
    image_bacode = Image.open(image_path)
    tk_image_bacode = ImageTk.PhotoImage(file=image_path_bacode)
    canvas_bacode = Canvas(root, width=66, height=67,highlightthickness=0, relief='ridge',bg='#fff')
    canvas_bacode.place(x=100,y=601)
    canvas_bacode.create_image(0, 0, anchor=NW, image=tk_image_bacode)
     

    #Card Monitor
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver(cid,sysValue,diaValue,pulseVvalue,sysInfo,serialport,baudrate,canvas,canvas_background,progress_bar,barcode_entry,canvas_bacode)
    cardmonitor.addObserver(cardobserver)

    root.mainloop()
    




if __name__ == '__main__':
    gui()
    