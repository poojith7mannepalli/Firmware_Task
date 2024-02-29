import serial
import time
serial_port = '/dev/ttyUSB0' 
baud_rate = 2400
text = """Finance Minister Arun Jaitley Tuesday hit out at former RBI governor Raghuram Rajan for predicting that the next banking crisis would be triggered by MSME lending, saying postmortem is easier than taking action when it was required. Rajan, who had as the chief economist at IMF warned of impending financial crisis of 2008, in a note to a parliamentary committee warned against ambitious credit targets and loan waivers, saying that they could be the sources of next banking crisis. Government should focus on sources of the next crisis, not just the last one.

In particular, government should refrain from setting ambitious credit targets or waiving loans. Credit targets are sometimes achieved by abandoning appropriate due diligence, creating the environment for future NPAs," Rajan said in the note." Both MUDRA loans as well as the Kisan Credit Card, while popular, have to be examined more closely for potential credit risk. Rajan, who was RBI governor for three years till September 2016, is currently."""


ser = serial.Serial(serial_port, baud_rate, timeout=1)

def send_data(text):
    start_time = time.time()
    ser.write(text.encode())
    ser.flush()  
    bytes_sent = len(text)
    end_time = time.time()
    calculate_speed(bytes_sent, start_time, end_time, "Sending")

def receive_data(expected_bytes):
    received_data = b''
    start_time = time.time()
    while len(received_data) < expected_bytes:
        if ser.in_waiting > 0:
            received_data += ser.read(ser.in_waiting)
    end_time = time.time()
    calculate_speed(len(received_data), start_time, end_time, "Receiving")
    return received_data.decode()

def calculate_speed(bytes_count, start_time, end_time, operation):
    time_elapsed = end_time - start_time  
    speed_bps = (bytes_count * 8) / time_elapsed  
    print(f"{operation} speed: {speed_bps:.2f} bps")

send_data(text)


time.sleep(10)


print("Starting to receive data...")
received_text = receive_data(1000) 
print("Received Text:", received_text[:1000] + "...")  

ser.close()  

