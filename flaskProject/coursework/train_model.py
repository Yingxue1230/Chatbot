from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

#extended training dataset with different variations
train_data = [
    # Query for all match information within a specific time range
    ("Can you show me all the match information of Manchester United within 5 years?", "match_info_query"),
    ("Display all Liverpool matches from 2020 to 2021", "match_info_query"),
    ("I want every game detail for Chelsea in the last five years", "match_info_query"),
    ("List every match Arsenal played from 2019 to 2023", "match_info_query"),
    ("Show Tottenham's games from 2020 to 2022", "match_info_query"),
    ("List all matches played by Real Madrid in the last two years", "match_info_query"),
    ("Show all the games for Barcelona from 2019 to 2021", "match_info_query"),
    ("I need to see every fixture involving Liverpool since 2019", "match_info_query"),
    ("Provide the complete match history for Manchester City over the past three years", "match_info_query"),
    ("Can you display all the Champions League matches for Chelsea in the last four years?", "match_info_query"),
    ("I want to review all the games that Juventus played in champions league from 2019 till now", "match_info_query"),
    ("Show me all the matches where Arsenal was a participant in the past five years.", "match_info_query"),
    ("List out every game played by PSG in champions league within the last three years.", "match_info_query"),
    ("I'd like to see all of Bayern Munich's Bundesliga matches from 2020 to 2022.", "match_info_query"),
    ("Detail every match Tottenham has been involved in since 2019.", "match_info_query"),
    ("Give me all match records for AC Milan in the last two years.", "match_info_query"),
    ("Present all the La Liga matches for Atletico Madrid from 2019 to 2023.", "match_info_query"),
    ("Can you outline all the games played by Inter Milan in the past 48 months?", "match_info_query"),
    ("Show every match involving Borussia Dortmund in the last six seasons.", "match_info_query"),
    ("I'm interested in all the games Ajax has played in the champions league since 2019.", "match_info_query"),
    ("Detail Napoli's match history in champions league over the last four years.", "match_info_query"),
    ("List all the competitive games for Leicester City from 2019 to 2022.", "match_info_query"),
    ("Provide a rundown of all matches featuring RB Leipzig in the past three years.", "match_info_query"),
    ("I want a list of all the games played by Everton in the Champions League since 2019.", "match_info_query"),
    ("Show all UEFA Champions League fixtures for Porto in the last five years.", "match_info_query"),
    ("Can you provide all Champions League match details for Barcelona from 2018 to 2022?", "match_info_query"),
    ("I'd like to know about Ajax's matches in the Champions League for the last 3 years.", "match_info_query"),
    ("What were Liverpool's Champions League results from 2017 to 2021?", "match_info_query"),
    ("Please show all Manchester United Champions League matches over the last 4 years.", "match_info_query"),
    ("Can you list all Bayern Munich's Champions League matches from 2015 to 2019?", "match_info_query"),
    ("I'm interested in Real Madrid's Champions League games for the last 5 years.", "match_info_query"),
    ("Show me Paris Saint-Germain's matches in the Champions League from 2016 to 2020.", "match_info_query"),
    ("Detail Juventus's Champions League activities over the past 3 years.", "match_info_query"),
    ("Provide a summary of Chelsea's matches in the Champions League from 2018 to 2022.", "match_info_query"),
    ("How did Borussia Dortmund perform in the Champions League over the last 6 years?", "match_info_query"),
    ("List all Atletico Madrid's matches in the Champions League from 2017 to 2021.", "match_info_query"),
    ("I want to see all of Inter Milan's Champions League matches for the past 4 years.", "match_info_query"),
    ("Detail all Manchester City's Champions League games from 2019 to 2023.", "match_info_query"),
    ("Provide information on AC Milan's Champions League matches over the last 5 years.", "match_info_query"),
    ("Can you provide all Champions League match details for Barcelona since 2018?", "match_info_query"),
    ("I'd like to know about Ajax's matches in the Champions League since 2019.", "match_info_query"),
    ("What were Liverpool's Champions League results since 2020?", "match_info_query"),
    ("Please show all Manchester United Champions League matches since 2021.", "match_info_query"),
    ("Can you list all Bayern Munich's Champions League matches since 2017?", "match_info_query"),
    ("I'm interested in Real Madrid's Champions League games since 2022.", "match_info_query"),
    ("Show me Paris Saint-Germain's matches in the Champions League since 2018.", "match_info_query"),
    ("Detail Juventus's Champions League activities since 2019.", "match_info_query"),
    ("Provide a summary of Chelsea's matches in the Champions League since 2020.", "match_info_query"),
    ("How did Borussia Dortmund perform in the Champions League since 2018?", "match_info_query"),
    ("Can you provide the match outcomes for PSG in the 2019 Champions League?", "match_info_query"),

    # Query for the number of matches won within a specific time period
    ("Can you tell me how many matches Bayern Munich won between 2018-2022?", "win_count_query"),
    ("How many victories did Real Madrid secure from 2019 to 2022?", "win_count_query"),
    ("What's the number of wins for Barcelona from 2019 to 2023?", "win_count_query"),
    ("Count the winning matches for Juventus in the last four years", "win_count_query"),
    ("Total wins for AC Milan from 2018 to 2021", "win_count_query"),
    ("How many matches did Chelsea win from 2019 to 2021?", "win_count_query"),
    ("Tell me the number of victories Real Madrid secured from 2020 to 2022.", "win_count_query"),
    ("What's the total win count for Barcelona between 2018 and 2021?", "win_count_query"),
    ("Can you provide the win statistics for Liverpool from 2019 to 2022?", "win_count_query"),
    ("I need to know how many games Juventus won from 2018 to 2020.", "win_count_query"),
    ("How many Bundesliga matches did Bayern Munich win from 2019 to 2021?", "win_count_query"),
    ("What were PSG's total wins from 2020 to 2022?", "win_count_query"),
    ("Show me Manchester City's total wins from 2019 to 2021.", "win_count_query"),
    ("How many victories did Arsenal secure from 2020 to 2022?", "win_count_query"),
    ("Provide Borussia Dortmund's win count from 2019 to 2020.", "win_count_query"),
    ("What is AC Milan's win total for 2019 to 2021?", "win_count_query"),
    ("Tell me Tottenham's total wins from 2020 to 2022.", "win_count_query"),
    ("How many matches did Ajax win from 2019 to 2021?", "win_count_query"),
    ("Can you tell me the number of wins Inter Milan had from 2019 to 2022?", "win_count_query"),
    ("What was Napoli's win count for 2019 to 2020?", "win_count_query"),
    ("Report the number of victories for Atletico Madrid from 2019 to 2021.", "win_count_query"),
    ("How many games did Manchester United win from 2020 to 2022?", "win_count_query"),
    ("What is Sevilla's win count for 2019 to 2021?", "win_count_query"),
    ("How many victories did RB Leipzig secure from 2019 to 2022?", "win_count_query"),
    ("Tell me the number of wins Everton had from 2019 to 2021.", "win_count_query"),
    ("How many Champions League matches did Chelsea win in the past three years?", "win_count_query"),
    ("Tell me the number of victories Real Madrid secured in the Champions League over the past two years.", "win_count_query"),
    ("What's the total win count for Barcelona in the Champions League in the last four years?", "win_count_query"),
    ("Can you provide the win statistics for Liverpool in the Champions League for the past three years?", "win_count_query"),
    ("I need to know how many games Juventus won in the Champions League in the past two years.", "win_count_query"),
    ("How many matches did Bayern Munich win in the Champions League over the past three years?", "win_count_query"),
    ("What were PSG's total wins in the Champions League in the last four years?", "win_count_query"),
    ("Show me Manchester City's total wins in the Champions League for the past two years.", "win_count_query"),
    ("How many victories did Arsenal secure in the Champions League in the past three years?", "win_count_query"),
    ("Provide Borussia Dortmund's win count in the Champions League for the past two years.", "win_count_query"),
    ("What is AC Milan's win total in the Champions League over the past three years?", "win_count_query"),
    ("Tell me Tottenham's total wins in the Champions League in the last four years.", "win_count_query"),
    ("How many matches did Ajax win in the Champions League in the past three years?", "win_count_query"),
    ("Can you tell me the number of wins Inter Milan had in the Champions League over the past two years?", "win_count_query"),
    ("What was Napoli's win count in the Champions League in the last four years?", "win_count_query"),
    ("How many Champions League matches has Chelsea won since 2020?", "win_count_query"),
    ("Tell me the number of victories Real Madrid has secured in the Champions League since 2021.", "win_count_query"),
    ("What's Barcelona's total win count in the Champions League since 2022?", "win_count_query"),
    ("Can you provide the win statistics for Liverpool in the Champions League since 2019?", "win_count_query"),
    ("I need to know how many games Juventus has won in the Champions League since 2020.", "win_count_query"),
    ("How many matches has Bayern Munich won in the Champions League since 2019?", "win_count_query"),
    ("What were PSG's total wins in the Champions League since 2022?", "win_count_query"),
    ("Show me Manchester City's total wins in the Champions League since 2020.", "win_count_query"),
    ("How many victories has Arsenal secured in the Champions League since 2021?", "win_count_query"),
    ("Provide Borussia Dortmund's win count in the Champions League since 2021.", "win_count_query"),
    ("What is AC Milan's win total in the Champions League since 2022?", "win_count_query"),
    ("Tell me Tottenham's total wins in the Champions League since 2019.", "win_count_query"),
    ("How many matches has Ajax won in the Champions League since 2019?", "win_count_query"),
    ("Can you tell me the number of wins Inter Milan has had in the Champions League since 2021?", "win_count_query"),


    # Query for the winning percentage over the past few years
    ("What is Inter Milan's winning percentage in the past five years?", "win_percentage_query"),
    ("Tell me the win rate of AC Milan over the last 3 years", "win_percentage_query"),
    ("What's PSG's success rate from 2019 to 2023?", "win_percentage_query"),
    ("Determine Dortmund's winning percentage between 2020 and 2023", "win_percentage_query"),
    ("Calculate the win ratio for Napoli from 2019 to 2022", "win_percentage_query"),
    ("What is the winning percentage of Chelsea from 2019 to 2022?", "win_percentage_query"),
    ("Can you calculate the win rate for Real Madrid between 2019 and 2021?", "win_percentage_query"),
    ("I need the success rate of Barcelona from 2019 to 2021.", "win_percentage_query"),
    ("Show me the win percentage of Liverpool for 2019 to 2022.", "win_percentage_query"),
    ("What was Juventus' win rate from 2019 to 2023?", "win_percentage_query"),
    ("How many percent of matches did Bayern Munich win in the champions league from 2019 to 2021?", "win_percentage_query"),
    ("Determine the winning percentage for PSG from 2019 to 2022.", "win_percentage_query"),
    ("What is Manchester City's win percentage in all competitions from 2019 to 2023?", "win_percentage_query"),
    ("Calculate Arsenal's win rate in the Champions League from 2019 to 2021.", "win_percentage_query"),
    ("Tell me the win percentage of Borussia Dortmund in champions league from 2018 to 2020.", "win_percentage_query"),
    ("What is AC Milan's win rate in champions league from 2019 to 2021?", "win_percentage_query"),
    ("Provide the winning percentage of Tottenham in the champions League for 2019 to 2022.", "win_percentage_query"),
    ("What's the win percentage of Ajax in champions league from 2019 to 2021?", "win_percentage_query"),
    ("Can you show the win rate for Inter Milan in Champions League from 2020 to 2022?", "win_percentage_query"),
    ("What has been Napoli's win percentage in champions league from 2019 to 2021?", "win_percentage_query"),
    ("Give the win percentage for Atletico Madrid in Champions League from 2019 to 2021.", "win_percentage_query"),
    ("How many percent of games did Manchester United win in the Champions League from 2019 to 2022?", "win_percentage_query"),
    ("What is Sevilla's winning percentage in champions league for 2019 to 2021?", "win_percentage_query"),
    ("Calculate the winning percentage of RB Leipzig in the Champions league from 2019 to 2021.", "win_percentage_query"),
    ("Tell me Everton's win percentage in the Champions League from 2019 to 2020.", "win_percentage_query"),
    ("What is the winning percentage of Chelsea in the Champions League over the past three years?", "win_percentage_query"),
    ("Can you calculate Real Madrid's win rate in the Champions League over the past two years?", "win_percentage_query"),
    ("I need the success rate of Barcelona in the Champions League for the last four years.", "win_percentage_query"),
    ("Show me Liverpool's win percentage in the Champions League for the past three years.", "win_percentage_query"),
    ("What was Juventus' win rate in the Champions League over the past three years?", "win_percentage_query"),
    ("How many percent of matches did Bayern Munich win in the Champions League over the last two years?", "win_percentage_query"),
    ("Determine PSG's winning percentage in the Champions League for the past four years.", "win_percentage_query"),
    ("What is Manchester City's win percentage in the Champions League over the past two years?", "win_percentage_query"),
    ("Calculate Arsenal's win rate in the Champions League for the last three years.", "win_percentage_query"),
    ("Tell me Borussia Dortmund's win percentage in the Champions League over the past two years.", "win_percentage_query"),
    ("What is the winning percentage of Chelsea in the Champions League since 2020?", "win_percentage_query"),
    ("Can you calculate Real Madrid's win rate in the Champions League since 2019?", "win_percentage_query"),
    ("I need the success rate of Barcelona in the Champions League since 2021.", "win_percentage_query"),
    ("Show me Liverpool's win percentage in the Champions League since 2019.", "win_percentage_query"),
    ("What was Juventus' win rate in the Champions League since 2022?", "win_percentage_query"),
    ("How many percent of matches has Bayern Munich won in the Champions League since 2019?", "win_percentage_query"),
    ("Determine PSG's winning percentage in the Champions League since 2020.", "win_percentage_query"),
    ("What is Manchester City's win percentage in the Champions League since 2019?", "win_percentage_query"),
    ("Calculate Arsenal's win rate in the Champions League since 2021.", "win_percentage_query"),
    ("Tell me Borussia Dortmund's win percentage in the Champions League since 2019.", "win_percentage_query"),
    ("What is AC Milan's win rate in the Champions League since 2022?", "win_percentage_query"),
    ("Provide Tottenham's winning percentage in the Champions League since 2019.", "win_percentage_query"),
]

# Separate question texts and labels
X, y = zip(*train_data)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Create a pipeline combining text vectorization and logistic regression classifier
pipeline = Pipeline([
    ('vectorizer', CountVectorizer()),  # Convert text to word frequency vectors
    ('classifier', LogisticRegression())  # Use a logistic regression classifier
])

# Train the model
pipeline.fit(X_train, y_train)

#store the model
joblib.dump(pipeline, 'model.pkl')

# Test the model performance
test_queries = [
    "What was PSG's win percentage in all competitions throughout 2020?",
    "What is the total number of victories for Bayern Munich in the Bundesliga for the 2021 season?",
    "What is the winning percentage of Inter Milan in domestic league matches since 2019?",
    "Show all the Champions League games involving Sevilla from 2018 to 2020.",
    "Tell me the number of matches Liverpool won in the 2022 Champions League.",
    "Provide a summary of all the matches played by Juventus in the Champions League during the 2021-2022 season.",
    "Calculate the win rate for AC Milan in Serie A for the last two seasons.",
    "List all matches where Barcelona played in the 2020-2021 season.",
    "Detail all the Champions League matches played by Ajax in 2021.",
    "How many wins did Manchester United secure in the Premier League during the 2019-2020 season?",
    "Display all Premier League matches for Arsenal in the 2019-2020 season.",
    "What's the percentage win of Sporting CP?",
    "Tell me Tottenham's total wins in the Champions League in the last four years.",
    "win rate"
]


# Predict intents using the trained model
predictions = pipeline.predict(test_queries)
for query, prediction in zip(test_queries, predictions):
    print(f"Query: {query}\nPredicted results: {prediction}\n")

# Predict on the test set and calculate the accuracy
y_prediction = pipeline.predict(X_test)

# Calculate and print the accuracy
accuracy = accuracy_score(y_test, y_prediction)
print(f"Model accuracy: {accuracy:.2f}")


