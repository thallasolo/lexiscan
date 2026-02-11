import time
import os
import requests

WATCH_DIR = "data/raw_pdfs"
API_URL = "http://localhost:8000/extract"

processed = set()

while True:
    for file in os.listdir(WATCH_DIR):
        if file.endswith(".pdf") and file not in processed:
            pdf_path = os.path.join(WATCH_DIR, file)
            print(f"📄 New PDF detected: {file}")

            with open(pdf_path, "rb") as f:
                response = requests.post(
                    API_URL,
                    files={"pdf": f}
                )

            print("HTTP Status:", response.status_code)
            print("RAW Response Text:\n", response.text)

            processed.add(file)

    time.sleep(5)
