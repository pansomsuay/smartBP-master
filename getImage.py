
#เรียกใช้ module ที่มาจาก pyscard สำหรับดึงข้อมูลจากบัตร

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from resizeimage import resizeimage
from PIL import Image
import glob

def photoCard(fileName): #อ่านไฟล์รูป
    cardtype = AnyCardType()
    cardrequest = CardRequest( timeout=1, cardType=cardtype )
    cardservice = cardrequest.waitforcard()
    cardservice.connection.connect()

    SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
    THAI_ID_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    REQ_PHOTO_P1 = [0x80,0xB0,0x01,0x7B,0x02,0x00,0xFF]
    REQ_PHOTO_P2 = [0x80,0xB0,0x02,0x7A,0x02,0x00,0xFF]
    REQ_PHOTO_P3 = [0x80,0xB0,0x03,0x79,0x02,0x00,0xFF]
    REQ_PHOTO_P4 = [0x80,0xB0,0x04,0x78,0x02,0x00,0xFF]
    REQ_PHOTO_P5 = [0x80,0xB0,0x05,0x77,0x02,0x00,0xFF]
    REQ_PHOTO_P6 = [0x80,0xB0,0x06,0x76,0x02,0x00,0xFF]
    REQ_PHOTO_P7 = [0x80,0xB0,0x07,0x75,0x02,0x00,0xFF]
    REQ_PHOTO_P8 = [0x80,0xB0,0x08,0x74,0x02,0x00,0xFF]
    REQ_PHOTO_P9 = [0x80,0xB0,0x09,0x73,0x02,0x00,0xFF]
    REQ_PHOTO_P10 = [0x80,0xB0,0x0A,0x72,0x02,0x00,0xFF]
    REQ_PHOTO_P11 = [0x80,0xB0,0x0B,0x71,0x02,0x00,0xFF]
    REQ_PHOTO_P12 = [0x80,0xB0,0x0C,0x70,0x02,0x00,0xFF]
    REQ_PHOTO_P13 = [0x80,0xB0,0x0D,0x6F,0x02,0x00,0xFF]
    REQ_PHOTO_P14 = [0x80,0xB0,0x0E,0x6E,0x02,0x00,0xFF]
    REQ_PHOTO_P15 = [0x80,0xB0,0x0F,0x6D,0x02,0x00,0xFF]
    REQ_PHOTO_P16 = [0x80,0xB0,0x10,0x6C,0x02,0x00,0xFF]
    REQ_PHOTO_P17 = [0x80,0xB0,0x11,0x6B,0x02,0x00,0xFF]
    REQ_PHOTO_P18 = [0x80,0xB0,0x12,0x6A,0x02,0x00,0xFF]
    REQ_PHOTO_P19 = [0x80,0xB0,0x13,0x69,0x02,0x00,0xFF]
    REQ_PHOTO_P20 = [0x80,0xB0,0x14,0x68,0x02,0x00,0xFF]

    PHOTO = [REQ_PHOTO_P1,REQ_PHOTO_P2,REQ_PHOTO_P3,REQ_PHOTO_P4,REQ_PHOTO_P5,
    REQ_PHOTO_P6,REQ_PHOTO_P7,REQ_PHOTO_P8,REQ_PHOTO_P9,REQ_PHOTO_P10,REQ_PHOTO_P11
    ,REQ_PHOTO_P12,REQ_PHOTO_P13,REQ_PHOTO_P14,REQ_PHOTO_P15,REQ_PHOTO_P16,REQ_PHOTO_P17,
    REQ_PHOTO_P18,REQ_PHOTO_P19,REQ_PHOTO_P20]
    
    apdu = SELECT+THAI_ID_CARD
    response, sw1, sw2 = cardservice.connection.transmit( apdu )

    ### Fetch and write photo บันทึกรูปภาพ
    fphoto = open('images/'+fileName+".png", "wb")
    for d in PHOTO:
        response, sw1, sw2 = cardservice.connection.transmit( d )
        if sw1 == 0x61:
            GET_RESPONSE = [0X00, 0XC0, 0x00, 0x00 ]
            apdu = GET_RESPONSE + [sw2]
            response, sw1, sw2 = cardservice.connection.transmit( apdu )
            fphoto.write(bytearray(response))
            #BackUpPhoto.write(bytearray(response))

def resizeImg(fileName): #ปรับขนาดรูป
    for name in glob.glob('images/'+fileName+".png"):
                print("ddd")
                with open(name, 'r+b') as f: 
                    print(name)
                    with Image.open(f) as image:
                        print(f)
                        print(image.format)
                        cover = resizeimage.resize_width(image, 148)
                        cover = resizeimage.resize_cover(cover, [148, 165])
                        cover.save(name, image.format)
                        print("d")


def resizeImg2(fileName):
    filePattern = 'images/' + fileName + '.png'
    files = glob.glob(filePattern)
    
    if len(files) == 0:
        print(f"No file found matching the pattern: {filePattern}")
        return
    
    for name in files:
        try:
            with Image.open(name) as image:
                cover = resizeimage.resize_width(image, 90)
                cover = resizeimage.resize_cover(cover, [90, 110])
                cover.save(name, image.format)
                print(f"Resized image: {name}")
        except Exception as e:
            print(f"Error resizing image {name}: {e}")


#resizeImg2("card_temp")








