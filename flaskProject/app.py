import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session #导入回话扩展
import joblib
import pandas as pd
from coursework.get_keywords import find_question_type, find_team, find_team2, get_year
from feedback_db import db, Feedback


app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#配置会话管理，这样可以交互式会话，每一步的输出都可以基于之前步骤的输入
app.config['SESSION_PERMANENT'] = False #会话生命周期不会永久持续
app.config['SESSION_TYPE'] = 'filesystem' #回话会将数据存储在服务器的文件系统中
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config['SECRET_KEY'] = 'my_key' #增加秘钥
Session(app)

CORS(app, supports_credentials=True)


# 基于app.py的位置构建模型和数据文件的路径
basedir = os.path.abspath(os.path.dirname(__file__))
model_path = os.path.join(basedir, 'coursework', 'model.pkl')
data_path = os.path.join(basedir, 'coursework', 'Champions League 2019-2023 Data.xlsx')

#加载训练好的模型
model = joblib.load("coursework/model.pkl")

#加载数据库
df = pd.read_excel("coursework/Champions League 2019-2023 Data.xlsx")

#读取所有队伍名称
all_teams = df['HOME_TEAM'].unique()


@app.route('/start', methods=['GET'])
def start():
    #每次都清除之前的数据
    session.clear()
    #将状态定为寻找问题类型
    session['stage'] = 'question_type'
    session.modified = True
    print("start接口——session['stage']:",session['stage'])
    message = ("You can choose one type of question to ask:<br>" +
          "1. All game information of one team during a specific time period.<br>" +
          "2. The winning information of one team within a specific time.<br>" +
          "3. The win percentage of one team in a period of time.<br>"+
          "4. I want to describe the question by myself!<br>"+
          "You can type the number of question you would like to.")
    return jsonify({'message': message})


@app.route('/set_question_type', methods=['POST'])
def set_question_type():
    session['stage'] = request.json.get('stage_value')
    print("用户输入问题类型后，初始化后的session['stage']:",session.get('stage'))
    # print(session)
    #如果状态不是寻找问题类型，报错
    #if session.get('stage') != 'question_type':
        #return jsonify({'error': 'Unexpected stage'}), 400
    #获取用户回答并且进行分类
    question_text = request.json.get('question_type')
    print("question_text:",question_text)
    question_type = find_question_type(question_text)
    print("question_type:",question_type)

    #如果获取失败，报错
    if question_type is None:
        return jsonify({'error': 'Invalid query type selected'}), 400
    #将获取的问题类型存入类型中
    session['question_type'] = question_type
    print("用户输入的问题类型存入session:",session.get('question_type'))
    #如果用户想直接一次性输入问题，跳转到predict
    if question_type == '4':
        return jsonify({'message': "Please provide a complete description of your question, including the type of your question, team name and time period.","nextStage": "predict"})
    #保存数据
    session.modified = True
    #下一个状态是team
    session['stage'] = 'team'
    print("session['stage']:",session['stage'])
    return jsonify({"message": "Which team are you interested in?", "nextStage": "team", "typeId": question_type})

@app.route('/set_team', methods=['POST'])
def set_team():
    session['stage'] = request.json.get('stage_value')
    print(session.get('stage'))
    #如果状态不是寻找队伍，报错
    #if session.get('stage') != 'team':
        #return jsonify({'error': 'Unexpected stage'}), 400
    print("request.json",request.json)
    team_answer = request.json.get('team')
    print("team_answer:",team_answer)
    team = find_team(team_answer, all_teams)
    print("team:",team)
    #如果找不到队伍，报错
    if team is None:
        return jsonify({'error': 'Team not found'}), 400
    #将获取的队伍存入数据
    session['team'] = team
    #保存数据
    session.modified = True
    print(session.get('team'))
    #下一个阶段是查找年份
    session['stage'] = 'year'
    print("stage:",session['stage'])
    return jsonify({"message": "What range of years do you want to know about this team?", "nextStage":"year", "teamName":team})


@app.route('/set_year', methods=['POST'])
def set_year():
    #如果状态不是寻找年份，报错
    #if session.get('stage') != 'year':
        #return jsonify({'error': 'Unexpected stage'}), 400
    #对回答进行获取
    session['stage'] = request.json.get('stage_value')
    year_answer = request.json.get('year')
    try:
        start_year, end_year = get_year(year_answer)
        session['start_year'] = start_year
        session['end_year'] = end_year
        print(session['start_year'], session['end_year'])
        session['stage'] = 'complete'
        typeId = request.json.get('typeId')
        teamName = request.json.get('teamName')
        return final_query(typeId,teamName)
    except ValueError as e:
        return handle_value_error(e)
    except Exception as e:
        return handle_exception(e)

def final_query(question_type,team):
    print(question_type,team,session.get('start_year'),session.get('end_year'))
    start_year = session.get('start_year')
    end_year = session.get('end_year')

    # 确保所有需要的信息都已经获取
    if not all([question_type, team, start_year, end_year]):
        return jsonify({"error": "Missing data for query execution."}), 400

    try:
        #根据不同的类型，返回相应的函数
        if question_type == '1':
            response = match_info_query(team, start_year, end_year)
        elif question_type == '2':
            response =  win_count_query(team, start_year, end_year)
        elif question_type == '3':
            response =  win_percentage_query(team, start_year, end_year)
        else:
            raise ValueError("Invalid question type")

        #获取查询结果的JSON数据
        response_data = response.get_json()

        #询问是否需要继续
        session['stage'] = 'ask_if_continue'
        #存储数据
        session.modified = True
        print(session.get('stage'))

        return jsonify({
            "message":response_data.get('message'),
            "data": response_data.get('data', None),
            "nextStage": "ask_if_continue",
            "ask": "Do you want to start again or exit? Type 'yes' to restart or 'no' to end.",
            "nextStage": "if_continue"
        })

    except Exception as e:
        return handle_exception(e)

@app.errorhandler(ValueError)
def handle_value_error(error):
    #从ValueError中得到错误信息
    return jsonify({'error': "Invalid input", "message": str(error)}), 400

@app.errorhandler(Exception)
def handle_exception(error):
    #普通的错误处理
    return jsonify({'error': "Internal Server Error", "message": str(error)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    session['stage'] = request.json.get('stage_value')
    print(session.get('stage'))
    try:
        #获取用户发送的json数据
        user_message = request.json.get('question')

        #使用模型预测查询的意图
        prediction = model.predict([user_message])[0]

        #根据输入查找队伍
        team = find_team(user_message,all_teams)

        #根据输入查找对应年份
        start_year, end_year = get_year(user_message)

        #根据预测结果调用相应的函数
        if prediction == "match_info_query":
            question_type = 1
            response = match_info_query(team, start_year, end_year)
        elif prediction == "win_count_query":
            question_type = 2
            response = win_count_query(team, start_year, end_year)
        elif prediction == "win_percentage_query":
            question_type = 3
            response = win_percentage_query(team, start_year, end_year)
        else:
            raise ValueError("Invalid question type")

        #获取查询结果的JSON数据
        response_data = response.get_json()

        #询问是否需要继续
        session['stage'] = 'ask_if_continue'
        #存储数据
        session.modified = True
        print(session.get('stage'))

        return jsonify({
            "message":response_data.get('message'),
            "data": response_data.get('data', None),
            "nextStage": "ask_if_continue",
            "ask": "Do you want to start again or exit? Type 'yes' to restart or 'no' to end.",
            "nextStage": "if_continue",
            "typeId": question_type,
            "teamName": team
        })

    except ValueError as e:
        return handle_value_error(e)
    except Exception as e:
        return handle_exception(e)


#求球队的所有比赛信息
@app.route('/match_info_query', methods=['POST'])
def match_info_query(team, start_year, end_year):
    try:
        #获取用户发送的json数据
        #data = request.json
        #获取用户输入的信息
        #user_message = data['message']

        # 使用get_keywords.py中的函数提取队伍名称和开始、结束年份
        # team = find_team(user_message, all_teams)
        # start_year, end_year = get_year(user_message)

        # 得到相应的球队在规定时间内的信息
        team_info = df[((df['HOME_TEAM'] == team) | (df['AWAY_TEAM'] == team))
                   & (df['SEASON'] >= start_year)
                   & (df['SEASON'] <= end_year)]

        # 将结果以列表形式返回
        if not team_info.empty:
            return jsonify({
                "message": f"Here are the matches of {team} from {start_year} to {end_year}.",
                "data": team_info.to_dict(orient='records')
            })
        else:
            return jsonify({"message": "No matches found."}), 404
    except ValueError as e:
        return handle_value_error(e)
    except Exception as e:
        return handle_exception(e)


#求所有获胜信息
@app.route('/win_count_query', methods=['POST'])
def win_count_query(team, start_year, end_year):
    # 获取用户发送的json数据
    #data = request.json
    # 获取用户输入的信息
    #user_message = data['message']

    try:
        # 使用get_keywords.py中的函数提取队伍名称和开始、结束年份
        #team = find_team(user_message, all_teams)
        #start_year, end_year = get_year(user_message)

        # 从数据库中获取符合条件的信息
        team_info = df[(((df['HOME_TEAM'] == team) & (df['Result'] == "Home team wins")) |
                    ((df['AWAY_TEAM'] == team) & (df['Result'] == "Away team wins")))
                   & (df['SEASON'] >= start_year)
                   & (df['SEASON'] <= end_year)]

        # 计算赢的数量
        win_count = team_info.shape[0]

        # 返回响应
        if win_count > 0:
            return jsonify({
                "data": team_info.to_dict(orient='records'),
                "message": f"{team} have won {win_count} game(s) from {start_year} to {end_year}."
            })

        else:
            return jsonify({"message": "No matches found for the team in the given season."}), 404
    except ValueError as e:
        return handle_value_error(e)
    except Exception as e:
        return handle_exception(e)


#求制定球队的胜率
@app.route('/win_percentage_query', methods=['POST'])
def win_percentage_query(team, start_year, end_year):
    # 获取用户发送的json数据
    #data = request.json
    # 获取用户输入的信息
    #user_message = data['message']

    try:
        # 使用get_keywords.py中的函数提取队伍名称和开始、结束年份
        #team = find_team(user_message, all_teams)

        #获取开始和结束年份
        #start_year, end_year = get_year(user_message)


        # 从数据库中获取符合条件的信息
        team_info = df[(((df['HOME_TEAM'] == team) & (df['Result'] == "Home team wins")) |
                    ((df['AWAY_TEAM'] == team) & (df['Result'] == "Away team wins")))
                   & (df['SEASON'] >= start_year)
                   & (df['SEASON'] <= end_year)]

        # 计算赢的数量
        win_count = team_info.shape[0]
        #print(win_count)

        # 获取所有的比赛场次
        match_info = df[((df['HOME_TEAM'] == team) | (df['AWAY_TEAM'] == team))
                    & (df['SEASON'] >= start_year)
                    & (df['SEASON'] <= end_year)]

        # 计算一共参加了多少场比赛
        match_count = match_info.shape[0]
        #print(match_count)

        # 计算胜率
        win_percentage = win_count / match_count

        if match_count > 0:
            return jsonify({
                "message": f"{team} have won {win_count} of {match_count} matches from {start_year} to {end_year}. "
                           f"The win percentage of {team} is {win_percentage:.2f} from {start_year} to {end_year}."
            })

        else:
            return jsonify({"message": "No matches found for the team in the given season."}), 404
    except ValueError as e:
        return handle_value_error(e)
    except Exception as e:
        return handle_exception(e)


@app.route('/if_continue', methods=['POST'])
def if_continue():
    session['stage'] = request.json.get('stage_value')
    print("用户输入问题类型后，初始化后的session['stage']:", session.get('stage'))

    #获取用户消息
    user_response = request.json.get('if_continue')
    #如果用户回答是，则重新开始
    if user_response.lower() in ['yes', 'true', 't', 'y', '1']:
        session.clear()
        #输入欢迎语
        message = ("Let's start a new query!<br>"+
          "You can choose one type of question to ask:<br>" +
          "1. All game information of one team during a specific time period.<br>" +
          "2. The winning information of one team within a specific time.<br>" +
          "3. The win percentage of one team in a period of time.<br>"+
          "4. I want to describe the question by myself!<br>"+
          "You can type the number of question you would like to.")

        return jsonify({
            "message": message,
            "nextStage": "question_type"
        })
    else:
        session.clear()
        #输入结束语，但是在结束之前请用户给予反馈
        message = ("Thanks for using our service! Are you satisfied with the results?<br>"+
                   "1. Yes<br>"+
                   "2. No<br>")
        return jsonify({"message": message,"nextStage": "give_feedback"})


@app.route('/give_feedback', methods=['POST'])
def give_feedback():
    try:
        user_feedback = str(request.json.get('feedback'))
        print(user_feedback)
        question_type = str(request.json.get('typeId'))
        print(question_type)
        team_name = str(request.json.get('teamName'))
        print(team_name)

        #创建feedback实例
        new_feedback = Feedback(feedback=user_feedback, question_type=question_type,team_name=team_name)

        #将反馈对象添加到数据库会话中并提交保存
        db.session.add(new_feedback)
        db.session.commit()


        #返回成功的响应
        return jsonify({"message":"Thank you for your feedback! See you again!"})

    except Exception as e:
        return jsonify({"Failed to submit feedback"}), 500

# 确保数据库创建
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
