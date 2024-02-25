from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

for page in writer.pages:
    for img in page.images:
        img.replace(img.image, quality=50)

with open("out.pdf", "wb") as f:
    writer.write(f)