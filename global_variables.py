SUMM1 = 'prod'
SUMM2 = 'palm'
SUMM3 = 'gemini'
summaries = [SUMM1, SUMM2, SUMM3]

Q = 5
THREADS = 30

PROMPT_COMPREHENSIBLE = """Here is a conversation between a Vodafone customer and an operator from the Vodafone customer service (a telecomunication company):
<conversation>
<TEXT>
</conversation>

The <conversation> is the output of a speech-recognition system and it may be inaccurate, however it should be possible to graps the content of the conversation.
I would like you to assess whether the conversation is still comprehensible.

Analyze the <conversation> and determine whether it is comprehensible, i.e. whether the customer's complaints and the assistance provided by the operator can be assessed.
Write out your <reasoning> as a string inside <reasoning> tag, then output the response by writing "Yes" if the conversation is understandable and "No" otherwise in the <comprehensible> tag.
Write your <reasoning> without including direct speech or quotation marks.

Output a valid JSON object as your final result.
The JSON must follow the following structure:
{
    "reasoning": <reasoning>,
    "comprehensible": "Yes/No"
}
"""

QUEST_PROMPT = """You are an expert in generating questions from a text.
You are given a <text> about a conversation between a customer from Vodafone (a telecommunication company) and a customer service representative of the company.
In the <text> the customer ("Cliente") is complaining about something and the operator ("Operatore") is providing assistance to them.

<text>
<TEXT>
</text>

Generate <Q> questions that can be answered only with "Yes" or "No" about the customer's request/complaint and the assistance provided by the operator.
Exclude questions containing specific prices, places and promotions' names.
Exclude also questions about the participation to customer satisfaction survey and about their personal data. 

Write each <question> in the appropriate tag under the key <questions>.
Output this full JSON object as your final result.
The JSON must follow the following structure:
{
    "questions": {
        "question_1": <question>,
        "question_2": <question>,
        ...
        "question_<Q>": <question>
    }
}
"""

ANSW_PROMPT = """You are an expert in answering questions based on a text.
You are given a <text> about a conversation between a Vodafone (a telecommunication company) customer and a customer service representative of the company.
In the <text> the customer ("Cliente") is complaining about something and the operator ("Operatore") is providing assistance to them.

<text>
<TEXT>
</text>

I want you to answer the following questions below based on the text provided.

<questions>
<QUESTIONS>
</questions>

Analyze the text and provide the <reply> and the <reasoning> as strings to each of the <questions>.
Your reasoning must be factual and based only on what is explicitly said in the conversation, without any further logical connections.
Write the answer in the <reply> tag and provide also your reasoning in the <reasoning> tag.
You are allowed to reply only using "Yes", "No", or "Unknown". Reply "Unknown" only when something is not mentioned in the <text>.

Output a valid JSON object as your final result.
The JSON must follow the following structure:
{
    "answers": {
        "answer_1": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>,
        }
        "answer_2": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>,
        },
        "answer_3": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>
        },
        ...
        "answer_<Q>": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>
        }
    }
}
"""

QA_PROMPT = """You are an expert in Question-Answering based on a text.
You are given a <text> about a conversation between a customer from Vodafone (a telecommunication company) and a customer service representative of the company.
In the <text> the customer ("Cliente") is complaining about something and the operator ("Operatore") is providing assistance to them.

<text>
<TEXT>
</text>

Analyze the <text> and generate <Q> questions that can be answered only with "Yes" or "No" about the customer's request/complaint and the assistance provided by the operator.
Write each question in the appropriate tag under the key "questions".
Exclude questions containing specific prices, places and promotions' names. Exclude also questions about the participation to customer satisfaction survey and about their personal data. 

Analyze the conversation again and provide the answer to each <question> in the appropriate <reply> tag under the key <answers>.
You are allowed to reply only using "Yes", "No", or "Unknown". Reply "Unknown" only when something is not mentioned in the <text>.
Your <reasoning> must be factual and based only on what is explicitly said in the conversation, without any further logical connections.
Write the answer in the <reply> tag and provide also your <reasoning> in the <reasoning> tag as strings.

Output a valid JSON object as your final result.
The JSON must follow the following structure:
{
    "questions": {
        "question_1": <question>,
        "question_2": <question>,
        ...
        "question_<Q>": <question>
    },
    "answers": {
        "answer_1": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>
        }
        "answer_2": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>
        },
        ...
        "answer_<Q>": {
            "reply": "Yes/No/Unknown",
            "reasoning": <reasoning>
        }
    }
}
"""