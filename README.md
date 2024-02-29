# FIRMWARE TASK
### PC to MCU and MCU to PC UART Data Transmission with STM32G0B1RE
## Overview
This project demonstrates a firmware implementation for transmitting a predefined text from a PC to an MCU ( STM32G0B1RE) via UART, storing it in EEPROM emulation, and then transmitting it back from the MCU to the PC. The firmware measures the real-time data transmission speed in bits per second, showcasing the efficiency and reliability of UART communication for embedded systems.

### Features
UART Communication: Utilizes UART protocol for full-duplex communication between the PC and the MCU.
EEPROM Emulation: Employs the MCU's flash memory to emulate EEPROM storage, allowing for persistent storage of received data.
Data Transmission Speed Measurement: Calculates the actual transmission speed based on the number of bits transmitted over the UART bus per second, providing insights into the communication efficiency.

### How It Works

Initialization: The system initializes all peripherals, including UART1 for PC communication . GPIOs are also configured, particularly for indicating operation status through an LED.

Receiving Data: The PC sends a block of text to the MCU via UART1. The MCU receives the data byte by byte, storing each byte into an EEPROM emulation region within its flash memory.

Storing Data: Data is buffered into a 64-bit (double-word) variable before being written to the flash memory to optimize flash write operations, considering the STM32G0's flash programming capabilities.

Transmitting Data Back: After receiving and storing the entire text, the MCU reads the stored data from the flash and sends it back to the PC through UART1.

Measuring Transmission Speed: The transmission speed is calculated by measuring the time taken to transmit the text and the number of bits transmitted, providing a real-time data transmission speed display on the PC.

Function Descriptions
EEPROM_WRITE(uint32_t address, uint64_t data): Writes a double word (64 bits) of data to a specific flash address, emulating EEPROM storage.
```c
void EEPROM_WRITE(uint32_t address, uint64_t data) {
    uint32_t writeAddress = EEPROM_EMULATION_ADDRESS + address * DOUBLE_WORD_SIZE;
    HAL_FLASH_Unlock();
    HAL_FLASH_Program(FLASH_TYPEPROGRAM_FAST, writeAddress, data);

    HAL_FLASH_Lock();
}
```
EEPROM_Read(uint32_t address, uint8_t *data, uint32_t length): Reads a block of data from the emulated EEPROM storage, starting from the specified address.
```c
void EEPROM_Read(uint32_t address, uint8_t *data, uint32_t length) {
    uint32_t readAddress = EEPROM_EMULATION_ADDRESS + address * DOUBLE_WORD_SIZE;
    for (uint32_t i = 0; i < length; i += DOUBLE_WORD_SIZE) {
        uint64_t tempData = *(uint64_t *)(readAddress + i);
        uint32_t bytesToCopy = (i + DOUBLE_WORD_SIZE > length) ? length % DOUBLE_WORD_SIZE : DOUBLE_WORD_SIZE;
        memcpy(&data[i], &tempData, bytesToCopy);
    }
}
```
BufferAndWriteEEPROM(uint8_t data): Buffers incoming data bytes until a full double word is accumulated, then writes it to the emulated EEPROM storage.
```c
void BufferAndWriteEEPROM(uint8_t data) {
    ((uint8_t*)&DoubleWordBuffer)[DoubleWordBufferIndex++] = data;
    if (DoubleWordBufferIndex == DOUBLE_WORD_SIZE) {
        EEPROM_WRITE(RxIndex / DOUBLE_WORD_SIZE, DoubleWordBuffer);
        DoubleWordBuffer = 0;
        DoubleWordBufferIndex = 0;
    }
}
```
HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart): Callback function for UART receive complete interrupt. It handles the reception of data bytes from the PC, buffers them, and triggers EEPROM storage or data transmission back to the PC.
```c
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        if (RxIndex < RX_BUFFER_SIZE) {
            BufferAndWriteEEPROM(RxBuffer[RxIndex]);
            RxIndex++;

            if (RxIndex == RX_BUFFER_SIZE) {

                if (DoubleWordBufferIndex > 0) {
                    EEPROM_WRITE(RxIndex / DOUBLE_WORD_SIZE, DoubleWordBuffer);
                }
                TransmitBack();
            } else {
                HAL_UART_Receive_IT(&huart1, &RxBuffer[RxIndex], 1);
            }
        }
    }
}
```
TransmitBack(void): Retrieves the stored data from EEPROM emulation and transmits it back to the PC via UART.
```c
void TransmitBack(void) {
    uint8_t dataToTransmit[RX_BUFFER_SIZE];
    EEPROM_Read(0, dataToTransmit, RX_BUFFER_SIZE);
    HAL_UART_Transmit(&huart1, dataToTransmit, RX_BUFFER_SIZE, HAL_MAX_DELAY);
}
```

Setup and Running
Hardware Setup: Connect the STM32G0B1RE to your PC using a UART to USB converter. Ensure proper connection of UART1 pins for RX and TX. To communicate between MCU to PC i planned on using USB to TTL Converter.
![20240228_191234](https://github.com/poojith7mannepalli/Firmware_Task/assets/66217036/53cb2df6-9cef-483f-bc9a-21a70cb97a40)
![20240228_191311](https://github.com/poojith7mannepalli/Firmware_Task/assets/66217036/9d8f5a88-cea1-4d77-a3c4-e5b46e24b999)

Software Requirements: This project requires STM32CubeIDE for compiling and flashing the firmware onto the STM32G0B1RE.I made sure that i had set the BaudRate to 2400.
#### To view the project code navigate to [Core->src->main.c] in main.c you can view the source code and in the [PC_REALTED->Firmware_Task.py] you can find the code for PC realted sending and receiving data
Flashing the Firmware: Open the project in STM32CubeIDE, compile it, and flash it onto the MCU.

Running the PC Application: Used python in VsCode
### Firmware_Task PC related Code
## Importing Libraries
```python

import serial
import time
```
These lines import the necessary Python libraries. The serial library is used for serial communication (you'll need pySerial installed in your environment), and the time library is used for handling time-related tasks, such as adding delays.

## Setting Up Serial Connection
```python

serial_port = '/dev/ttyUSB0'
baud_rate = 2400
```
Here, you're specifying the serial port (/dev/ttyUSB0, common for Linux systems) and the baud rate (2400) for the serial communication. These values should be adjusted based on your actual hardware setup and the requirements of the device you're communicating with.

## The Text Variable
```python

text = """Finance Minister Arun Jaitley... currently."""
This multiline string is the data you intend to send over the serial connection. It appears to be a snippet of a news article.
```
## Opening the Serial Connection
````python

ser = serial.Serial(serial_port, baud_rate, timeout=1)
```
This line opens the serial port with the specified baud rate and a read timeout of 1 second. A timeout is useful to avoid blocking the code indefinitely if no data is received.

## The send_data Function
```python

def send_data(text):
    start_time = time.time()
    ser.write(text.encode())
    ser.flush()
    bytes_sent = len(text)
    end_time = time.time()
    calculate_speed(bytes_sent, start_time, end_time, "Sending")
```
This function sends the provided text over the serial port. It measures the time taken to send the data and calculates the sending speed in bits per second (bps). The flush() method ensures that all written data is sent out immediately.

## The receive_data Function
```python

def receive_data(expected_bytes):
    received_data = b''
    start_time = time.time()
    while len(received_data) < expected_bytes:
        if ser.in_waiting > 0:
            received_data += ser.read(ser.in_waiting)
    end_time = time.time()
    calculate_speed(len(received_data), start_time, end_time, "Receiving")
    return received_data.decode()
```
This function waits to receive a specified number of bytes over the serial port, measuring the time taken and calculating the receiving speed in bps. It continues reading data until the expected number of bytes is received or the timeout occurs. The received data is then decoded from bytes to a string before being returned.

## The calculate_speed Function
```python

def calculate_speed(bytes_count, start_time, end_time, operation):
    time_elapsed = end_time - start_time
    speed_bps = (bytes_count * 8) / time_elapsed
    print(f"{operation} speed: {speed_bps:.2f} bps")
```
This utility function calculates and prints the speed of the operation (sending or receiving) in bps.

## Executing the Communication
```python

send_data(text)

time.sleep(10)

print("Starting to receive data...")
received_text = receive_data(1000)
print("Received Text:", received_text[:1000] + "...")

ser.close()
```
This part of the code sends the text, waits for 10 seconds (presumably to allow the receiving side to process and start sending data back), and then attempts to receive up to 1000 bytes of data. Finally, it closes the serial connection.


