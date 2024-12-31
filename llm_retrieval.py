from config import OPENAI_API_KEY
import os
from openai import OpenAI
import re

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def sanitize_reference(input_str):
    return re.sub(r"\s", "", input_str).lower()

def get_all_scriptures(fp):
    """Parse the scriptures.txt file into a dict"""
    scripture_dict = dict()

    file = open(fp, 'r')
    for line in file:
        current_id = line.split("     ")[0]
        scripture_dict[sanitize_reference(current_id)] = line.split("     ")[1]
    return scripture_dict

def append_to_lists(sub_v, used_verses, chapters, verses, texts, scripture_dict):
    """Append a reference to a few lists"""
    texts.append(sub_v + "\t" + scripture_dict[sanitize_reference(sub_v)] + "\n")
    chapters.append(sub_v.split(":")[0])
    verses.append(sub_v.split(":")[1])
    used_verses.add(sanitize_reference(sub_v))

def scriptures_from_verses(verses, scripture_dict):
    output_string = ""
    used_verses = set()
    chapters = []
    verses = []
    texts = []
    for v in verses:
        if (sanitize_reference(v) in scripture_dict.keys()) and (sanitize_reference(v) not in used_verses):
            append_to_lists(v, used_verses, chapters, verses, texts, scripture_dict)
        elif v.find("-") >=0:
            if not (v.split(":")[1].split("-")[0].strip().isdigit() and v.split(":")[1].split("-")[1].strip().isdigit()):
                continue
            cur_verse = int(v.split(":")[1].split("-")[0])
            last_verse = int(v.split(":")[1].split("-")[1])
            if cur_verse > last_verse:
                continue
            while cur_verse <= last_verse:
                sub_v = v.split(":")[0] + ":" + str(cur_verse)
                if (sanitize_reference(sub_v) in scripture_dict.keys()) and (sanitize_reference(sub_v) not in used_verses):
                    append_to_lists(sub_v, used_verses, chapters, verses, texts, scripture_dict)
                cur_verse +=1
    for ref in sorted(zip(chapters, verses, texts)):
        output_string += ref[2]
    return output_string
    
        
def get_scriptures_string(scripture_dict, question, generative_model):
    verses = get_verses_if_asked(question, generative_model)
    output_string = scriptures_from_verses(verses, scripture_dict)
    if len(output_string) == 0:
        verses = get_verse_references(question, generative_model)
        output_string = scriptures_from_verses(verses, scripture_dict)
    return output_string

def get_verse_references(question, generative_model):
    """Get a list of verses that refer to the question of interest
    Args:
        question: the question someone asked
        generative_model: the generative model to use
    """

    sys_prompt = f"""
    You are a knowledgeable, faithful, and thoughtful latter-day saint. Your role is to suggest scriptures that will be relevant to answering gospel questions. 

    These scriptures may come from the Old Testament, the New Testament, the Bible, the Book of Mormon, the Doctrine of Covenants, or the Pearl of Great Price. 

    Choose scriptures that are highly relevant to the question at hand, following this response format:
    ```
    Doctrine and Covenants 78:4-7
    Mosiah 4:27
    Matthew 6:19-21
    2 Corinthians 9:7
    Alma 34:28-29
    ```

    Your list should contain five to ten scripture references. Each reference should be on its own line in the format <book> <chapter>:<verse(s)>. Do not include the actual text of the scripture in your response. Do not include any numbers or other symbols prior to the scripture reference. 

    """
    
    client = OpenAI()
    response = client.chat.completions.create(
        model=generative_model,
        messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.split("\n")

def get_verses_if_asked(question, generative_model):
    """Get a list of verses that a user specifically asked for
    Args:
        question: the question someone asked
        generative_model: the generative model to use
    """

    sys_prompt = f"""
    You are a concise, faithful, and thoughtful latter-day saint. Your role is to determine whether the person asking this question is asking for a specific section of scripture to be read back to them. If they say "Show me the whole book of  first nephi", you should return "1 Nephi 1:1-20"

    These scriptures may come from the Old Testament, the New Testament, the Bible, the Book of Mormon, the Doctrine of Covenants, or the Pearl of Great Price. 

    If the user is asking for a specific scripture, return a scripture reference. The reference should be on its own line in the format <book> <chapter>:<start verse>-<end verse>. Do not include the actual text of the scripture in your response. Do not include any numbers or other symbols prior to the scripture reference. 

    If the user has a more vague question, simply return "the user did not request a specific scripture"

    """
    
    client = OpenAI()
    response = client.chat.completions.create(
        model=generative_model,
        messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.split("\n")
