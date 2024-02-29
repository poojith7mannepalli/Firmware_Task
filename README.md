# FIRMWARE TASK
###PC to MCU and MCU to PC UART Data Transmission with STM32G0B1RE
##Overview
This project demonstrates a firmware implementation for transmitting a predefined text from a PC to an MCU ( STM32G0B1RE) via UART, storing it in EEPROM emulation, and then transmitting it back from the MCU to the PC. The firmware measures the real-time data transmission speed in bits per second, showcasing the efficiency and reliability of UART communication for embedded systems.

###Features
UART Communication: Utilizes UART protocol for full-duplex communication between the PC and the MCU.
EEPROM Emulation: Employs the MCU's flash memory to emulate EEPROM storage, allowing for persistent storage of received data.
Data Transmission Speed Measurement: Calculates the actual transmission speed based on the number of bits transmitted over the UART bus per second, providing insights into the communication efficiency.

###How It Works

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

TransmitBack(void): Retrieves the stored data from EEPROM emulation and transmits it back to the PC via UART.
```c
void TransmitBack(void) {
    uint8_t dataToTransmit[RX_BUFFER_SIZE];
    EEPROM_Read(0, dataToTransmit, RX_BUFFER_SIZE);
    HAL_UART_Transmit(&huart1, dataToTransmit, RX_BUFFER_SIZE, HAL_MAX_DELAY);
}


Setup and Running
Hardware Setup: Connect the STM32G0B1RE to your PC using a UART to USB converter. Ensure proper connection of UART1 pins for RX and TX.

Software Requirements: This project requires STM32CubeIDE for compiling and flashing the firmware onto the STM32G0B1RE.

Flashing the Firmware: Open the project in STM32CubeIDE, compile it, and flash it onto the MCU.

Running the PC Application: Use a serial terminal or a custom PC application to send the predefined text to the MCU and receive the transmitted data back.

Contributing
Contributions to this project are welcome. Please ensure to follow the coding standards and submit pull requests for any enhancements, bug fixes, or feature additions.
