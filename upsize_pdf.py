import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF

def resize_pdf(pdf_path, scale_factor=2, margin=10):
    """
    Resize all pages of a PDF by a specified scale factor using PyMuPDF, including margins to avoid cropping.

    Args:
    - pdf_path (str): Path to the PDF file.
    - scale_factor (float): Factor by which to scale up the pages. Default is 2.
    - margin (int): Margin size added to each side of the page to prevent cropping.

    Returns:
    - str: Path to the resized PDF file.
    """
    output_pdf_path = pdf_path.replace('.pdf', f'_resized_{scale_factor}x.pdf')

    # Open the original PDF document
    original_pdf = fitz.open(pdf_path)
    
    # Create a new PDF document
    new_pdf = fitz.open()
    
    for page in original_pdf:
        # Get the size of the original page
        rect = page.rect
        new_rect = fitz.Rect(rect.tl, rect.br * scale_factor)  # Scale the page size
        
        # Adjust for margins
        new_rect.x1 += margin * scale_factor
        new_rect.y1 += margin * scale_factor
        new_rect.x0 -= margin * scale_factor
        new_rect.y0 -= margin * scale_factor
        
        # Create a new blank page in the new PDF with the scaled size
        new_page = new_pdf.new_page(-1, width=new_rect.width + 2 * margin * scale_factor, height=new_rect.height + 2 * margin * scale_factor)
        
        # Get the page's pixmap at the scaled size and higher resolution
        pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor), dpi=300)
        
        # Insert the scaled pixmap into the new page
        new_page.insert_image(new_rect, pixmap=pix)
    
    # Save the new PDF document
    new_pdf.save(output_pdf_path)
    
    # Close the PDF documents
    original_pdf.close()
    new_pdf.close()

    return output_pdf_path

def open_file():
    """Open a file dialog to select a PDF, then resize it."""
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        scale_factor = 2  # Example scale factor
        margin = 10  # Margin size
        output_pdf_path = resize_pdf(file_path, scale_factor, margin)
        print(f"Resized PDF saved as: {output_pdf_path}")
        tk.messagebox.showinfo("Success", f"Resized PDF saved as:\n{output_pdf_path}")
    root.destroy()  # Close the application

if __name__ == "__main__":
    root = tk.Tk()
    open_file()
