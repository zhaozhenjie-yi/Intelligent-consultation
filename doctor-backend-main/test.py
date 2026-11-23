from local_config import env
import openai

openai.api_base = "https://gateway.ai.cloudflare.com/v1/f2580bfc5d6902b6fc8a063d69d049ef/open-ai/openai"
openai.api_key = env("MODEL_API_KEY_1")
model = "gpt-4-1106-preview"

query = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Who are you? Are you frm China22?"}]

response = openai.ChatCompletion.create(model=model, messages=query, temperature=0.5)

gpt_message = response["choices"][0]["message"]
print(gpt_message)
