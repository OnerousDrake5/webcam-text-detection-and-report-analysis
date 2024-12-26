from flask import Flask, render_template, request, Response
import cv2
import easyocr
import time
import fitz  # PyMuPDF for PDF processing
import os

app = Flask(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=True)

# Initialize a list to collect detected text
detected_text = []

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and text extraction."""
    global detected_text
    detected_text = []  # Reset detected text

    # Check if a file was uploaded
    if 'pdf' not in request.files:
        return "Error: No file uploaded!"

    file = request.files['pdf']

    # Save the uploaded file
    pdf_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)  # Ensure the uploads directory exists
    file.save(pdf_path)

    # Process the PDF
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pdf_text = page.get_text()

        if pdf_text.strip():
            detected_text.append(f"Page {page_num + 1}:
{pdf_text.strip()}")
        else:
            # If no text is found, render page as image and process with OCR
            pix = page.get_pixmap(dpi=150)
            img_path = f"uploads/page_{page_num + 1}.png"
            pix.save(img_path)

            image_results = reader.readtext(img_path)
            for (_, text, prob) in image_results:
                if prob > 0.6:
                    detected_text.append(f"Page {page_num + 1} OCR: {text}")

            os.remove(img_path)

    pdf_document.close()

    # Redirect to results page
    return render_template('result.html', detected_text=detected_text)

@app.route('/webcam')
def webcam():
    """Render the webcam detection page."""
    return render_template('webcam.html')

@app.route('/start-webcam', methods=['POST'])
def start_webcam():
    """Start webcam text detection with bounding boxes."""
    global detected_text
    detected_text = []  # Clear previous results

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        return "Error: Cannot access webcam!"

    detection_interval = 3  # Time in seconds between detections
    last_detection_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Get the current time
        current_time = time.time()

        if current_time - last_detection_time >= detection_interval:
            # Perform text detection
            results = reader.readtext(frame)

            for (bbox, text, prob) in results:
                if prob > 0.6:  # Confidence threshold
                    (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]

                    # Draw bounding box
                    cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

                    # Add text label
                    cv2.putText(frame, text, (int(x_min), int(y_min) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                    # Save detected text
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    detected_text.append(f"{timestamp} | Webcam: {text}")

            last_detection_time = current_time

        # Display the frame with bounding boxes
        cv2.imshow("Webcam Text Detection", frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Redirect to results page after detection ends
    return render_template('result.html', detected_text=detected_text)

@app.route('/download-results', methods=['GET'])
def download_results():
    """Download detected text as a file."""
    output = "\n".join(detected_text)
    return Response(
        output,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=detected_text.txt"}
    )

@app.route('/results')
def results():
    """Display the detected text."""
    return render_template('result.html', detected_text=detected_text)

if __name__ == '__main__':
    # Ensure the uploads folder exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)