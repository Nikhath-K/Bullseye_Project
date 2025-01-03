import cv2
import pytesseract
from gpiozero import LED
from time import sleep

# Define the GPIO pins where LEDs are connected
led_upcount = LED(17)  # GPIO 17 for upcount
led_downcount = LED(27)  # GPIO 27 for downcount

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def detect_numbers(frame):
    # Define the region of interest (ROI) where the numbers are located
    roi = frame[100:300, 200:400]  # Example coordinates

    # Convert ROI to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # OCR with a whitelist of numbers and a decimal point
    config = "--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789."
    text = pytesseract.image_to_string(thresh, config=config)

    # Extract numbers and allow one decimal point
    numbers = ''.join(char for char in text if char.isdigit() or char == '.')
    if numbers.count('.') > 1:
        numbers = numbers.split('.')[0] + '.' + numbers.split('.')[1][:1]  # Keep only one decimal

    return numbers

def main():
    # Initialize camera with HD resolution
    cap = cv2.VideoCapture(0)  # Use 0 for default camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    previous_number = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Detect numbers and preprocess ROI
        numbers = detect_numbers(frame)

        # Validate detected numbers
        if numbers:
            if numbers != previous_number:
                print(f"Detected Numbers: {numbers}")

                try:
                    if previous_number:
                        current_number = float(numbers)
                        prev_number = float(previous_number)
                        if current_number > prev_number:
                            led_upcount.on()  # Turn on LED for upcount
                            led_downcount.off()  # Turn off LED for downcount
                        elif current_number < prev_number:
                            led_downcount.on()  # Turn on LED for downcount
                            led_upcount.off()  # Turn off LED for upcount
                        else:
                            led_upcount.off()
                            led_downcount.off()

                        previous_number = numbers
                except ValueError:
                    print(f"Invalid number format: {numbers}")
                    led_upcount.off()
                    led_downcount.off()
        else:
            if previous_number:
                print(f"No new number detected. Retaining previous number: {previous_number}")

        # Draw a rectangle around the ROI for visualization
        cv2.rectangle(frame, (200, 100), (400, 300), (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Camera Feed", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
