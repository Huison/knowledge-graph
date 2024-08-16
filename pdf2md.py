import fitz  # PyMuPDF
from markdownify import markdownify as md


def pdf_to_markdown(pdf_path, md_path):
    doc = fitz.open(pdf_path)
    with open(md_path, 'w', encoding='utf-8') as md_file:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            md_text = md(text)
            md_file.write(md_text + "\n\n")


pdf_path = '/home/huison/ymkj/中部训练二期项目/知识图谱/高等数学-上册.pdf'
md_path = 'output1.md'
pdf_to_markdown(pdf_path, md_path)
