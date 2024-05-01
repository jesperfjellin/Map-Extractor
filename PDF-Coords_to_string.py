import tkinter as tk
from tkinter import Canvas, filedialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pytesseract
import csv
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def select_pdf_file():
    """ Open a file dialog to select a PDF file and return its path. """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    root.destroy()  # Destroy the root after selection
    return pdf_path

def extract_page_image(pdf_path, page_number):
    """ Extract a specific page of the given PDF and convert it to a PIL Image. """
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def select_roi(image):
    """ Allow the user to select a Region of Interest (ROI) on the image using mouse drag in a Tkinter window. """
    root = tk.Tk()
    root.title("Select Region of Interest (ROI)")
    photo_image = ImageTk.PhotoImage(image)
    canvas = Canvas(root, width=photo_image.width(), height=photo_image.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)

    rect_start = {}
    rect_obj = None

    def on_drag(event):
        nonlocal rect_obj
        if 'start_x' in rect_start:
            if rect_obj:
                canvas.delete(rect_obj)
            rect_obj = canvas.create_rectangle(rect_start['start_x'], rect_start['start_y'], event.x, event.y, outline='red')

    def on_click(event):
        rect_start['start_x'] = event.x
        rect_start['start_y'] = event.y

    def on_release(event):
        nonlocal rect_obj
        if rect_obj:
            rect_start['end_x'] = event.x
            rect_start['end_y'] = event.y
            canvas.delete(rect_obj)
        root.quit()

    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    
    root.mainloop()

    if 'end_x' in rect_start:
        return (min(rect_start['start_x'], rect_start['end_x']), 
                min(rect_start['start_y'], rect_start['end_y']),
                abs(rect_start['end_x'] - rect_start['start_x']), 
                abs(rect_start['end_y'] - rect_start['start_y']))
    else:
        return None

def perform_ocr_on_roi(image, roi, scale_factor=6):
    """ Perform OCR on the selected region of interest (ROI) on the image. """
    cropped_image = image.crop((roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3]))
    
    # Scale up the cropped image
    new_width = int(cropped_image.width * scale_factor)
    new_height = int(cropped_image.height * scale_factor)
    cropped_image = cropped_image.resize((new_width, new_height))

    text = pytesseract.image_to_string(cropped_image, lang='eng', config='--psm 6')
    return text.strip()

def main():
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("No PDF file selected.")
        return

    first_page_image = extract_page_image(pdf_path, 0)
    roi_coordinates = select_roi(first_page_image)
    if not roi_coordinates:
        print("No ROI selected.")
        return

    pdf_document = fitz.open(pdf_path)
    results = []

    for page_number in range(len(pdf_document)):
        page_image = extract_page_image(pdf_path, page_number)
        extracted_text = perform_ocr_on_roi(page_image, roi_coordinates, scale_factor=6)
        results.append((page_number + 1, extracted_text))
        print(f"Page {page_number + 1}: {extracted_text}")

    # Write results to CSV
    with open(r'C:\Python\PDF-Coords_to_string\ROI_result.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Page Number', 'Extracted Text'])
        writer.writerows(results)

if __name__ == "__main__":
    main()
