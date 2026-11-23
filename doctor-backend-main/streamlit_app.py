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
system_prompt = ""


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
        # chat = ChatOpenAI(base_url="https://openai.arnotho.com/v1",
        #                  temperature=0)

        chat = ChatOpenAI(base_url="https://api.deepseek.com/v1",
                          api_key=env("DEEPSEEK_API_KEY"), model_name='deepseek-chat',
                          temperature=0)
        # agent.client.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # # agent_executor = AgentExecutor(agent=agent, tools=[])
        #                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model_name='qwen-max',
        #                   temperature=0)
        with st.container():
            avatars = {"human": "user", "ai": "assistant"}
            if len(msgs.messages) == 0:
                msgs.clear()
                msgs.add_ai_message("请问您的姓名是")
            for msg in msgs.messages:
                st.chat_message(avatars[msg.type]).write(msg.content)
            st.session_state['text'] = ''
            # wav_audio_data = st_audiorec()
            # if wav_audio_data:
            response = whisper_stt(language='zh')
            st.session_state['text'] = st.session_state._last_speech_to_text_transcript
            uploaded_file = st.file_uploader("选择报告图片")
            if uploaded_file is not None:
                res_image = ocr_client.basicGeneral(uploaded_file.getvalue())
                print(res_image)
                reports.append(res_image)
                st.session_state['reports'].append(res_image)
                print(len(st.session_state['reports']))
                st.session_state['report_text'] = res_image
                report_words = map(lambda x: ",".join(
                    [words['words'] for words in x["words_result"]]), st.session_state['reports'])
                report_list = list(report_words)
                report_set = set(report_list)
                report_list = list(report_set)
                index = 1
                all_report = ""
                for s in report_list:
                    all_report += (",报告" + str(index) + ":" + str(s) + "\n")
                    index += 1

                # messages = [
                #     SystemMessage(
                #         content="你是一位泌尿外科的医生，根据目前你和患者的聊天记录和患者上传的检查报告，你需要生成病历"
                #     ),
                #     HumanMessage(
                #         content="患者和你的聊天记录是：\n" + "\n".join([msg.content for msg in msgs.messages])
                #     ),
                #     HumanMessage(
                #         content="\n患者上传的检查报告内容是：\n" + ",".join([words['words'] for words in res_image["words_result"]])
                #     ),
                # ]
                # with st.chat_message("assistant"):
                #     #st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                #     #config = {
                #     #    'callbacks' : [st_cb]
                #     #}
                #     response = chat.invoke(messages)
                #     #msgs.add_ai_message(response["content"])
                #     st.write(response.content)

            system_prompt = st.text_input("prompt")
            if st.session_state['text'] == '请重说':
                msgs.add_ai_message(st.session_state['text'])
            elif user_input := st.chat_input() or (
                    st.session_state['text'] is not None and len(st.session_state['text']) > 0):
                if st.session_state['text'] is not None and len(st.session_state['text']) > 0:
                    msgs.add_user_message(st.session_state['text'])
                    st.chat_message("user").write(st.session_state['text'])
                    user_input = st.session_state['text']
                else:
                    msgs.add_user_message(user_input)
                    st.chat_message("user").write(user_input)
                with st.chat_message("assistant"):
                    # st_cb = StreamCHandler(st.container())
                    # if len(st.session_state['thread_id']) == 0:
                    #     response = agent_executor.invoke({"content": user_input})
                    #     st.session_state['thread_id'] = response['thread_id']
                    # else:
                    #     response = agent_executor.invoke({"content": user_input, 'thread_id': st.session_state['thread_id']})

                    response = generate_response(user_input, chat, msgs, system_prompt)
                    msgs.add_ai_message(response.content)
                    print("[agent_executor.invoke.input]: " + user_input)
                    print("[agent_executor.invoke.response]: " + response.content)

                    st.write(response.content)
                    # speech_file_path = 'audio_response.mp3'
                    # text_to_speech_ai(speech_file_path, response.content)
                    # autoplay_audio(speech_file_path)
                    st.session_state['text'] = ''
                    st.session_state['status'] = ''
                    st.session_state['button_message'] = "开始说话"

            # if st.button("导出问诊对话信息"):
            #     file_content = "患者和你的聊天记录是：\n" + "\n".join([msg.content for msg in msgs.messages])
            #
            #     # 将文件内容转换为字节流
            #     file_bytes = file_content.encode('utf-8')

            "\n".join([f"{'医生' if msg.type == 'ai' else '患者'}:{msg.content}" for msg in msgs.messages])
            # 创建下载按钮
            st.download_button(
                label="下载对话记录（可用于生成病历）",
                data=("患者和你的聊天记录是：\n" + "\n".join(
                    [f"{'医生' if msg.type == 'ai' else '患者'}:{msg.content}" for msg in msgs.messages])).encode('utf-8'),
                file_name="对话.txt",
                mime="text/plain"
            )
            st.download_button(
                label="下载检查报告记录（可用于生成病历）",
                data=("\n患者上传的检查报告的OCR结果是：\n" + all_report).encode('utf-8'),
                file_name="检查报告.txt",
                mime="text/plain"
            )
            st.download_button(
                label="下载token数据",
                data=("\n st.session_state['prompt_cache_hit_tokens']：\n" + str(
                    sum( st.session_state['prompt_cache_hit_tokens'])) + '\n' + " st.session_state['prompt_cache_miss_tokens']：\n" + str(
                    sum( st.session_state['prompt_cache_miss_tokens'])) + '\n'+" st.session_state['input_tokens']：\n" + str(
                    sum( st.session_state['input_tokens'])) + '\n'+" st.session_state['output_tokens']：\n" + str(
                    sum( st.session_state['output_tokens'])) + '\n').encode('utf-8'),
                file_name="token.txt",
                mime="text/plain"
            )
            if st.button("点击结束对话生成病历"):
                # st.session_state['reports'] = set(st.session_state['reports'])

                # all_words = ",".join([word['words'] for res_image in st.session_state['reports'] for word in res_image['words_result']])
                messages = [
                    SystemMessage(
                        content="你是一位泌尿外科的医生，根据目前你和患者的聊天记录和患者上传的检查报告，你需要生成病历，其中主诉需要凝练（20字以内），多个症状，一般加上“伴”，例如临床中，一般会写成：血尿2月伴尿痛1月，其中针对病人的检查报告需要检查的日期（精确到日，不需要分时）+某某医院后边什么科室不需要，针对检查报告只需要诊断结果，不需要诊断现象描述。另外在生成病历时要注意使用专业的医疗用语，例如：如:尿血2个月（应该是血尿）；整个排尿过程（应该是全程）； 患者自诉尿中有血，所以是肉眼可见了，临床中，专业术语应该是 全程肉眼血尿； 疼痛为火辣辣感，应该是灼烧感。"
                    ),
                    HumanMessage(
                        content="患者和你的聊天记录是：\n" + "\n".join(
                            [f"{'医生' if msg.type == 'ai' else '患者'}:{msg.content}" for msg in msgs.messages])
                    ),

                    HumanMessage(
                        content="\n患者上传的检查报告内容是：\n" + all_report
                    ),
                ]
                with open("conversion.txt", "w") as f:
                    f.write("患者和你的聊天记录是：\n" + "\n".join([msg.content for msg in msgs.messages]))
                    f.write("\n")
                    f.write("\n患者上传的检查报告内容是：\n" + all_report)

                with st.chat_message("assistant"):
                    # st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                    # config = {
                    #    'callbacks' : [st_cb]
                    # }
                    # response = generate_response("嘿嘿嘿", chat, msgs)
                    response = chat.invoke(messages)
                    # msgs.add_ai_message(response["content"])
                    st.write(response.content)
    except Exception as ex:

        print(str(ex))
        exception_traceback = traceback.format_exc()
        print(exception_traceback)
        return '请重说'


def generate_response(user_input, chat, msgs, system):
    # 构建包含所有历史对话内容的 messages 列表

    messages = [
        SystemMessage(
            content=system),
    ]
    # 添加历史对话内容
    for msg in msgs.messages:
        if msg.type == "human":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    # 添加当前用户输入
    messages.append(HumanMessage(content=user_input))

    # 调用 chat.invoke 获取响应
    response = chat.invoke(messages)
    st.session_state['prompt_cache_hit_tokens'].append(response.response_metadata['token_usage']['prompt_cache_hit_tokens'])
    st.session_state['prompt_cache_miss_tokens'].append(response.response_metadata['token_usage']['prompt_cache_miss_tokens'])
    st.session_state['input_tokens'].append(response.usage_metadata['input_tokens'])
    st.session_state['output_tokens'].append(response.usage_metadata['output_tokens'])

    return response


if __name__ == '__main__':
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = ''
    if ('button_message' not in st.session_state):
        st.session_state['button_message'] = "开始说话"
        st.session_state['status'] = ""
    if ('text' not in st.session_state):
        st.session_state['text'] = ''
        st.session_state['reports'] = []
        st.session_state['input_tokens'] = []
        st.session_state['output_tokens'] = []
        st.session_state['prompt_cache_hit_tokens'] = []
        st.session_state['prompt_cache_miss_tokens'] = []

    main()
