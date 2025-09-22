import pymupdf

pdf_path = "input_pdf/000776_广发证券_2024.pdf"
document = pymupdf.open(pdf_path)

toc = document.get_toc()


print(toc)
