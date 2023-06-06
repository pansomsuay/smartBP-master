
import serial
import configparser
 
config = configparser.RawConfigParser()
config.read('app-config.ini')
serialport=config.get('HOSxP','serialport')

def returnDataUSB():
    
    print("Insert or remove a smartcard in the system.")
    print("Press Ctrl+C to exit.")

    
    try:
        # Keep the program running
        #while True:
            baud_rate = 9600  # Update this with the appropriate baud rate

            # Create a serial object
            ser = serial.Serial(serialport, baud_rate, timeout=1)

    # Open the serial connection
            ser.close()
            ser.open()


            # Check if the serial connection is open
            if ser.is_open:
                print("Serial connection is open.")

                # Read data from the pressure gauge
                while True:
                    
                    data = ser.readline().decode().strip()

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
                        
            else:
                print("Insufficient data elements in the list.")
            # Close the serial connection
            ser.close()
            pass

    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C)
        pass

   