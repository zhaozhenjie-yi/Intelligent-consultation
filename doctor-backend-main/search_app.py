from local_config import env
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import SearchApplicationClient
from langchain.agents import AgentExecutor, AgentType,  ConversationalChatAgent, initialize_agent, Tool, load_tools, ZeroShotAgent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain.memory import ConversationBufferMemory,ConversationSummaryMemory, ConversationSummaryBufferMemory, ConversationKGMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory.chat_message_histories.mongodb import MongoDBChatMessageHistory
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.callbacks import StreamlitCallbackHandler
from streamlit_chat import message
from streamlit_javascript import st_javascript

import extra_streamlit_components as stx
import base64
import hashlib
import os
import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import sys
import json
import requests

client = Elasticsearch(env("ELASTICSEARCH_URL"), http_auth=(env("ELASTICSEARCH_USERNAME"), env("ELASTICSEARCH_PASSWORD")))
searchclient = SearchApplicationClient(client)

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.delta_generator.DeltaGenerator, initial_text: str = ""):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # Workaround to prevent showing the rephrased question as output
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.text += token
        self.container.markdown(self.text)

def main():
    msgs = StreamlitChatMessageHistory()
    chat = ChatOpenAI(model_name='gpt-4-1106-preview', temperature=0, streaming=True)
    with st.container():
        avatars = {"human": "user", "ai": "assistant"}
        if len(msgs.messages) == 0:
            msgs.clear()
            msgs.add_ai_message("请在这里搜索论文~")
        for msg in msgs.messages:
            st.chat_message(avatars[msg.type]).write(msg.content)
        ppt_title = st.text_input("请输入ppt标题")
        if st.button('根据当前对话生成ppt'):
            with st.chat_message("assistant"):
                messages_ppt = [
                    SystemMessage(
                        content="你是一位科研人员，你需要综合拟定的标题和我们我们刚才的对话记录，为我用markdown格式生成一个PPT的大纲，根据我们的搜索结果生成每一页对应的具体内容，格式对我很重要"
                    ),
                    HumanMessage(
                        content="我设置的ppt主题为: " + ppt_title + "\n之前的搜索记录为：\n" + "\n".join(st.session_state['history'])
                    )
                ]
                print("\n".join(st.session_state['history']))
                st_cb = StreamHandler(st.empty())
                config = {
                    'callbacks' : [st_cb]
                }
                response = chat.invoke(messages_ppt, config=config)
        if user_input := st.chat_input():       
            with st.chat_message("assistant"):
                messages_translate = [
                    SystemMessage(
                        content="我会提供给你一个文本query，你需要充分理解query内容，然后将其简化，尽可能展开缩写，尽可能形成一个容易理解语句通顺的query, 一定要翻译成英文，这对我很重要。我只需要最后翻译好的英文结果，不需要其他任何文本，我需要在搜索中使用，这对我很重要"
                    ),
                    HumanMessage(
                        content=user_input
                    )
                ]
                response = chat.invoke(messages_translate)
                st.write('自动生成的智能搜索语句：' + response.content)
                search_result = client.search(index="pubmed", query={"multi_match": {"query": response.content, "fields": ['Article Title', 'Abstract']}})
                st.write('搜索完毕，整理文档')
                #print(search_result['hits'])
                messages_summary = [
                    SystemMessage(
                        content="我会提供给你一个query和JSON形式的搜索结果列表，希望你一定根据搜索结果列表的内容来回答query，需要体现具体数字指标，，最终回答尽可能详细严谨，要符合事实，同时保证简洁，不可以捏造自行创作，体现你的专业性，字数在500字左右吧。尽可能用markdown呈现结构化答案吧，这对我很重要。结果用中文。"
                    ),
                    HumanMessage(
                        content='User Query: ' + user_input
                    ),
                    HumanMessage(
                        content='\n Reference: \n' + str(search_result['hits'])
                    )
                ]
                #response = chat.invoke(messages_summary)
                st_cb = StreamHandler(st.empty())
                config = {
                    'callbacks' : [st_cb]
                }
                summary_response = chat.invoke(messages_summary, config=config)
                st.session_state['history'].append(user_input)
                st.session_state['history'].append(summary_response.content)
                st.write('整理完毕')
                #st.markdown(response.content, unsafe_allow_html=True)

if __name__ == '__main__':
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = ''
    if('button_message' not in st.session_state):
        st.session_state['button_message'] = "开始说话"
        st.session_state['status'] = ""
    if('history' not in st.session_state):
        st.session_state['history'] = []
    
    main()
