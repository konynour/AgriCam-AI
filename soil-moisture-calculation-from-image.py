import cv2
import numpy as np
import serial
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# ---------- CONFIG ----------
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200
Gbp = 133.89
CSV_LOG_FILE = "moisture_log.csv"
PLOT_WINDOW_SIZE = 10  # Number of recent entries to show
# ----------------------------

def estimate_soil_moisture(Gmean):
    if Gmean > Gbp:
        return ((Gmean - (-1727.7232) - 74.107143 * 19.03) / 19.020563) * 1.034
    else:
        return ((Gmean - 137.12 - 2.566448 * 19.03) / -2.593588) * 1.166

def classify_moisture(sm_value):
    if sm_value < 20:
        return "Dry"
    elif 20 <= sm_value <= 31:
        return "Moist"
    else:
        return "Wet"

def analyze_row(mask, row_label, masked_img, ser):
    pixels = cv2.countNonZero(mask)
    B, G, R, _ = cv2.mean(masked_img, mask=mask)
    sm = estimate_soil_moisture(G)
    moisture_class = classify_moisture(sm)

    print(f"\n{row_label}:")
    print(f"  RGB Mean: [{round(R, 2)}, {round(G, 2)}, {round(B, 2)}]")
    print(f"  Pixels: {pixels}")
    print(f"  Soil Moisture: {round(sm, 2)}")
    print(f"  Classification: {moisture_class}")

    if moisture_class == "Dry":
        status = "Start irrigation"
        ser.write(f"{status} in {row_label}\n".encode())
    elif moisture_class == "Moist":
        status = "Sufficient"
    else:
        status = "Stop irrigation"
        ser.write(f"{status} in {row_label}\n".encode())

    print(f"   {status} in {row_label}")
    return round(sm, 2), moisture_class, status

def log_to_csv(sm1, class1, status1, sm2, class2, status2):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(CSV_LOG_FILE, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now, sm1, class1, status1, sm2, class2, status2])

def live_plot():
    try:
        df = pd.read_csv(CSV_LOG_FILE, header=None,
                         names=["Timestamp", "SM1", "Class1", "Status1", "SM2", "Class2", "Status2"])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Only show last N readings
        df = df.tail(PLOT_WINDOW_SIZE)

        plt.clf()  # Clear previous frame
        plt.plot(df['Timestamp'], df['SM1'], label='Row 1', marker='o', color='blue')
        plt.plot(df['Timestamp'], df['SM2'], label='Row 2', marker='o', color='green')
        plt.xlabel('Time')
        plt.ylabel('Soil Moisture')
        plt.title('Soil Moisture Over Time (Live Update)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.pause(0.1)
    except Exception as e:
        print("Plotting error:", e)

def main():
    print("\n--- Starting New Capture ---")
    print("Current time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
    except serial.SerialException:
        print(f"Could not open port {SERIAL_PORT}. Check the connection.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot access camera.")
        return

    ret, img = cap.read()
    cap.release()
    if not ret:
        print("Failed to capture image.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_filename = f"original_image_{timestamp}.jpg"
    cv2.imwrite(original_filename, img)

    # Define ROIs
    mask1 = np.zeros(img.shape[:2], dtype=np.uint8)
    mask2 = np.zeros(img.shape[:2], dtype=np.uint8)
    vertices1 = np.array([(50, 300), (200, 300), (200, 450), (50, 450)], np.int32)
    vertices2 = np.array([(400, 300), (600, 300), (600, 450), (400, 450)], np.int32)
    cv2.fillConvexPoly(mask1, vertices1, 1)
    cv2.fillConvexPoly(mask2, vertices2, 1)

    masked_img = cv2.bitwise_and(img, img, mask=mask1 | mask2)
    masked_filename = f"masked_image_{timestamp}.jpg"
    cv2.imwrite(masked_filename, masked_img)

    sm1, class1, status1 = analyze_row(mask1, "Row 1", masked_img, ser)
    sm2, class2, status2 = analyze_row(mask2, "Row 2", masked_img, ser)

    # Label image
    cv2.putText(masked_img, f"Row 1: {class1}", (60, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(masked_img, f"Row 2: {class2}", (410, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("Soil Moisture Classification", masked_img)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    log_to_csv(sm1, class1, status1, sm2, class2, status2)
    live_plot()
    ser.close()

# ----------- LOOP -----------
if __name__ == "__main__":
    plt.ion()  # Turn on interactive mode
    while True:
        try:
            main()
        except Exception as e:
            print("Error:", e)
        print("Waiting 30 seconds...\n")
        time.sleep(30)
