import re
import json

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")
sns.set(font_scale=1.5)

from global_variables import *

def clean_up_response(x):
    clean_response = re.sub(r"\n|```json|```|\}\.", "", x)
    clean_response = re.sub(r"\,\s*\}", "}", clean_response)
    clean_response = clean_response.replace("JSON","").replace('\n', '')
    return clean_response


def extract_json(
        x,
        REGEX_PATTERN = "((\[[^\}]{1,})?\{s*[^\}\{]{1,}?:.*\}([^\{]+\])?)"
        ):
    
    x = clean_up_response(x)
    # x = re.search(REGEX_PATTERN, x)[0]
    # if isinstance(x, tuple): ### IN CASE OF MULTIPLE MATCHES
    #     x = x[0]
    try:
        x = json.loads(x)
    except:
        try:
            x = eval(x)
        except:
            x = "ERROR"
    return x


def compute_hallucination_score(
        row,
        model,
        against,
        V=1
        ):
    
    score = 0
    
    for i in range(Q):
    
        if V==1:
            if 'Unknown' in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply'] and 'Unknown' not in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply']:
                score += 1
            if 'Unknown' in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply'] and 'Unknown' not in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply']:
                score += 1
    
        else:
            if 'Unknown' in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply']:
                score += 1
            if 'Unknown' in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply']:
                score += 1
    
    return score


def compute_contradiction_score(
        row,
        model,
        against
        ):
    
    score = 0
    
    for i in range(Q):
        if 'Yes' in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply'] and 'No' in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply']:
            score += 1
        if 'No' in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply']:
            score += 1
        if 'Yes' in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply'] and 'No' in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply']:
            score += 1
        if 'No' in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply']:
            score += 1
    
    return score


def compute_noninformativeness_score(
        row,
        model,
        against,
        V=1
        ):
    
    score = 0
    
    for i in range(Q):
        
        if V==1:
            if 'Unknown' in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply'] and 'Unknown' not in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply']:
                score += 1
            if 'Unknown' in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply'] and 'Unknown' not in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply']:
                score += 1
        
        else:
            if 'Unknown' in row[f'{model}_answ_{against}_from_conv'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_conv_from_conv'][f'answer_{i+1}']['reply']:
                score += 1
            if 'Unknown' in row[f'{model}_answ_{against}_from_{against}'][f'answer_{i+1}']['reply'] and 'Yes' in row[f'{model}_answ_conv_from_{against}'][f'answer_{i+1}']['reply']:
                score += 1
    
    return score


def plot_score_distributions(
        df,
        model,
        V=1
        ):

    score_names = ['hall', 'contr', 'noninfo']

    for i in range(3):

        plt.figure(figsize=(12, 8))
        plt.subplot(3, 1, i+1)

        scores = df[
            [f'{model}_{score_names[i]}_scr_{S}_{V}' for S in summaries]
                    ].melt(var_name='Model', value_name='Score').groupby(['Model', 'Score']).size().reset_index(name='Frequency')

        ax = sns.barplot(data=scores, x='Score', y='Frequency', hue='Model')
        plt.title(f'Frequency of {score_names[i].upper()} Scores for Each Model')
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.legend(title='Model')
        sns.move_legend(ax, "upper right")
        plt.show()