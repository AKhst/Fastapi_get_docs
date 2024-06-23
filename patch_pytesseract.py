import importlib.util
import os

pytesseract_path = os.path.join(
    os.path.dirname(importlib.util.find_spec("pytesseract").origin), "pytesseract.py"
)

with open(pytesseract_path, "r") as file:
    lines = file.readlines()

with open(pytesseract_path, "w") as file:
    for line in lines:
        if "pkgutil.find_loader" in line:
            line = line.replace("pkgutil.find_loader", "importlib.util.find_spec")
        file.write(line)
