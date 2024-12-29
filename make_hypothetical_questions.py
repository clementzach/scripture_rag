from config import OPENAI_API_KEY
import os
from openai import OpenAI
import re

GENERATIVE_MODEL = "gpt-4o-mini"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def get_all_chapters(fp):
    """Get all availabale chapters in scripture"""
    chapters_list = set()
    file = open(fp, 'r')
    for line in file:
        current_chapter = line.split(":")[0]     
        chapters_list.add(current_chapter)
    return chapters_list

def get_chapter_text(fp, chapter_to_find):
    """
    Get text corresopnding to a chapter of scripture
    """
    output_text = ""
    file = open(fp, 'r')
    for line in file:
        current_chapter = line.split(":")[0]
        if current_chapter == chapter_to_find:
            output_text +=  line
    return output_text

def get_hypothetical_questions(chapter_text):
    system_prompt = f"""You are a knowledgeable, faithful, compassionate, and thoughtful latter-day saint. Your role is to anticipate the questions that can be answered from a given section of scripture to enable actual user questions to be efficiently mapped to verse references. 

The questions generated should be something that a Latter-day Saint in the current day may ask as they are trying to understand a verse in a different part of scripture or if they are trying to remember a fact about the story in the scripture. 


For each verse provided, generate: 
1. A question that asks about the general facts of the verse
2. A question about the life application of the verse
3. A question about the doctrine taught in the verse

To format your answer, provide a scripture reference in the format <book> <chapter>:<verse>, then type the question that can be answered by the scripture reference. 

Put each reference/question combination on a new line. 

Here is some example output: 

```
Alma 32:6 Are people in poverty less loved in God's sight?
Alma 32:11 Do we need to be in a synagogue to worship god?
```
    """

    client = OpenAI()
    response = client.chat.completions.create(
        model=GENERATIVE_MODEL,
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chapter_text}
        ]
    )
    questions = response.choices[0].message.content
    return "\n".join([x for x in questions.split("\n") if len(x.strip()) > 5])


def main():
    questions_fp = "data/hypothetical_questions.txt"
    scriptures_fp = "data/scriptures.txt"
    all_chapters = get_all_chapters(scriptures_fp)
    for chapter in all_chapters:
        chapter_text = get_chapter_text(scriptures_fp, chapter)
        questions = get_hypothetical_questions(chapter_text)
        with open(questions_fp, "a") as f:
            f.write(questions + "\n")

if __name__ == "__main__":
    main()
            
