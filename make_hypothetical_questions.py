from config import OPENAI_API_KEY
import os
from openai import OpenAI
import re

GENERATIVE_MODEL = "gpt-4o-mini"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def get_chapters_dict(fp):
    """
    Get text corresopnding to a chapter of scripture
    """
    chapters_dict = dict()
    file = open(fp, 'r')
    for line in file:
        current_chapter = line.split(":")[0]
        if current_chapter in chapters_dict:
            chapters_dict[current_chapter] += line
        else:
            chapters_dict[current_chapter] = line

    return chapters_dict

def get_hypothetical_questions(chapter_text):
    system_prompt = f"""You are a knowledgeable, faithful, compassionate, and thoughtful latter-day saint. Your role is to anticipate the questions that can be answered from a given section of scripture to enable actual user questions to be efficiently mapped to verse references. 

The questions generated should be something that a Latter-day Saint in the current day may ask as they are trying to understand a verse in a different part of scripture or if they are trying to remember a fact about the story in the scripture. 


For each verse provided, generate exactly three questions: 
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
    all_chapters = get_chapters_dict(scriptures_fp)
    for chapter in all_chapters.keys():
        chapter_text = all_chapters[chapter]
        questions = get_hypothetical_questions(chapter_text)
        ## For long chapters, gpt has trouble writing three questions per verse. In this case, we'll split the chapters into sections of 10 verses. 
        if len(questions.split("\n")) < (len(chapter_text.split("\n")) * 2):
            questions = ""
            current_chapter_text = ""
            verses = chapter_text.split("\n")
            min_verse = 0
            increment_size = 10
            overlap_size = 2
            while (min_verse) < (len(verses)):
                questions = questions + "\n" + get_hypothetical_questions("\n".join(verses[min_verse:min(len(verses), (min_verse + increment_size))]))
                min_verse += increment_size - overlap_size ## We will have a 2-verse overlap, which is probably not ideal. Perhaps later I should do something to ensure that there is the same number per verse. 
        with open(questions_fp, "a") as f:
            f.write(questions + "\n")

if __name__ == "__main__":
    main()
            
