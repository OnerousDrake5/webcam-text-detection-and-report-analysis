import os
import re
import pandas as pd
import pdfplumber
import cv2
import easyocr
import time
from flask import Flask, render_template, request, send_file, redirect

app = Flask(__name__)

# Ensure uploads folder exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=True)

# Global variable for storing detected text from webcam
detected_text = []

def process_pdf(pdf_path):
    """Extract text and process test results from a PDF."""
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():  # Ensure the page has meaningful text
                results.append({"Page": page.page_number, "Content": text.strip()})
    return pd.DataFrame(results)  # Convert results to a DataFrame

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and processing."""
    if 'pdf' not in request.files:
        return "Error: No file uploaded!"

    file = request.files['pdf']
    pdf_path = os.path.join('uploads', file.filename)
    file.save(pdf_path)

    # Process the uploaded PDF file
    results = process_pdf(pdf_path)
    if results.empty:  # Explicitly check if the DataFrame is empty
        return "No data found in the uploaded PDF."

    # Save results to CSV
    csv_path = os.path.join('uploads', 'processed_results.csv')
    results.to_csv(csv_path, index=False, sep='|', encoding='utf-8')

    return render_template('result.html', csv_file='processed_results.csv')

@app.route('/start-webcam', methods=['POST'])
def start_webcam():
    """Start webcam text detection with continuous visualization and key press for capturing."""
    global detected_text
    detected_text = []  # Clear previous results

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    if not cap.isOpened():
        return "Error: Cannot access webcam!"

    # Variables for frame processing
    frame_count = 0
    process_every_n_frames = 10  # Only process every 10th frame
    last_results = []  # Store the last detected results

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Only perform text detection every n frames
        if frame_count % process_every_n_frames == 0:
            try:
                results = reader.readtext(frame)
                if results:  # Only update if we detected something
                    last_results = results
            except Exception as e:
                print(f"Error in text detection: {e}")
                continue

        # Draw boxes using the last known results
        for (bbox, text, prob) in last_results:
            if prob > 0.6:  # Confidence threshold
                try:
                    # Extract bounding box coordinates
                    (x_min, y_min) = bbox[0]
                    (x_max, y_max) = bbox[2]

                    # Convert coordinates to integers for OpenCV
                    x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])

                    # Draw bounding box
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                    # Add text label
                    cv2.putText(frame, text, (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                except Exception as e:
                    print(f"Error drawing boxes: {e}")
                    continue

        # Display the frame with boxes
        cv2.imshow("Webcam Text Detection (Press Space to Capture, Q to Quit)", frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            # Save all currently detected text
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            for (_, text, prob) in last_results:
                if prob > 0.6:
                    detected_text.append(f"{timestamp} | {text}")
                    print(f"Captured: {text}")  # Debug print
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Redirect to review page after detection ends
    return redirect('/review-webcam-text')


@app.route('/review-webcam-text')
def review_webcam_text():
    """Review the detected text from the webcam."""
    return render_template('review.html', detected_text=detected_text)

@app.route('/save-webcam-text', methods=['POST'])
def save_webcam_text():
    """Save detected text from the webcam as a .txt file."""
    if not detected_text:
        return "No text to save!"

    output_path = os.path.join('uploads', 'webcam_detected_text.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(detected_text))

    return send_file(output_path, as_attachment=True, mimetype='text/plain')

@app.route('/download-csv/<filename>')
def download_csv(filename):
    """Download the processed CSV file."""
    return send_file(
        os.path.join('uploads', filename),
        as_attachment=True,
        mimetype="text/csv"
    )

if __name__ == "__main__":
    app.run(debug=True)
