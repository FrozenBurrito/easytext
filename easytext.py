import argparse
import openai
import os
import re
import unicodedata
from dotenv import load_dotenv
from pathlib import Path

# load .env file
load_dotenv()

# read command line argument, get input filename
# see also https://stackoverflow.com/questions/30750843/python-3-unicodedecodeerror-charmap-codec-cant-decode-byte-0x9d
parser = argparse.ArgumentParser('easytext.py')
parser.add_argument('input_filename', help='Path to input text file.', type=argparse.FileType('r', encoding='utf8', errors='ignore'))
args = parser.parse_args()
input_filename = args.input_filename

# read text from input_filename into string
# todo items: 1) handle titles or subtitles; 2) handle non-paragraph data
fulltext = input_filename.read()
fulltext = re.sub(r'\n\n+', '\n\n', fulltext).strip()
fulltext = unicodedata.normalize('NFKD', fulltext).encode('ascii','ignore')

paragraphs = []
for paragraph in fulltext.decode().split("\n\n"):
    paragraphs.append( re.sub(r'\n', ' ', paragraph).strip() )
#paragraphs = fulltext.split("\n\n")
#for paragraph in fulltext.split("\n\n"):
    #paragraphs.append(' '.join(paragraph.splitlines()))

# create to AI endpoint, request paraphrased version
# todo items: 
# 1) test other API settings (temp, etc); 
# 2) test and refine prompt
# 3) multiple prompts for different grade levels
# 4) add support for other AI endpoints
openai.organization = os.getenv('OPENAI_ORG_ID')
openai.api_key = os.getenv('OPENAI_API_KEY')
prompt = os.getenv('PROMPT')
paraphrased = []
for i, p in enumerate(paragraphs):
    print("Req paraphrase for paragraph", str(i+1), "of", str(len(paragraphs)))
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt + p}])
    paraphrased.append(completion.choices[0].message.content)
    print("Recv paraphrase for paragraph", str(i+1), "of", str(len(paragraphs)))

# create readme.md file with side-by-side table
# todo items: 
# 1) title extraction from paragraphs[0]
# 2) write rows after X paragraphs processed by endpoint
# 3) on CTRL+C, dump & write current output
# 4) option to begin processing at a specific paragraph number (error recovery)
md_row_headings = "|Para.|Main Text|Paraphrased|\n" 
md_row_sep = "|:-:|:----------|:----------|\n"
#output_filepath_str = "output" + "\\" + Path(input_filename.name).resolve().stem + '.md'
output_filepath_str = Path(input_filename.name).with_suffix('.md')
with open(output_filepath_str, 'w') as f:
    f.write(md_row_headings)
    f.write(md_row_sep)
    for i, p in enumerate(paragraphs):
        f.write("|" + str(i+1) + "|" + p + "|" + paraphrased[i] + "|" + "\n")
    f.close()
print('Done! Output saved to', output_filepath_str)