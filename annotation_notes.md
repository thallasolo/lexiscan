## Week 1 – OCR Quality Evaluation

OCR was performed on scanned legal PDF contracts using Tesseract OCR after converting PDF pages to images.
The extracted text output was manually reviewed before annotation.

Observations:
- Party names such as organization names were readable and correctly extracted
- Dates present in the contracts were clear and interpretable
- Monetary values and legal terms were visible without major corruption
- Minor spacing issues and occasional line breaks were observed but did not affect meaning

Conclusion:
The OCR quality is sufficient for manual annotation using a Doccano-compatible workflow and for training a Named Entity Recognition (NER) model.

