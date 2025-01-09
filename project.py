import cv2
import pytesseract
from gpiozero import LED

# Define the GPIO pins where LEDs are connected
led_upcount = LED(17)  # GPIO 17 for upcount
led_downcount = LED(27)  # GPIO 27 for downcount

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def detect_numbers(frame):
    # Define a smaller region of interest (ROI)
    roi = frame[250:550, 450:750]  # Adjust coordinates for smaller ROI

    # Convert ROI to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Apply a simple threshold for faster processing
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # OCR configuration for faster detection
    config = "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(thresh, config=config)

    # Extract valid integers (ignore decimals and negatives)
    numbers = ''.join(char for char in text if char.isdigit())

    return int(numbers) if numbers.isdigit() else None

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

        # Detect numbers in the frame
        detected_number = detect_numbers(frame)

        # Only process if the detected number is different from the previous one
        if detected_number is not None and detected_number != previous_number:
            print(f"Detected Number: {detected_number}, Previous Number: {previous_number}")

            # LED logic for upcount and downcount
            if previous_number is not None:
                try:
                    current_number = float(detected_number)
                    prev_number = float(previous_number)

                    # Check for missing numbers
                    if current_number == prev_number + 1:  # Upcount sequence
                        led_upcount.off()
                        led_downcount.off()  # Ensure downcount LED is off in upcount sequence
                    elif current_number == prev_number - 1:  # Downcount sequence
                        led_upcount.off()  # Ensure upcount LED is off in downcount sequence
                        led_downcount.off()
                    else:  # Missing number detected
                        if current_number > prev_number + 1:  # Missing number in upcount
                            print(f"Missing number detected: {prev_number + 1}")
                            led_upcount.on()
                            led_downcount.off()  # Ensure downcount LED is off
                        elif current_number < prev_number - 1:  # Missing number in downcount
                            print(f"Missing number detected: {prev_number - 1}")
                            led_downcount.on()
                            led_upcount.off()  # Ensure upcount LED is off

                except ValueError:
                    print(f"Invalid number format: {detected_number}")
                    led_upcount.off()
                    led_downcount.off()

            # Update the previous number after processing
            previous_number = detected_number

        # Draw a rectangle around the ROI for visualization
        cv2.rectangle(frame, (450, 250), (750, 550), (0, 255, 0), 2)

        # Display the camera feed
        cv2.imshow("Camera Feed", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
