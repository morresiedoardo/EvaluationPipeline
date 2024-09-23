### Import libraries

from time import sleep
import concurrent.futures
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
tqdm.pandas()

import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.generative_models import GenerativeModel
from vertexai import generative_models
from google.api_core import exceptions as google_exceptions
class EmptyResponseException(Exception):    pass
class GenericResponseException(Exception):    pass

from typing_extensions import Any, Self, TypedDict
  
class ModelParameters(TypedDict):
    max_output_tokens: int
    temperature: float
    top_k: int
    top_p: float
    
class ModelConfig(TypedDict):
    name: str
    prompt_placeholder: str
    max_retry: int
    sleep_time_generic: int
    sleep_time_rate_limit: int
    model_parameters: ModelParameters


### Variables
THREADS = 30
Q = 5


### Config

model_config = ModelConfig()

model_config["model_parameters"] = {
    "temperature": 0,
    "max_output_tokens": 2048,
    "top_p": 1,
    "top_k": 40,
}

model_config["max_retry"] = 5
model_config["sleep_time_generic"] = 5
model_config["sleep_time_rate_limit"] = 60


### PALM

model_palm = TextGenerationModel.from_pretrained("text-bison@002")

def palm_call(
        prompt: str,
        model: TextGenerationModel,
        model_config: ModelConfig,
    ) -> str:
    
    retry = 0
    max_retry = model_config["max_retry"]
    sleep_time_rate_limit = model_config["sleep_time_rate_limit"]
    sleep_time_generic = model_config["sleep_time_generic"]

    model_parameters = model_config["model_parameters"]

    while True:
        retry += 1
        try:
            result = model.predict(prompt, **model_parameters).text
            if result:
                return result
            if retry >= max_retry:
                return ""
            sleep(sleep_time_generic)
        except google_exceptions.ResourceExhausted as e:  # 429
            if retry >= max_retry:
                raise GenericResponseException(f"Max retry limit reached | {e!s}") from e
            sleep(sleep_time_rate_limit)
        except (
            google_exceptions.InternalServerError,  # 500
            google_exceptions.ServiceUnavailable,  # 503
        ) as e:
            if retry >= max_retry:
                raise GenericResponseException(f"Service offline | {e!s}") from e
            sleep(sleep_time_generic)
        except google_exceptions.BadRequest:  # 400
            return "PALM TOKEN LIMIT"
        
def palm_call_mt(
        df,
        column_text,
        column_questions,
        column_output,
        prompt,
        model,
        model_config,
        goal,
        threads=THREADS
    ):
    
    def format_prompt(prompt, goal, row):
        global Q
        if goal=='comprehensible':
            prompt = prompt.replace("<TEXT>", row[column_text])
        if goal in ('generate_questions', 'generate_questions_and_answers'):
            prompt = prompt.replace("<TEXT>", row[column_text]).replace("<Q>", str(Q))
        if goal=='generate_answers':
            prompt = prompt.replace("<TEXT>", row[column_text]).replace("<QUESTIONS>", str(row[column_questions])).replace("<Q>", str(Q))
        return prompt
    
    def parallelized_palm_call(df):
        df[column_output] = df.apply(lambda row: palm_call(format_prompt(prompt, goal, row),
                                                           model=model_palm, model_config=model_config),
                                     axis=1)
        return df
    
    df_parallelized = np.array_split(df, threads)
    print(f"\nDataset splitted in {threads} chunks of ~{len(df_parallelized[0])} rows each\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
        results = tqdm(executor.map(parallelized_palm_call, df_parallelized), total=THREADS)
        executor.shutdown(wait = True)

    df_enriched = [result for result in results]
    df_enriched = pd.concat(df_enriched)
    
    return df_enriched


### GEMINI

TEMPERATURE = 0
MAX_TOKENS = 2048
model_parameters = {
    "temperature": TEMPERATURE,
    "top_p": 1,
    "max_output_tokens": MAX_TOKENS,   
}

model_gemini = GenerativeModel(
    "gemini-1.5-pro-001",
)

safety_config = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

def gemini_call(
        prompt,
        model=model_gemini,
        model_parameters=model_parameters
    ) -> str:
    
    global model_dict_conf
    retry = 0
    result = ""
    MAX_RETRY = 10
    SLEEP_TIME_RATELIMIT = 60
    SLEEP_TIME_GENERIC = 1
    TEMPERATURE = 0.00
    MAX_TOKENS = 1024
    model_parameters = {
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_TOKENS,   
    }
    
    while True:
        retry += 1
        try:
            response = model_gemini.generate_content(prompt,
                                                     safety_settings=safety_config,
                                                     generation_config=model_parameters)
            try:
                result = response.text.strip()
            except Exception as e:
                print(e)
                return result
            if result == "" or result is None:
                raise EmptyResponseException("Empty response")
            else:
                return result  
        except EmptyResponseException as e:
            if retry >= MAX_RETRY:
                result = ""
                return result
            sleep(SLEEP_TIME_GENERIC)
        except google_exceptions.ResourceExhausted as e: #429
            if retry >= MAX_RETRY:
                raise GenericResponseException(f"Max retry limit reached | {str(e)}") from e
            sleep(SLEEP_TIME_RATELIMIT)
        except (
            google_exceptions.InternalServerError,  # 500
            google_exceptions.ServiceUnavailable,  # 503
        )as e:
            if retry >= MAX_RETRY:
                raise GenericResponseException(f"Service offline | {str(e)}") from e
            sleep(SLEEP_TIME_GENERIC)
        except google_exceptions.BadRequest as e:  # 400
            result = "GEMINI TOKEN LIMIT"
            return result
        
def gemini_call_mt(
        df,
        column_text,
        column_questions,
        column_output,
        prompt,
        model,
        model_config,
        goal,
        threads=THREADS
    ):
    
    def format_prompt(prompt, goal, row):
        global Q
        if goal=='comprehensible':
            prompt = prompt.replace("<TEXT>", row[column_text])
        if goal in ('generate_questions', 'generate_questions_and_answers'):
            prompt = prompt.replace("<TEXT>", row[column_text]).replace("<Q>", str(Q))
        if goal=='generate_answers':
            prompt = prompt.replace("<TEXT>", row[column_text]).replace("<QUESTIONS>", str(row[column_questions])).replace("<Q>", str(Q))
        return prompt
    
    def parallelized_gemini_call(df):
        df[column_output] = df.apply(lambda row: gemini_call(format_prompt(prompt, goal, row),
                                                             model=model_gemini, model_parameters=model_parameters),
                                     axis=1)
        return df
    
    df_parallelized = np.array_split(df, threads)
    print(f"\nDataset splitted in {threads} chunks of ~{len(df_parallelized[0])} rows each\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
        results = tqdm(executor.map(parallelized_gemini_call, df_parallelized,), total=THREADS)
        executor.shutdown(wait = True)
    
    df_enriched = []
    for result in results:
        df_enriched.append(result)
    df_enriched = pd.concat(df_enriched)
    
    return df_enriched