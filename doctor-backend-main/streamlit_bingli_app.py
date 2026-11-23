from local_config import env
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import time
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
from whisper_stt import whisper_stt, text_to_speech_ai

import extra_streamlit_components as stx
import base64
import streamlit as st
import speech_recognition as sr
import traceback

from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = env("BAIDU_OCR_APP_ID")
API_KEY = env("BAIDU_OCR_API_KEY")
SECRET_KEY = env("BAIDU_OCR_SECRET_KEY")

ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def set_page_container_style(
        max_width: int = 1100, max_width_100_percent: bool = True,
        padding_top: int = 1, padding_right: int = 3, padding_left: int = 1, padding_bottom: int = 3,
        color: str = "black", background_color: str = "white",
):
    if max_width_100_percent:
        max_width_str = f'max-width: 100% !important;'
    else:
        max_width_str = f'max-width: {max_width}px !important;'
    st.markdown(
        f'''
            <style>
                .reportview-container .sidebar-content {{
                    padding-top: {padding_top}rem;
                }}
                .reportview-container .main .block-container div[data-testid="block-container"] {{
                    {max_width_str}
                    padding: {padding_top}rem {padding_right}rem {padding_bottom}rem {padding_left}rem !important;
                }}
                .block-container {{
                    {max_width_str}
                    padding: {padding_top}rem {padding_right}rem {padding_bottom}rem {padding_left}rem !important;
                }}
                div[data-testid="block-container"] {{
                    {max_width_str}
                    padding: {padding_top}rem {padding_right}rem {padding_bottom}rem {padding_left}rem !important;
                }}
                .reportview-container .main {{
                    color: {color} !important;
                    background-color: {background_color} !important;
                }}
            </style>
            ''',
        unsafe_allow_html=True,
    )


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


def speech_to_text(audio):
    r = sr.Recognizer()
    try:
        text = r.recognize_whisper_api(sr.AudioFile(audio))
        print('recognized text: ' + text)
        return text
    except Exception as ex:
        print('Sorry could not recognize your voice:' + str(ex))
        return '请重说'


def main():
    try:
        set_page_container_style(max_width_100_percent=True, color="black", background_color="white")
        msgs = StreamlitChatMessageHistory()
        reports = []
        index = 1
        all_report = ""
        # agent = OpenAIAssistantRunnable(assistant_id="asst_4QDqKdQamXFTjYi0ib6g3Rck", as_agent=True)
        # agent = OpenAIAssistantV2Runnable(assistant_id="asst_H0pPWMD50Nhdr61k2RgglZ24", as_agent=True)

        # agent = OpenAIAssistantV2Runnable(assistant_id="asst_tNIX4bgPaHUFFeG1PpHBv1Ti", as_agent=True)
        # agent.client.base_url="https://gateway.ai.cloudflare.com/v1/f2580bfc5d6902b6fc8a063d69d049ef/open-ai/openai"
        # agent_executor = AgentExecutor(agent=agent, tools=[])
        # chat = ChatOpenAI(model_name='gpt-4o-2024-05-13', temperature=0)

        # agent.client.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # # agent_executor = AgentExecutor(agent=agent, tools=[])
        chat = ChatOpenAI( base_url = "https://openai.arnotho.com/v1",model_name='gpt-4o-2024-05-13',
                          temperature=0.2)
        with st.container():
            # input1 = st.text_input("问诊信息")
            # input2 = st.text_input("检查报告")
            input3 = st.text_input("指令")
            input1 = st.text_area("问诊记录", height=250)
            input2=st.text_area("检查报告 OCR 文本", height=200)
            if st.button("点击根据问诊和报告生成病历"):
                # st.session_state['reports'] = set(st.session_state['reports'])

                # all_words = ",".join([word['words'] for res_image in st.session_state['reports'] for word in res_image['words_result']])
                messages = [
                    SystemMessage(
                        content=input3
                    ),
                    HumanMessage(
                        content=f"患者和你的聊天记录是：\n{input1}\n患者上传的检查报告内容是：\n{input2}"
                    ),
                ]

                print("generating")

                    # st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                    # config = {
                    #    'callbacks' : [st_cb]
                    # }
                    # response = generate_response("嘿嘿嘿", chat, msgs)
                response = chat.invoke(messages)
                print(response.content)
                    # msgs.add_ai_message(response["content"])
                st.write(response.content)
    except Exception as ex:

        print(str(ex))
        exception_traceback = traceback.format_exc()
        print(exception_traceback)
        return '请重说'




if __name__ == '__main__':
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = ''
    if ('button_message' not in st.session_state):
        st.session_state['button_message'] = "开始说话"
        st.session_state['status'] = ""
    if ('text' not in st.session_state):
        st.session_state['text'] = ''
        st.session_state['reports'] = []

    main()
