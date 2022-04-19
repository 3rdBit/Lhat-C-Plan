import re
import json
import time
# import os.path

# import chat_functions

ip = ''
port = ''
user = ''
textbox = ''  # 用于显示在线用户的列表框
show = 1  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = 'Lhat! Chatting Room'  # 聊天对象


'''
注意：
receive函数里的用json判断用户列表和普通消息是要改的，
所以后续专门改这个东西，还有打包函数。
'''


def pack(raw_message: str, send_from, chat_with, message_type, file_name=None):
    """
    打包消息，用于发送
    :param raw_message: 正文消息
    :param send_from: 发送者
    :param chat_with: 聊天对象
    :param message_type: 消息类型
    :param file_name: 文件名，如果不是文件类型，则为None
    """
    message = {
        'by': send_from,
        'to': chat_with,
        'type': message_type,
        'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        'message': raw_message,
        'file': file_name,
        'end': 'JSON_MESSAGE_END'
    }  # 先把收集到的信息存储到字典里
    return json.dumps(message).encode('utf-8')  # 再用json打包


def unpack(json_message: str):
    """
    解包消息，用于接收JSON格式的消息
    看不懂message字典对应的东西吗？message_types里面有。

    :param json_message: JSON消息
    :return: 返回的东西有很多，也有可能是报错
    ==================================================
    return返回值大全：
    JSON_MESSAGE_NOT_EOF: 消息不完整
    NOT_JSON_MESSAGE: 不是JSON格式的消息
    MANIFEST_NOT_JSON: 用户名单不是JSON格式
    UNKNOWN_MESSAGE_TYPE: 未知消息类型
    --------------------------------------------------
    FILE_SAVED: 文件保存成功
    <一个列表>: 这是用户名单，有用的
    """
    try:
        message = json.loads(json_message)
        if message['end'] != 'JSON_MESSAGE_END':
            return 'JSON_MESSAGE_NOT_EOF'
    except json.decoder.JSONDecodeError:
        return 'NOT_JSON_MESSAGE'

    if message['type'] == 'TEXT_MESSAGE_ARTICLE':  # 如果是纯文本消息
        return message['type'], message['to'], \
               (message['by'] + f' [{message["time"]}] : \n  ' + message['message']), message['by']
    elif message['type'] == 'USER_MANIFEST':  # 如果是用户列表
        try:
            manifest = json.loads(message['message'])
            return message['type'], manifest
        except json.decoder.JSONDecodeError:
            return 'MANIFEST_NOT_JSON'

    elif message['type'] == 'FILE_RECV_DATA':
        '''
        output_box.emit('锵锵！正在接收文件...')
        file_path = os.path.join('/files/', message['message'])
        with open(file_path, 'wb') as opened_file:
            opened_file.write(message['message'])
        output_box.emit(f'接收完毕！保存路径为：{file_path}')
        return 'FILE_SAVED'
        '''
        # 待办 接收文件
    else:
        return 'UNKNOWN_MESSAGE_TYPE'


def send(connection, raw_message: str, send_from, output_box):
    """
    发送消息，但是得要TCP连接。
    """
    # 待办 更人性化且更先进的发送函数，所以函数体要更改
    # 消息类型，消息类型要改，以后使用pack()来打包消息
    chat_with = 'Lhat! Chatting Room'
    if not raw_message:
        output_box.emit('\n[提示] 发送的消息不能为空！')
        return
    elif raw_message.startswith('//tell'):  # 如果是私聊
        command_message = raw_message.split(' ')  # 分割完之后，分辨一下是否为命令
        chat_with = command_message[1]
        raw_message = re.sub('//tell', '[私聊消息] 到', raw_message)
    # message = raw_message + r'\+-*/' + send_from + r'\+-*/' + chat_with  # 打包消息，旧版的
    message = pack(raw_message, send_from, chat_with, 'TEXT_MESSAGE_ARTICLE')  # 被替换
    connection.send(message)  # 发送消息


def receive(username, window_object, signals):
    """
    接收消息，但是得要TCP连接。
    :param username: 当前接收的用户名
    :param window_object: 窗口对象，内含connection，是TCP连接
    :param signals: 绑定的信号，用于触发方法
    :param tips_box: 对话框
    """
    # 待办 更人性化且更先进的接收函数，所以函数体要更改
    # 用unpack()来解包消息
    signals.appendOutPutBox.emit('欢迎来到Lhat聊天室！大家开始聊天吧！\n'
                                 '[小提示] 使用 /tell <用户名> 来私聊！\n')
    while True:
        try:
            received_data = window_object.connection.recv(1024)  # 接收信息
        except ConnectionError:
            return
        received_data = received_data.decode('utf-8')
        print(received_data)  # ---
        message = unpack(received_data)  # 解包消息
        message_type = message[0]
        if message_type == 'TEXT_MESSAGE_ARTICLE':
            message_send_to = message[1]
            message_body = message[2]
            message_send_by = message[3]
            if message_send_to == 'Lhat! Chatting Room':  # 群聊
                signals.appendOutPutBox.emit(message_body)
            elif message_send_to == username or message_send_by == username:  # 私聊
                signals.appendOutPutBox.emit(message_body)

        elif message_type == 'USER_MANIFEST':
            message_body = message[1]
            online_users = message_body
            signals.clearOnlineUserList.emit()
            signals.appendOnlineUserList.emit('Lhat! Chatting Room')
            signals.appendOnlineUserList.emit('====在线用户====')
            for user_index, online_username in enumerate(online_users):
                # online_username是用于显示在线用户的，不要与username混淆
                signals.appendOnlineUserList.emit(str(online_username))
                # online_users[user_index] + '\n')
