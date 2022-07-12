#!/usr/bin/python3

from PyPDF2 import PdfReader, PdfFileWriter, PdfFileReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTLine, LAParams, LTAnno
from collections import defaultdict
import string
import os
import sys
import re

class Text:
    def __init__(self, content:str, font_name:str, size:float, page:int) -> None:
        self.content =  content
        self.font_name =  font_name
        self.size =  size
        self.page =  page
        self.type = ''

    def __str__(self) -> str:
        return self.content
    
    def __eq__(self, __o: object) -> bool:
        '''
        Whether they are the same font
        '''
        if(abs(self.size - __o.size) < 0.0001 and self.font_name == __o.font_name):
            return True
        else:
            return False

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __len__(self) -> int:
        return len(self.content)

    def set_type(self, t:str):
        self.type = t
    
    def get_type(self) -> str:
        return self.type
    
    def lower(self) -> str:
        return self.content.lower()
    
    def is_title(self) -> bool:
        if(len(self.content) <= 4 or len(self.content) >= 100):
            return False
        
        enable_strings = string.ascii_letters + string.digits + '.- '
        for chr in self.content:
            if(chr not in enable_strings):
                return False
        
        return True

def check_title(text:str)->bool:
    check_str = ''
    enable_strings = string.ascii_letters + string.digits + '.- '
    for chr in text:
        if(chr not in enable_strings):
            check_str += chr
    
    if(not check_str):
        return True
    else:
        return False

def get_text_info(file_path:str) -> list:
    result = []
    pages = extract_pages(file_path)
    i = 0
    for page in pages:
        for element in page:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    font_name = ''
                    size = -1
                    if isinstance(text_line, LTChar):
                        font_name = text_line.fontname
                        size = text_line.size

                    if(not font_name and not isinstance(text_line, LTAnno)):
                        for character in text_line:
                            if isinstance(character, LTChar):
                                font_name = character.fontname
                                size = character.size
                    result += [Text(text_line.get_text().strip() , font_name, size, i)]

        i += 1
    return result

def main(file_path:str):
    reader = PdfReader(file_path)

    if(reader.outlines):
        print('Warn: existed outline')
        return

    texts = get_text_info(file_path)

    section = None
    subsection = None

    for text in texts:
        if('introduction' in text.lower()):
            section = text
            break

    subsection_candidates = []

    for text in texts:
        is_existed = False
        for existed in subsection_candidates:
            if(section and section != text and existed == text):
                is_existed = True
                break

        if(is_existed == False and text.is_title()):
            subsection_candidates += [text]

    for i in range(len(subsection_candidates)):
        print('%3d: %s' % (i, subsection_candidates[i]))

    print('')
    print('Input the subsection [index] : ', end='', flush=True)
    input_content = input().strip()
    if(input_content.isnumeric()):
        input_index = int(input_content)
        if(input_index >= 0 and input_index < len(subsection_candidates)):
            subsection = subsection_candidates[input_index]

    titles = []

    previous_text = Text('' , '', -1, -1) # initial
    for text in texts:
        if(section and section == text):
            text.set_type('section')
            if(not (previous_text.get_type() == 'section' and previous_text == text)):
                titles.append(text)
            else:
                titles[-1].content += text.content
        
        elif(subsection and subsection == text):
            text.set_type('subsection')
            if(not (previous_text.get_type() == 'subsection' and previous_text == text)):
                titles.append(text)
            else:
                titles[-1].content += text.content

        previous_text = text

    tmp = titles
    titles = []
    for text in tmp:
        if(text.is_title()):
            text.content = text.content.title()
            titles += [text]

    print('')
    print('Generate outline:')
    print('')

    for i in range(len(titles)):
        print('%3d: %s' % (i, titles[i].content))

    print('')
    print('Input the index to be removed : ', end='', flush=True)
    remove_list = sorted(set([int(v) for v in re.findall('\d+', input())]), reverse=True)
    for index in remove_list:
        titles.pop(index)

    print('')
    writer = PdfFileWriter()
    for i in range(len(reader.pages)):
        writer.addPage(reader.getPage(i))

    parent = None
    for bookmark in titles:
        print(bookmark.content)
        if(bookmark.get_type() == 'section'):
            parent = writer.add_bookmark(bookmark.content, bookmark.page, parent=None)
        elif(bookmark.get_type() == 'subsection'):
            writer.add_bookmark(bookmark.content, bookmark.page, parent=parent)
        
    print('')

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
    # main('test.pdf')
