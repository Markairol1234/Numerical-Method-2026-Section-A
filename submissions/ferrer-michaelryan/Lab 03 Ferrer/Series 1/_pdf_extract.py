import sys, importlib.util
mods = ['pypdf', 'PyPDF2', 'pdfplumber', 'fitz', 'pdfminer']
for m in mods:
    print(m, 'OK' if importlib.util.find_spec(m) else 'MISSING')

try:
    import pypdf
    print('--- pypdf extraction ---')
    r = pypdf.PdfReader(r'c:\Users\Mayk\OneDrive\Desktop\html\figures\Series1.pdf')
    for i, page in enumerate(r.pages):
        print(f'===== PAGE {i+1} =====')
        print(page.extract_text())
except Exception as e:
    print('pypdf error:', e)