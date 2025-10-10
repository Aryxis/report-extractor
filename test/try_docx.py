import logging
from pdf2docx import Converter
import time

# # 将第三方库的日志级别设高（只有 WARNING/ERROR/CRITICAL 会显示）
# logging.getLogger("pdf2docx").setLevel(logging.WARNING)

# logging.disable(logging.CRITICAL)

pdf_file = "002500_山西证券_2024.pdf"
pdf_file = "test.pdf"

start_time = time.time()
cv = Converter(pdf_file)
cv.extract_tables()
end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.4f} seconds")

# exit(0)

# tables = cv.extract_tables(start=0, end=1)


ps = cv.pages
# print(type(ps))
# print(list(ps))
p = ps[0]
sec = p.sections

for s in sec:
    for col in s:
        for blk in col.blocks:
            print(blk)


# cv.close()

# for table in tables:
#     for row in table:
#         print(row)

# cv.convert("out.docx")
# cv.close()
