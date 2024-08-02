from config import OPENAI_API_KEY
import os
from openai import OpenAI
import re

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def sanitize_reference(input_str):
    return re.sub("\s", "", input_str).lower()

def get_all_scriptures(fp):
    """Parse the scriptures.txt file into a dict"""
    scripture_dict = dict()

    file = open(fp, 'r')
    for line in file:
        current_id = line.split("     ")[0]
        scripture_dict[sanitize_reference(current_id)] = line.split("     ")[1]
    return scripture_dict
        
def get_scriptures_string(scripture_dict, question, generative_model):
    verses = get_verse_references(question, generative_model)
    output_string = ""
    for v in verses:
 
        if sanitize_reference(v) in scripture_dict.keys():
            output_string += v + "\t" + scripture_dict[sanitize_reference(v)] + "\n"
        elif v.find("-") >=0:
            cur_verse = int(v.split(":")[1].split("-")[0])
            last_verse = int(v.split(":")[1].split("-")[1])
            if cur_verse > last_verse:
                continue
            while cur_verse <= last_verse:
                sub_v = v.split(":")[0] + ":" + str(cur_verse)
                if sanitize_reference(sub_v) in scripture_dict.keys():
                    output_string += sub_v + "\t" + scripture_dict[sanitize_reference(sub_v)] + "\n"
                cur_verse +=1
                
    return output_string


def get_verse_references(question, generative_model):
    """Get a list of verses that refer to the question of interest
    Args:
        question: the question someone asked
        generative_model: the generative model to use
    """

    sys_prompt = f"""
    You are a concise, faithful, and thoughtful latter-day saint. Your role is to suggest scriptures that will be relevant to answering gospel questions. 

    These scriptures may come from the Old Testament, the New Testament, the Bible, the Book of Mormon, the Doctrine of Covenants, or the Pearl of Great Price. 

    Choose scriptures that are highly relevant to the question at hand. 

    Return a list of five to ten scripture references to answer the question. Each reference should be on its own line in the format <book> <chapter>:<verse>. Do not include the actual text of the scripture in your response. 

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