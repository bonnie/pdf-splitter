# reference: https://stackoverflow.com/a/61726736

import os
from PyPDF2 import PdfReader, PdfWriter
import re
import string
from datetime import datetime

filename="NewJamBook-V2LC"
path = 'pdfs-to-split/{}.pdf'.format(filename)
first_page = 12
last_page = 410

try:
    os.mkdir(filename)
except: 
    timestamp = datetime.now().timestamp()
    os.rename(filename, filename + '-' + str(timestamp) )
    os.mkdir(filename)


warnings = []

# for ccmc jam book
def get_filename(page, page_num):
    title =  page.extract_text().split(' (')[0]
    if len(title) > 150:
        warnings.append("not printing page {}: title too long".format(str(page_num)))
        return
    
    # remove cruft from beginning
    title = re.sub(r'^\d{1,3} TOC\s*', '', title)

    # remove section header text 
    headings = [
        "Americana", 
        "Irish Songs", 
        "Scottish Songs", 
        "Australian Songs", 
        "Other Traditional Songs \(Various Origins\)", 
        "Spiritual / Gospel",
        "Country-Western Songs",
        "Folk Songs",
        "Popular Songs \(1950-Present\)",
        "Novelty / Silly / Funny Songs",
    ]
    title = re.sub(r'^\s*({})\b'.format('|'.join(headings)), '', title)

    # from all caps to title case
    title = string.capwords(title)

    # Remove any trailing *
    title = re.sub(r'\*$', '', title)

    # remove any '/'
    title = re.sub(r'/', '-', title)

    # remove any leading / trailing whitespace
    title.strip()

    # move "the" and "a" and "an" to the end
    title = re.sub(r'^(The|A|An) \b(.*)', r'\2, \1', title)

    if len(title) == 0:
        warnings.append("not printing page {}: title was reduced to nothing".format(str(page_num)))
        return

    return '{}.pdf'.format(title)



pdf = PdfReader(path)
page = first_page - 1
while (page < last_page - 1 and page < len(pdf.pages)):
    pdf_writer = PdfWriter()
    pdf_writer.add_page(pdf.pages[page])

    output_filename = get_filename(pdf.pages[page], page)
    output_path = "{}/{}".format(filename, output_filename)

    # is this a two-pager?
    if "(2P)" in pdf.pages[page].extract_text():
        pdf_writer.add_page(pdf.pages[page + 1])
        next_page = page + 2
    else: 
        next_page = page + 1

    if (output_filename):
        with open(output_path, 'wb') as out:
            pdf_writer.write(out)

        print('Created: {}'.format(output_filename))
    
    # advance
    page = next_page

print ("WARNINGS")
print ('\n'.join(warnings))