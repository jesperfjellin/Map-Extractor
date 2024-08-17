# PDF Map Text Extractor

This Python script enables users to extract text information from specific regions of scanned paper maps stored as PDFs. It allows for easy selection of a Region of Interest (ROI) on one page and then scans the same area across all pages in the PDF, performing Optical Character Recognition (OCR) to extract text. The results are saved in a CSV file for easy analysis and retrieval.

## What is OCR?
Optical Character Recognition (OCR) is a technology that converts different types of documents, such as scanned paper documents, PDFs, or images captured by a digital camera, into editable and searchable data. This script uses OCR to recognize and extract textual information from scanned map images.

## About Tesseract
Tesseract is a popular open-source OCR engine maintained by Google. It supports multiple languages and is highly effective at extracting text from images, making it ideal for processing scanned documents like maps. In this script, Tesseract is used to perform OCR on the selected regions of the map images.
