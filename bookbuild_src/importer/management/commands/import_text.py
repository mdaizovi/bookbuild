from docx2python import docx2python
from io import StringIO


def import_text(filename):
    doc_result = docx2python(f"{filename}.docx")
    body = [x.strip() for x in doc_result.body[0][0] if len(x) > 1]
    print(body)


for filename in ["Texte-2017/03-ausflug"]:
    import_text(filename)
