from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage

# create sync sql message history by connection_string
message_history = SQLChatMessageHistory(
    session_id='test',
    connection='mysql+pymysql://root:root@localhost/ai_ability_platform?charset=utf8mb4',
    table_name='chat_message',
)
# message_history.add_message(HumanMessage("hello2"))
# print(message_history.get_messages())
for mes in message_history.get_messages():
    print(mes)