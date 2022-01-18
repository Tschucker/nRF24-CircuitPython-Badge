#NRF24L01 CircuitPython Badge Test
import board
import neopixel
import time
import struct
from adafruit_pybadger import pybadger
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24

# set this to 0 or 1 for the two badges
radio_number = 0
# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]
# using the python keyword global is bad practice. Instead we'll use a 1 item
# list to store our float number for the payloads sent
payload = [0.0, 5]

SPI_BUS = board.SPI()  # init spi bus object
CE_PIN = DigitalInOut(board.D6) 
CSN_PIN = DigitalInOut(board.D5)

try: 
    # initialize the nRF24L01 on the spi bus object
    nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

    # set the Power Amplifier level to -12 dBm since this test example is
    # usually run with nRF24L01 transceivers in close proximity
    nrf.pa_level = 0

    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

    # uncomment the following 3 lines for compatibility with TMRh20 library
    # nrf.allow_ask_no_ack = False
    # nrf.dynamic_payloads = False
    # nrf.payload_length = 4
    # nrf.power = True
    nrf.auto_ack = False
    
except:
    print("Cannot find NRF24")
      

pybadger.show_terminal()
state = "init"

while True:
    if pybadger.button.a:
        if state != "tx":
            print("Button A")
            print("State TX")
            state = "tx"
            try:
                nrf.listen = False  # ensures the nRF24L01 is in TX mode
            except:
                print("Failed nrf listen")
                #state = "idle"
            count = 0
    elif pybadger.button.b:
        if state != "rx":
            print("Button B")
            print("State RX")
            state = "rx"
            try:
                nrf.listen = True  # put radio into RX mode and power up
            except:
                print("Failed nrf listen")
                #state = "idle"
    elif pybadger.button.start:
        if state != "idle":
            print("Button start")
            print("State idle")
            state = "idle"
    elif pybadger.button.select:
        if state != "set":
            print("Button select")
            print("State settings")
            state = "set"
            try:
                nrf.print_details()
            except:
                print("Failed nrf settings")
                #state = "idle"

        
    if state == "tx":
        try:
            # use struct.pack to packetize your data
            # into a usable payload
            buffer = struct.pack("<f", payload[0])
            print(count)
            # "<f" means a single little endian (4 byte) float value.
            start_timer = time.monotonic_ns()  # start timer
            result = nrf.send(buffer)
            end_timer = time.monotonic_ns()  # end timer
            if not result:
                print("send() failed or timed out")
                state = "idle"
            else:
                print(
                    "Tx successful! Time to Tx:",
                    f"{(end_timer - start_timer) / 1000} us. Sent: {payload[0]}"
                )
                payload[0] += 0.01
            time.sleep(1)
            count += 1
        except:
            print("Failed TX")
            count = 0
            #state = "idle"
        
    elif state == "rx":
        try:
            if nrf.available():
                # grab information about the received payload
                payload_size, pipe_number = (nrf.any(), nrf.pipe)
                # fetch 1 payload from RX FIFO
                buffer = nrf.read()  # also clears nrf.irq_dr status flag
                # expecting a little endian float, thus the format string "<f"
                # buffer[:4] truncates padded 0s if dynamic payloads are disabled
                payload[0] = struct.unpack("<f", buffer[:4])[0]
                # print details about the received packet
                print(f"Rx {payload_size} bytes on pipe {pipe_number}: {payload[0]}")
        except:
            print("Failed RX")
            #state = "idle"
            
    elif state == "set":
        if pybadger.button.up:
            print("Button up")
        elif pybadger.button.down:
            print("Button down")
        