#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import requests

class ChatDeepSeek():

    api_url = 'https://api.deepseek.com/chat/completions'

    def __init__(self, config) -> None:
        # 自己搭建或第三方代理的接口
        self.max_tokens = config.get("max_tokens")
        self.temperature = config.get("temperature")
        self.conversation_list = {}
        self.headers = {
            'Authorization': f'Bearer {config.get("apikey")}',
            'Content-Type': 'application/json'
        }
        self.system_content_msg = {"role": "system", "content": config.get("prompt")}
        print(self.headers)

    def get_answer(self, question: str, wxid: str) -> str:
        # wxid或者roomid,个人时为微信id，群消息时为群id
        self.updateMessage(wxid, question, "user")

        try:
            data = {
                'model': 'deepseek-chat',  # 假设使用的模型名称
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant.'},  # 系统提示
                    {'role': 'user', 'content': question}  # 用户输入
                ],
                'max_tokens': self.max_tokens,  # 生成的最大 token 数
                'temperature': self.temperature  # 控制生成文本的随机性
            }
            # 发送 POST 请求
            response = requests.post(self.api_url, headers=self.headers, json=data)

            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应内容
                result = response.json()
                # 提取生成的对话回复
                reply = result['choices'][0]['message']['content']
                self.updateMessage(wxid, reply, "assistant")
                print('Assistant:', reply)
            else:
                print(f'Error: {response.status_code}')
                print(response.text)

        except Exception as e0:
            rsp = "发生未知错误：" + str(e0)

        # print(self.conversation_list[wxid])

        return rsp

    def updateMessage(self, wxid: str, question: str, role: str) -> None:
        now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        time_mk = "当需要回答时间时请直接参考回复:"
        # 初始化聊天记录,组装系统信息
        if wxid not in self.conversation_list.keys():
            question_ = [
                self.system_content_msg,
                {"role": "system", "content": "" + time_mk + now_time}
            ]
            self.conversation_list[wxid] = question_

        # 当前问题
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)

        for cont in self.conversation_list[wxid]:
            if cont["role"] != "system":
                continue
            if cont["content"].startswith(time_mk):
                cont["content"] = time_mk + now_time

        # 只存储10条记录，超过滚动清除
        i = len(self.conversation_list[wxid])
        if i > 10:
            print("滚动清除微信记录：" + wxid)
            # 删除多余的记录，倒着删，且跳过第一个的系统消息
            del self.conversation_list[wxid][1]


if __name__ == "__main__":
    from configuration import Config
    config = Config().DEEPSEEK
    if not config:
        exit(0)
    chat = ChatDeepSeek(config)

    while True:
        q = input(">>> ")
        try:
            time_start = datetime.now()  # 记录开始时间
            print(chat.get_answer(q, "wxid"))
            time_end = datetime.now()  # 记录结束时间

            print(f"{round((time_end - time_start).total_seconds(), 2)}s")  # 计算的时间差为程序的执行时间，单位为秒/s
        except Exception as e:
            print(e)
