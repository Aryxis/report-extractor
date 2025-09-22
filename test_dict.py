import pdfplumber
import random
import time

# pdf_name = "input_pdf/002500_山西证券_2024.pdf"
pdf_name = "input_pdf/300059_东方财富_2024.pdf"
# pdf_name = "input_pdf/601318_中国平安_2012.pdf"
# pdf_name = "input_pdf/601166_兴业银行_2012.pdf"


doc = pdfplumber.open(pdf_name)
all_pages = []

begin = time.time()
for page in doc.pages:
    text_blocks = page.extract_words(
        extra_attrs=["size"],
        x_tolerance=3,
        y_tolerance=3,
    )
    all_pages.append({"page_number": page.page_number, "blocks": text_blocks})
    # all_pages.append(text_blocks)
end = time.time()
print("Time taken to extract all pages: ", end - begin)

count = {}


# page_indices = random.sample(range(len(doc.pages)), 10)
# page_start = random.randint(0, len(doc.pages) - 20)


begin = time.time()
for page in all_pages:
    # page = all_pages[i]
    for text in page["blocks"]:
        key = round(text["size"], 1)
        count[key] = count.get(key, 0) + 1
        if key >= 16.0:
            print(text)
end = time.time()
print("Time taken to count font sizes: ", end - begin)

for k, v in sorted(count.items(), key=lambda x: x[1]):
    print(k, ":", v)

"""
300059_东方财富_2024

18.0 : 2
7.0 : 3
4.6 : 3
10.0 : 18
16.0 : 28
14.0 : 28
12.0 : 154
6.5 : 358
5.5 : 371
8.0 : 814
7.6 : 1031
10.6 : 2481
9.0 : 15891



---


002500_山西证券_2024

18.0  :  1
24.0  :  4
16.0  :  23
12.0  :  184
6.5   :  273
10.0  :  913
7.6   :  1414
7.0   :  1907
8.0   :  2803
10.6  :  3350
11.0  :  5842
9.0   :  12073

---

"""
