import cv2
import pytesseract
import time
from gpiozero import LED
from time import sleep

# Define the GPIO pin where the LED is connected
led = LED(17)  # GPIO 17

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def detect_numbers(frame):
    # Define the region of interest (ROI) where the numbers are located
    roi = frame[100:300, 200:400]  # Example coordinates

    # Convert ROI to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding and morphological operations in a single step
    thresh = cv2.morphologyEx(
        cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2), 
        cv2.MORPH_CLOSE, 
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    )

    # OCR with a whitelist of numbers and a decimal point
    config = "--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789."
    text = pytesseract.image_to_string(thresh, config=config)

    # Extract numbers and allow one decimal point
    numbers = ''.join(char for char in text if char.isdigit() or char == '.')
    if numbers.count('.') > 1:
        numbers = numbers.split('.')[0] + '.' + numbers.split('.')[1][:1]  # Keep only one decimal

    return numbers, roi

def main():
    # Initialize camera with HD resolution
    cap = cv2.VideoCapture(0)  # Use 0 for default camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    previous_number = None
    candidate_number = None
    candidate_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Detect numbers and preprocess ROI
        numbers, roi = detect_numbers(frame)

        # Draw a rectangle around the detected region for user corrections
        cv2.rectangle(frame, (200, 100), (400, 300), (0, 255, 0), 2)

        # Display live feed and detected ROI for user corrections
        cv2.imshow("Live Camera Feed", frame)

        # User can correct the region with mouse click
        def mouse_click(event, x, y, flags, param):
            nonlocal roi
            if event == cv2.EVENT_LBUTTONDOWN:
                roi = frame[y-100:y+100, x-200:x+200]  # Update ROI based on user input

        cv2.setMouseCallback("Live Camera Feed", mouse_click)

        if numbers:
            if numbers != candidate_number:
                candidate_number = numbers
                candidate_time = time.time()
            elif time.time() - candidate_time >= 0.01:  # Confirm after 10ms
                if candidate_number != previous_number:
                    print(f"Detected Numbers: {candidate_number}")
                    previous_number = candidate_number
                    if '.' in candidate_number and candidate_number.count('.') == 1:
                        led.on()   # Turn LED on if upcounting
                    else:
                        led.off()  # Turn LED off for non-numeric or downcount
        else:
            led.off()  # Ensure LED is off if no numbers are detected

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
