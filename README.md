README

Project Overview

This project is a Flask-based web application that facilitates two primary functionalities:

PDF Text Extraction: Upload a PDF document, extract text from it, and save the extracted data in a CSV file.

Webcam Text Detection: Use the webcam to detect text in real-time, capture the detected text, and save it to a file.

It leverages libraries such as EasyOCR for text detection, pdfplumber for PDF text extraction, and OpenCV for webcam access and visualization.

Features

1. PDF Text Extraction

Upload a PDF through the web interface.

Extract text from each page of the PDF.

Save the extracted text as a CSV file with page numbers and content.

2. Webcam Text Detection

Start a webcam feed to detect text in real-time.

Draw bounding boxes around detected text on the live feed.

Capture text using the space bar and save it with timestamps.

Save the detected text as a .txt file.

3. File Management

Processed files (CSV and text files) are saved in an uploads directory.

Download processed files directly from the web interface.

Prerequisites

Python 3.7+

Libraries:

Flask

EasyOCR

OpenCV

pdfplumber

pandas

A webcam for the text detection functionality.

Installation and Setup

Clone the repository:

git clone <repository_url>
cd <repository_folder>

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open the application in your browser:

http://127.0.0.1:5000/

Usage

Uploading and Processing PDFs

Navigate to the home page.

Upload a PDF document.

View the extracted text and download the resulting CSV file.

Webcam Text Detection

Start the webcam text detection from the interface.

Use the live feed to visualize detected text.

Press the space bar to capture detected text.

Press 'Q' to quit and review captured text.

Save the captured text as a .txt file.

File Structure

.
|-- app.py                  # Main application file
|-- uploads/                # Directory for uploaded and processed files
|-- templates/              # HTML templates for the web interface
    |-- index.html          # Home page
    |-- result.html         # PDF results page
    |-- review.html         # Webcam review page

Known Issues and Limitations

Webcam detection may experience lag depending on system performance.

EasyOCR might not detect all text in low-quality frames or PDFs.

No explicit support for PDFs with non-standard encodings or heavy images.

Future Improvements

Add support for multi-language text detection.

Improve error handling and logging.

Optimize webcam processing for better real-time performance.

Add user authentication and file management features.

License

This project is open-source and available under the MIT License.

