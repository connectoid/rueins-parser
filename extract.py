from datetime import datetime

import fitz
import pypdfium2 as pdfium


time1 = datetime.now()
pdffile = "file.pdf"
doc = fitz.open(pdffile)
page = doc.load_page(0)  # number of page
pix = page.get_pixmap()
output = "outfile.png"
pix.save(output)
doc.close()
time2 = datetime.now()
print(f'fitz: {time2 - time1}')


time1 = datetime.now()
# Load a document
pdf = pdfium.PdfDocument("file.pdf")

# Loop over pages and render
page = pdf[0]
image = page.render(scale=4).to_pil()
image.save(f"output.jpg")
time2 = datetime.now()
print(f'fitz: {time2 - time1}')
