import asyncio
import re
import traceback

HOST = ''  # Listening to any
PORT = 8000  # The port number of the server

async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break

        decoded_data = data.decode('utf-8', errors='ignore')
        print(f'Incoming GPS Tracker data : {decoded_data}')

        # Split the GPS data packet using regular expressions
        data_parts = re.split('[,|]+', decoded_data)

        if len(data_parts) > 15:
            # Extract information from data parts
            protocol_header = data_parts[0]
            gps_signal_status = data_parts[1]
            latitude = data_parts[2] + "." + data_parts[3]
            longitude = data_parts[4] + "." + data_parts[5]
            latitude = data_parts[2] + data_parts[3]
            longitude = data_parts[4] + data_parts[5]
            speed_knots = data_parts[6]
            course_degrees = data_parts[7]
            timestamp = data_parts[8]
            magnetic_variation = data_parts[9]
            ew_indicator = data_parts[10]
            gps_fix = data_parts[11]
            horizontal_dilution = data_parts[12]
            altitude_meters = data_parts[13]
            input_output_status = data_parts[14]
            analog_data_1 = data_parts[15]
            analog_data_2_hex = data_parts[16]  # Hexadecimal format

            # Convert hexadecimal analog_data_2 to decimal
            try:
                analog_data_2_decimal = int(analog_data_2_hex, 16)
                # Calculate external car battery voltage in volts
                battery_voltage = (analog_data_2_decimal * 6) / 1024
            except ValueError:
                analog_data_2_decimal = None
                battery_voltage = None

            odometer_meters = data_parts[17]
            rfid = data_parts[18]

            print("Device Active:", "Yes" if input_output_status != "0000" else "No")

            # Check if input and output status corresponds to specific conditions
            if input_output_status == "1000":
                print("Engine is ON")
            elif input_output_status == "1C00":
                print("Door is OPEN and Engine is ON")
            elif input_output_status == "0101":
                print("Relay is activated to stop the car and SOS button is pressed down")
            elif input_output_status == "0200":
                print("Device is disconnected from external power supply")
            elif input_output_status == "0000":
                print("Input and output devices not connected")
            else:
                print("FAULT CODE input/output status:", input_output_status)

            # Print the extracted information
            print("Protocol Header:", protocol_header)
            print("GPS Signal Status:", "Valid" if gps_signal_status == "S" else "Invalid")
            print("Latitude:", latitude)
            print("Longitude:", longitude)
            print("Speed (knots):", speed_knots)
            print("Course (degrees):", course_degrees)
            # Format timestamp as DD/MM/YYYY
            timestamp_parts = [timestamp[0:2], timestamp[2:4], "20" + timestamp[4:6]]
            formatted_timestamp = "/".join(timestamp_parts)
            print("Timestamp (DD/MM/YYYY):", formatted_timestamp)
            print("Magnetic Variation:", magnetic_variation)
            print("East/West Indicator:", "East" if ew_indicator == "E" else "West")
            print("GPS Fix:", "Valid" if gps_fix == "A" else "Invalid")
            print("Horizontal Dilution:", horizontal_dilution)
            print("Altitude (meters):", altitude_meters)
            print("Input/Output Status:", input_output_status)
            print("Device Active:", "Yes" if input_output_status != "0000" else "No")
            print("Analog Data 1:", analog_data_1)
            print("Analog Data 2 (Hexadecimal):", analog_data_2_hex)
            # Check if analog_data_2 was successfully converted to decimal
            if analog_data_2_decimal is not None:
                print("External Car Battery Voltage:", battery_voltage, "Volts")
            else:
                print("External Car Battery Voltage: Invalid Data")
            print("Total Mileage(Meters):", odometer_meters)
            print("RFID:", rfid)
        else:
            print("Loading GPRS Data Packets")

            # Send the received data back to the client using ASCII encoding
            writer.write(data)

    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
