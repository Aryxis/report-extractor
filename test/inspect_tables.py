import fitz

doc = fitz.open("test.pdf")
page = doc[0]

try:
    tf = page.find_tables()
except Exception as e:
    print("page.find_tables() raised:", e)
    tf = None

tables = []
if tf is None:
    tables = []
else:
    # Try to convert to list safely
    try:
        tables = list(tf)
    except TypeError:
        # TableFinder may not be directly iterable; try extract()
        if hasattr(tf, "extract"):
            try:
                tables = tf.extract()
            except Exception as e:
                print("tf.extract() raised:", e)
                tables = [tf]
        else:
            tables = [tf]

print(f"Detected {len(tables)} table-like objects")
for i, t in enumerate(tables):
    print("--- Table", i, "---")
    try:
        print("type:", type(t))
        print("dir( obj ) sample:", [a for a in dir(t) if not a.startswith("_")][:50])
        # try to print some useful methods/attrs
        for attr in [
            "bbox",
            "bboxes",
            "rect",
            "to_pandas",
            "to_list",
            "cells",
            "nrows",
            "ncols",
            "cell",
        ]:
            try:
                val = getattr(t, attr)
                print(f"{attr}:", type(val))
            except Exception as e:
                print(f"{attr}: <error> {e}")

        # try to inspect a cell if possible
        if hasattr(t, "cell"):
            try:
                c = t.cell(0, 0)
                print("cell(0,0) type:", type(c))
                # print small subset of attrs
                for a in ["bbox", "text", "text_lines", "chars"]:
                    print("cell.", a, getattr(c, a, "<no attr>"))
            except Exception as e:
                print("cell inspect failed:", e)
    except Exception as e:
        print("error inspecting table:", e)
