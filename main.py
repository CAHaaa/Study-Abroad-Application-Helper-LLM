from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
import os

def generate_document():
    # 创建文档对象（使用 article 文档类）
    doc = Document('basic', documentclass='article')

    # 添加文档元数据
    doc.preamble.append(Command('title', 'PyLaTeX Example'))
    doc.preamble.append(Command('author', 'Your Name'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))  # 插入标题

    # 添加章节
    with doc.create(Section('Introduction')):
        doc.append('Hello from PyLaTeX! ')
        doc.append(italic('This text is italic.'))

        # 添加子章节
        with doc.create(Subsection('Features')):
            doc.append('Supports formulas: $E=mc^2$')
            doc.append(NoEscape(r'\newline'))  # 换行
            doc.append(r'And special characters: \# \$ \%')

    # 添加独立数学公式
    with doc.create(Section('Math Example')):
        doc.append(NoEscape(r'The quadratic formula:'))
        doc.append(NoEscape(r'\[ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \]'))

    # 生成PDF（自动调用pdflatex）
    doc.generate_pdf(clean_tex=False, compiler='pdflatex')


if __name__ == '__main__':
    generate_document()