import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import numpy as np
import pandas as pd

import joblib
import lightgbm
import sklearn

from optimizer import optimize, random_mailing
from processor import prepare_data, products


models = ["Model 1", "Model 2", "Model 3"]

def VeronicaAsAFunction(data):
    df = prepare_data()

    if data['random_mailing']:
        df['optimal_decision'] = random_mailing(df, data)
    else:
        optimal_decision = optimize(df, data)
        df['optimal_decision'] = optimal_decision

    optimization_results = df[df['optimal_decision']==1].groupby(['channel', 'product']).\
                                        agg({'client_id': 'count'}).\
                                        rename(columns={'client_id': 'client_cnt'})
    optimization_results = optimization_results.reset_index()
    
    # считаем выручку
    profit_calculation = optimization_results.copy()
    profit_calculation['product_ltv'] = profit_calculation['product'].map({
        'mortgage': data['ltv_mortgage'],
        'pension': data['ltv_pension'],
        'savings': data['ltv_savings']
    })
    profit_calculation['channel_cost'] = profit_calculation['channel'].map({
        'sms': data['sms_cost'],
        'call': data['call_cost'],
        'email': data['email_cost']
    })

    revenue = (profit_calculation['product_ltv'] * profit_calculation['client_cnt']).sum()
    cost = (profit_calculation['channel_cost'] * profit_calculation['client_cnt']).sum()
    max_profit = revenue - cost

    # количество клиентов для рассылок
    num_clients = optimization_results['client_cnt'].sum()

    # склонности 
    total_by_product = optimization_results.groupby('product')['client_cnt'].sum()
    propensity = {product: 0.0 for product in products}
    for product in total_by_product.index:
        propensity[product] = total_by_product[product] / num_clients if num_clients > 0 else 0

    mortgage_propensity = propensity['mortgage']
    pension_propensity = propensity['pension']
    savings_propensity = propensity['savings']

    channels_names = ['SMS', 'Emails', 'Calls']

    channel_colors = {
        'sms': (96/255, 180/255, 255/255),
        'emails': (255/255, 189/255, 69/255),
        'calls': (61/255, 213/255, 109/255)
    }

    sns.set_style('whitegrid')
    plt.figure(figsize=(16, 6), facecolor='white')

    for i, channel in enumerate(channels_names, 1):
        ax = plt.subplot(1, len(channels_names), i)

        sns.histplot(
            data=df[df['channel'] == channel.lower()],
            x='score',
            bins=20,
            color=channel_colors[channel.lower()],
            edgecolor='white',
            alpha=0.9,
            ax=ax
        )

        ax.set_title(f'{channel}', fontsize=22, fontweight='bold', color=channel_colors[channel.lower()])
        ax.set_xlabel('Score', fontsize=16, color='#333333', fontweight='bold')
        ax.set_ylabel('', fontsize=10, color='#333333', fontweight='bold')

        ax.tick_params(axis='both', colors='#555555', labelsize=14)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
        ax.set_facecolor('#f9f9f9')
        ax.grid(True, alpha=0.3)

        for spine in ax.spines.values():
            spine.set_color('#cccccc')

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    return {
        'max_profit': max_profit,
        'num_clients': num_clients,
        'mortgage_propensity': mortgage_propensity,
        'pension_propensity': pension_propensity,
        'savings_propensity': savings_propensity,
        'scores_distribution': plt
        }