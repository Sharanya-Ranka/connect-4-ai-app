import json
import re
import itertools


texfile = r".\src\data\original_script.tex"
jsonfile = r".\src\data\blogContent1.json"


def parseSection(section):
    section_title, section_text = section
    section_text = section_text.strip("\n")
    paragraphs = re.split(r"\n\n", section_text)

    paragraphs_json = [parseParagraph(paragraph) for paragraph in paragraphs]
    section_json = {section_title: {"title": section_title, "data": paragraphs_json}}

    return section_json

    # breakpoint()


def parseParagraph(paragraph_text):
    return {"type": "paragraph", "value": paragraph_text}


def parseBlockMath(blockmath_text):
    pass


def parseInlineMath(text):
    pass


def getSections(text):
    # breakpoint()

    pt1 = re.sub(r".*?(?=\\section\{)", "", text, flags=re.DOTALL, count=1)
    pt2 = re.sub(r"\\end\{document\}", "", pt1)
    sections = re.findall(
        r"\\section\{(.*?)\}(.*?)(?=\\section|$)", pt2, flags=re.DOTALL
    )
    # sections = [(section_title, section_text) for section_title, section_text in splits]

    return sections


with open(texfile, "r", encoding="utf8") as fp:
    content = "".join(fp.readlines())
    sections = getSections(content)
    all_sections_dict = {}

    for section in sections:
        section_json = parseSection(section)
        all_sections_dict.update(section_json)

    with open(jsonfile, "w") as fp:
        json.dump(all_sections_dict, fp, indent=4)
