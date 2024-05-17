import os
from dotenv import load_dotenv
load_dotenv()

import requests
from uuid import uuid4 as uuid

class BaseClovaInterface:
    def __init__(self):
        self._api_url = os.getenv("CLOVA_API_URL")
        self._api_key = os.getenv("CLOVA_API_KEY")
        self._api_key_primary_val = os.getenv("API_GATEWAY_KEY")
    
        self._service_api_key = os.getenv("SERVICE_API_KEY")
        self._embedding_api_url = os.getenv("EMBEDDING_API_URL")
        self._chunking_api_url = os.getenv("CHUNKING_API_URL")
        self._calc_api_url = os.getenv("CALC_API_URL")
        self._summary_api_url = os.getenv("SUMMARY_API_URL")

    def input_prompts(self, system_prompt: str, user_prompt: str) -> list:
        return [
            {
                "role":"system",
                "content": system_prompt
            },
            {
                "role":"user",
                "content": user_prompt
            }
        ]

    def execute(self, messages, temperature=0.4, maxTokens=1024):
        request_data = {
            'messages': messages,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': maxTokens,
            'temperature': temperature,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True
        }

        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        resp = []
        with requests.post(self._api_url, headers=headers,
                           json=request_data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    resp.append(line.decode("utf-8"))
        try:
            return eval(resp[-4][5:])['message']['content']
        except:
            print(resp)
            return "Something went wrong!"

    def execute_stream(self, messages, temperature=0.4, maxTokens=1024):
        request_data = {
            'messages': messages,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': maxTokens,
            'temperature': temperature,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True
        }

        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        resp_iter=requests.post(self._api_url, headers=headers,json=request_data, stream=True).iter_lines()
        class StreamIterator:
            def __iter__(self):
                self._r = resp_iter
                self._event_token = False
                return self
            def __next__(self):
                resp_string = ""
                line = next(self._r)
                if line:
                    decoded_string = line.decode("utf-8")
                    if decoded_string=="event:token":
                        self._event_token = True
                    elif decoded_string[:4]=="data":
                        if self._event_token == True:
                            self._event_token = False
                            resp_string = eval(decoded_string.replace("null","None")[5:])['message']['content']
                return resp_string
        iterator = StreamIterator()
        return iterator


    def embed_text(self, text: str):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._service_api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
        }

        response = requests.post(
            self._embedding_api_url,
            headers=headers,
            json={'text': text})
        res = eval(response.text.replace("null","None"))
        if res['status']['code'] == '20000':
            return res['result']
        else:
            return 'Error'
    
    def chunk_text(self, text: str):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._service_api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
        }
        response = requests.post(
            self._chunking_api_url,
            headers=headers,
            json={
                "text" : text,
                "alpha" : -100,
                "segCnt" : -1,
                "postProcess" : True,
                "postProcessMaxSize" : 2000,
                "postProcessMinSize" : 100
            }
        )
        return eval(response.text.replace("null","None"))
        
        

    def calc_token(self, messages: list):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._service_api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
        }
        response = requests.post(
            self._calc_api_url,
            headers=headers,
            json={"messages":messages}
        )
        res = eval(response.text.replace("null","None"))
        if res['status']['code'] == '20000':
            return res['result']['messages']
        else:
            return "Error"
        
    def summarize_texts(self, sentences: list, useAutoSentenceSplitter=True):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._service_api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid()),
        }
        response = requests.post(
            self._summary_api_url,
            headers=headers,
            json={
                "texts" : sentences, # within 35000 characters (incl. spaces)
                "includeAiFilters" : False,
                "autoSentenceSplitter" : useAutoSentenceSplitter,
                "segCount" : -1,
                "segMinSize" : 300,
                "segMaxSize" : 1000
            }
        )
        res = eval(response.text.replace("null","None"))
        if res['status']['code'] == '20000':
            return res['result']
        else:
            return "Error"