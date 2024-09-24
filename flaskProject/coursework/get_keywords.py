import re
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from fuzzywuzzy import process
from word2number import w2n
import pandas as pd

# #加载数据库
# df = pd.read_excel("Champions League 2019-2023 Data.xlsx")
#
# #读取所有队伍名称
# all_teams = df['HOME_TEAM'].unique()
#
# reply = input("Enter your question:")


#定义一个能对用户回答进行问题分类的函数
def find_question_type(reply):
    if '1' in reply or 'first' in reply.lower() or 'one' in reply.lower():
        return '1'
    elif '2' in reply or 'second' in reply.lower() or 'two' in reply.lower():
        return '2'
    elif '3' in reply or 'third' in reply.lower() or 'three' in reply.lower():
        return '3'
    elif '4' in reply or 'four' in reply.lower() or 'fourth' in reply.lower():
        return '4'
    else:
        raise ValueError("Sorry! Please enter valid answer.")

## Function to find the team name from the query
def find_team(reply, team_names):
    #先把句子里的champions league删除
    clean_reply = re.sub(r'champions league', '', reply, flags=re.IGNORECASE)

    # Tokenization: Break the question down into individual words or tokens
    tokens = word_tokenize(clean_reply)

    # show a part of speech to each token
    tagged = pos_tag(tokens)

    # named entity recognition: Indentify named entities in the question
    name_entities = ne_chunk(tagged)
    #print(name_entities)

    # initialize lists to store extracted team names and years
    teams = []

    for entity in name_entities:
        # check if the entity has the 'label' attribute
        if hasattr(entity, 'label'):
            # if the entity is labeled as a geopolitical entity or organization or GPE, add it to the teams list
            if entity.label() == 'PERSON' or entity.label() == 'ORGANIZATION' or entity.label() == 'GPE':
                teams.append(' '.join([word[0] for word in entity]))

    # if can't find person or organization or GPE, store NNP
    for tag in tagged:
        if tag[1] == "NNP":
            teams.append(tag[0])

    #print(teams)

    #Initialize a variable to store the best matching team name
    best_team = ""
    highest_score = 0
    #compare each word in the reply
    for team in teams:
        # Find the best match for the word in the list of team names
        match, score = process.extractOne(team, team_names)
        # If this word's match score is the highest we've seen, update the best match
        if score > highest_score:
            highest_score = score
            best_team = match
    # Return the best matching team name if the highest match score is above a threshold
    if highest_score > 80:
        print("the best team is: ", best_team)
        return best_team
    else:
        raise ValueError("Sorry! I could not find the team based on your input.")
        print("Sorry I can't find the team")


#find_team(reply,all_teams)



#定义一个找队伍的函数
def find_team2(reply, all_teams):
    # Normalize the reply to lower case and remove punctuation for more reliable matching
    normalized_reply = re.sub(r'[^\w\s]', '', reply.lower())

    # Split the normalized reply into words
    words = normalized_reply.split()

    # Initialize an empty list to store potential team matches
    potential_teams = []

    # Iterate over each word to find potential team matches
    for word in words:
        # Iterate over the list of all team names
        for team in all_teams:
            # Normalize the team name for matching
            normalized_team = team.lower()
            # Check if the word is exactly in the team name (using word boundaries)
            if re.search(r'\b' + re.escape(word) + r'\b', normalized_team):
                potential_teams.append(team)

    # Use fuzzy matching to find the best match if there are multiple potential matches
    if potential_teams:
        # Using process.extractOne to find the closest match to the user input
        best_match, score = process.extractOne(reply, potential_teams)
        # Optional: Ask for user confirmation if the match is not confident
        if score < 80:
            # Here you could implement a user confirmation step
            print(f"Not sure about '{best_match}' with a confidence of {score}%. Please confirm.")
        print("2The best team is: ", best_match)
        return best_match
    else:
        print("No matching team found.")
        return "No matching team found."

#find_team2(reply,all_teams)

#开始匹配年份

def get_year(reply):
    #设置合法年份的范围
    min_year = 2019
    max_year = 2023

#先用正则表达式来匹配‘in'或者'for‘后面的年份，因为有可能用户只想查询某一年的信息
    special_year_pattern = r"\b(in|for)\s(\d{4})\b"

#和用户的回复进行匹配
    match = re.search(special_year_pattern, reply, re.IGNORECASE)
    if match:
        year = int(match.group(2))
        #如果找到匹配，提取年份
        if min_year <= year <= max_year:
            start_year = year
            end_year = year
            return start_year, end_year
        else:
            raise ValueError(f"The year must be between {min_year} and {max_year}.")

#用正则表达式来匹配年份
    year_pattern = r"\b\d{4}\b"

#在回答中匹配年份
    years = re.findall(year_pattern, reply)
    #print("The years are ", years)

    #如果提取出两个年份，则分别对应起始和结束年份
    if len(years) == 2:
        start_year = int(years[0])
        end_year = int(years[1])
        if min_year <= start_year <= max_year and min_year <= end_year <= max_year:
            return start_year, end_year
        else:
            raise ValueError(f"The year must be between {min_year} and {max_year}.")

    #如果提取出一个年份，则年份对应起始年份，结束年份为2023年
    elif len(years) == 1:
        start_year = int(years[0])
        if min_year <= start_year <= max_year:
            end_year = 2023
            return start_year, end_year
        else:
            raise ValueError(f"The year must be between {min_year} and {max_year}.")

    #如果没有准确年份，则提取过去n年中的n
    else:
        #如果有"last year", "this year"等词语，则要分开考虑
        if "last year" in reply:
            start_year = 2023
            end_year = 2023
            return start_year, end_year

        else:
            # Tokenization: Break the question down into individual words or tokens
            tokens = word_tokenize(reply)

            # show a part of speech to each token
            tagged = pos_tag(tokens)

            for tag in tagged:
                #如果识别出来是数字，则首先判断是数字还是字母
                if tag[1] == "CD":
                    #如果是数字，直接用int提取
                    try:
                        number = int(tag[0])
                        if number <= 5:
                            start_year = 2023-number+1
                            end_year = 2023
                            return start_year, end_year
                        else:
                            raise ValueError(f"The year must be between {min_year} and {max_year}.")
                    except ValueError:
                        #如果是字母，将字母转换成数字
                            number = w2n.word_to_num(tag[0])
                            if number <= 5:
                                start_year = 2023-number+1
                                end_year = 2023
                                return start_year,end_year
                            else:
                                raise ValueError(f"The year must be between {min_year} and {max_year}.")


    raise ValueError("No valid year found or the provided year is out of the allowed range.")

