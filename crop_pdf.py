import tkinter as tk
from tkinter import Canvas, filedialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import os

def select_pdf_file():
    """ Open a file dialog to select a PDF file and return its path. """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    root.destroy()  # Destroy the root after selection
    return pdf_path

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

def crop_pdf_to_roi(original_pdf_path, roi_coordinates):
    """ Crop each page of the original PDF to the selected ROI and save as a new PDF. """
    # Open the original PDF document
    original_pdf = fitz.open(original_pdf_path)
    
    # Create a new PDF document
    new_pdf = fitz.open()
    
    for page_number in range(len(original_pdf)):
        # Load the page
        page = original_pdf.load_page(page_number)
        
        # Get the media box (page size)
        media_box = page.rect
        
        # Adjust crop box coordinates if necessary
        x1, y1, width, height = roi_coordinates
        x2 = x1 + width
        y2 = y1 + height
        
        if x1 < media_box.x0:
            x1 = media_box.x0
        if x2 > media_box.x1:
            x2 = media_box.x1
        if y1 < media_box.y0:
            y1 = media_box.y0
        if y2 > media_box.y1:
            y2 = media_box.y1
        
        crop_box = fitz.Rect(x1, y1, x2, y2)
        
        # Crop the page to the adjusted crop box
        page.set_cropbox(crop_box)
        
        # Create a new blank page with the same size as the cropped region
        new_page = new_pdf.new_page(width=crop_box.width, height=crop_box.height)
        
        # Copy the cropped content to the new page
        new_page.insert_page(page_number, page)
    
    # Save the new PDF document with "_cropped" appended to the original file name
    output_pdf_path = original_pdf_path.replace('.pdf', '_cropped.pdf')
    new_pdf.save(output_pdf_path)
    
    # Close the PDF documents
    original_pdf.close()
    new_pdf.close()
    return output_pdf_path

def main():
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("No PDF file selected.")
        return

    original_pdf = fitz.open(pdf_path)
    first_page = original_pdf.load_page(0)
    pix = first_page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    roi_coordinates = select_roi(img)
    if not roi_coordinates:
        print("No ROI selected.")
        return

    cropped_pdf_path = crop_pdf_to_roi(pdf_path, roi_coordinates)
    print(f"PDF cropped and saved as: {cropped_pdf_path}")

if __name__ == "__main__":
    main()
