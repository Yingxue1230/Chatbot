<template>
  <div id="app" class="background">
    <div id="chatbot">
      <div id="chat-window" ref="chatWindow">
        <div v-for="(message, index) in messages" :key="index" class="message">
         <div v-if="!message.table" :class="{'user-message': message.sender === 'user', 'bot-message': message.sender === 'bot'}" v-html="message.content">
   <!-- 通过 v-html 渲染消息内容，以支持 HTML 格式（如换行 <br>） -->
         </div>


    <!-- 显示表格信息 -->
          <table v-if="message.table" class="match-table">
           <thead>
             <tr>
              <th>Date</th>
              <th>Home Team</th>
              <th>Home Score</th>
              <th>Away Score</th>
              <th>Away Team</th>
              <th>Stadium</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="match in message.table" :key="match.MATCH_ID">
                <td>{{ formatDate(match.DATE_TIME) }}</td>
                <td>{{ match.HOME_TEAM }}</td>
                <td>{{ match.HOME_TEAM_SCORE }}</td>
                <td>{{ match.AWAY_TEAM_SCORE }}</td>
                <td>{{ match.AWAY_TEAM }}</td>
                <td>{{ match.STADIUM }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <input type="text" v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." class="input-field">
      <button @click="sendMessage" class="send-button">Send</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'session:';
export default {
  data() {
    return {
      newMessage: '',
      messages: [],
      errorMessage: '',
      stage: 'question_type',
      typeId: '',
      teamName: ''
    };
  },
  mounted() {
    //初始化消息
    this.messages.push({ sender: 'bot', content: "Hello! I'm your football chatbot. You can ask me something about Champions League from 2019-2023." });
    // 然后请求 Flask 后端的 /start 端点获取初始询问消息
    axios.get('http://127.0.0.1:5000/start',{ withCredentials:true })
      .then(response => {
        // 接收并显示来自 Flask 的第二条消息
        this.messages.push({
          sender: 'bot',
          content: response.data.message
        });
        //从响应中设置初始阶段
        //this.stage = response.data.stage
        // 确保视图更新后滚动到最新消息
        this.$nextTick(this.scrollToBottom);
      })
      .catch(error => {
        // 处理错误情况，例如网络问题或服务器错误
        const errorMessage = error.response ? error.response.data.message : 'Network error, please try again later.';
        this.messages.push({
          sender: 'bot',
          content: errorMessage
        });
        this.$nextTick(this.scrollToBottom);
      });
  },

  methods: {

    // 让日期只显示年、月、日
    formatDate(dateStr) {
      const date = new Date(dateStr);
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0'); // 加1因为月份是从0开始的
      const day = date.getDate().toString().padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    sendMessage() {
      if (this.newMessage.trim() === '') {
        return;
      }

      const userMessage = this.newMessage.trim();
      this.messages.push({
        sender: 'user',
        content: userMessage,
      });

      //发送消息到Flask应用
      let apiEndpoint = '';
      let payload = {};
      //根据阶段来分配给相应流程
      if (this.stage === 'question_type'){
        apiEndpoint = 'http://127.0.0.1:5000/set_question_type';
        payload = {question_type: userMessage,stage_value:this.stage};
      } else if (this.stage === 'team'){
        apiEndpoint = 'http://127.0.0.1:5000/set_team';
        payload = {team: userMessage,stage_value:this.stage};
      } else if (this.stage === 'year'){
        apiEndpoint = 'http://127.0.0.1:5000/set_year';
        payload = {year: userMessage,stage_value:this.stage,typeId: this.typeId,teamName: this.teamName};
      } else if (this.stage === 'if_continue'){
        apiEndpoint = 'http://127.0.0.1:5000/if_continue';
        payload = {if_continue: userMessage,stage_value:this.stage};
      } else if (this.stage === 'predict'){
        apiEndpoint = 'http://127.0.0.1:5000/predict';
        payload = {question: userMessage,stage_value:this.stage};
      } else if (this.stage === 'give_feedback'){
        apiEndpoint = 'http://127.0.0.1:5000/give_feedback';
        payload = {feedback: userMessage,stage_value:this.stage,typeId: this.typeId,teamName: this.teamName};
      }

axios.post(apiEndpoint, payload, { withCredentials: true })
    .then(response => {
      //增加延迟
      setTimeout(() => {
        // 首先推送文本消息
        this.messages.push({
          sender: 'bot',
          content: response.data.message
        });

        // 如果有表格，再将其作为消息添加
        if (response.data.data && response.data.data.length > 0) {
          this.messages.push({
            sender: 'bot',
            table: response.data.data,
          });
        }

        if (response.data.ask) {
          this.messages.push({
            sender: 'bot',
            content: response.data.ask
          });
        }

        // 更新阶段
        this.stage = response.data.nextStage || this.stage;
        this.teamName = response.data.teamName || this.teamName;
        this.typeId = response.data.typeId || this.typeId
        console.log(this.stage)
        // 滚动到底部
        this.$nextTick(this.scrollToBottom);
      }, 500);
    })
        .catch(error => {
          const errorMessage = error.response ? error.response.data.message : 'Network error, please try again later.';
          this.messages.push({
            sender: 'bot',
            content: errorMessage,
            type: 'error'
          });
          this.$nextTick(this.scrollToBottom);
        })
        .finally(() => {
          this.newMessage = '';
          this.$nextTick(this.scrollToBottom);
        });
    },
    // 让页面自动滑到底部
    scrollToBottom(){
      const chatWindow = this.$refs.chatWindow;
      chatWindow.scrollTop = chatWindow.scrollHeight;
    },
  },
};
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0px;
}

#chat-window {
  background-color: rgba(255, 255, 255, 0.90);
  height: 600px;
  width: 1200px;
  overflow-y: scroll;
  border: 2px solid #ccc;
  padding: 10px;
  margin: 0 auto 15px; /* 确保水平居中且底部有适当间距 */
  border-radius: 15px;
  position: relative; /* 设置为相对定位 */
  top: 30px;
}

.background{
  /* WebP format for supported browsers */
  background-image: url('~@/assets/background.jpeg');

  min-height: 100%;
  margin: 0;
  padding: 0;
  background-size: cover; /* Cover the entire page */
  background-position: center center; /* Center the background image */
  background-repeat: no-repeat;
  height: 100%; /* Full height */
  width: 100%; /* Full width */
  background-attachment: fixed;
}

.message {
  clear: both;
  font-size: 20px;
  margin: 15px 0;
}

.user-message {
  font-size: 20px;
  text-align: right;

}

.bot-message {
  text-align: left;
}

.user-message, .bot-message {
  //white-space: pre-line;
  position: relative; /* 设置定位上下文 */
  padding: 10px;
  border-radius: 10px;
  display: inline-block;
  margin-bottom: 15px;
  font-weight: 500;
}

.user-message {
  background-color: #007bff;
  color: #ffffff;
  text-align: right;
  float: right;
  right: 5px;
}

.user-message:after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  border-width: 10px 10px 0 0;
  border-style: solid;
  border-color: #007bff transparent transparent transparent;
  /* 调整气泡的位置 */
  transform: translate(50%, 50%);
}

.bot-message {
  background-color: #f5da78;
  text-align: left;
  float: left;
  left: 5px;
}

.bot-message:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  border-width: 10px 0 0 10px;
  border-style: solid;
  border-color: #f5da78 transparent transparent transparent;
  /* 调整气泡的位置 */
  transform: translate(-50%, 50%);
}


.input-field {
  margin-top: 50px;
  width: 800px; /* 调整宽度 */
  height: 35px; /* 调整高度 */
  font-size: 20px; /* 调整字体大小 */
  padding: 0 15px; /* 增加一些内边距 */
  border-radius: 10px;
}

.send-button {
  margin-top: 0px;
  width: 80px; /* 调整宽度 */
  height: 35px; /* 调整高度 */
  margin-left: 10px; /* 增加左边距来远离输入框 */
}

.match-table {
  width: 90%;
  border-collapse: collapse;
  margin-top: 20px;
  front-size: 14px;
  background-color: #ffffff;
}

.match-table th,
.match-table td {
  border: 3px solid #f5da78;
  padding: 3px; /* 单元格内边距 */
  text-align: center; /* 文本左对齐 */
}

.match-table th {
  background-color: #f5da78; /* 表头背景颜色 */
}

</style>
