#!/usr/bin/python3

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from PyPDF2 import PdfReader, PdfFileWriter
import os
import sys

def get_text_info(file_path:str) -> list:
    result = []

    pages = extract_pages(file_path)
    i = 0
    for page_layout in pages:
        left_content = ''
        right_content = ''
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                if(element.x0 < page_layout.width/2 and element.x1 < page_layout.width/2):
                    left_content += element.get_text()
                if(element.x0 > page_layout.width/2 and element.x1 > page_layout.width/2):
                    right_content += element.get_text()
        i += 1
        result += [left_content + right_content]

    return result

def get_page(pages_len, pi):
    for i in range(len(pages_len)):
        if(pi < pages_len[i]):
            return i - 1
    return -1

def main(file_path:str):
    section_table = [   'I. ', 'II. ', 'III. ', 'IV. ', 
                        'V. ', 'VI. ', 'VII. ', 'VIII. ', 
                        'IX. ', 'X. ', 'XI. ', 'XII. ', 
                        'XIII. ', 'XIV. ', 'XV. ', 'XVI. ', 
                        'XVII. ', 'XVIII. ', 'XIX. ', 'XX. ']
    subsection_table = ['A. ', 'B. ', 'C. ', 'D. ', 
                        'E. ', 'F. ', 'G. ', 'H. ', 
                        'I. ', 'J. ', 'K. ', 'L. ', 
                        'M. ', 'N. ', 'O. ', 'P. ', 
                        'Q. ', 'R. ', 'S. ', 'T. ']

    reader = PdfReader(file_path)

    if(reader.outlines):
        print('Warn: existed outline')
        return

    pages = get_text_info(file_path)

    pages_len = [0]
    for page in pages:
        pages_len += [pages_len[-1] + len(page)]
    content = ''.join(pages)

    writer = PdfFileWriter()
    for i in range(len(reader.pages)):
        writer.addPage(reader.getPage(i))

    sections = []
    contents = []

    pre_head = 0
    for section in section_table:
        find = False
        head = pre_head
        while(find == False):
            head = content.find('\n' + section, head)
            if(head == -1):
                break

            head += len('\n' + section)
            tail = content.find('\n', head)
            title = content[head: tail].strip()
            if(title.isupper()):
                title = section + title.title()
                page_num = get_page(pages_len, head)
                sections += [writer.add_bookmark(title, page_num, parent=None)]
                contents += [content[pre_head: head]]
                find = True
                pre_head = head

    count_len = len(contents.pop(0))
    contents += [content[pre_head: -1]]
    
    for i in range(len(contents)):
        head = 0
        for subsection in subsection_table:
            head = contents[i].find('\n' + subsection, head)
            if(head == -1):
                break

            head += len('\n' + subsection)
            tail = contents[i].find('\n', head)
            title = subsection + contents[i][head: tail].strip()
            page_num = get_page(pages_len, count_len + head)
            writer.add_bookmark(title, page_num, parent=sections[i])
        count_len += len(contents[i])
        
    f = open('tmp.pdf', 'wb')
    writer.write(f)
    f.close()

    os.rename('tmp.pdf', file_path)

if(__name__ == '__main__'):
    if(len(sys.argv) < 2):
        print('Usage: %s file' % (sys.argv[0]))
        exit(1)

    for i in range(len(sys.argv) - 1):
        file_path = sys.argv[i + 1]
        if(os.access(file_path, os.F_OK)):
            print('Handle with "%s"\n' % (file_path))
            main(file_path)
        else:
            print('Warn: %s not found' % (file_path))
