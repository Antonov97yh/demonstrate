import random
import pandas as pd
from mip import Model, MAXIMIZE, CBC, BINARY, OptimizationStatus, xsum


channel_limits = {
    'sms': 'sms',
    'calls': 'calls',
    'emails': 'emails'
}


def optimize(frame: pd.DataFrame, limits_and_profit: dict) -> list:
    """
    Возвращает массив оптимальных предложений для максимизации прибыли.
    
    :param frame: DataFrame с информацией о клиентах, продуктах и каналах связи.
    :param limits_and_profit: Словарь с ограничениями на количество коммуникаций и ltv каждого продукта.
    :return: Список оптимальных предложений (бинарных переменных).
    """
    
    df = frame.copy()

    ltv_mortgage = limits_and_profit["ltv_mortgage"]
    ltv_pension = limits_and_profit["ltv_pension"]
    ltv_savings = limits_and_profit["ltv_savings"]
    
    model = Model(sense=MAXIMIZE, solver_name=CBC)
    model.verbose = 0
    
    x = [model.add_var(var_type=BINARY) for _ in range(df.shape[0])]
    df['x'] = x

    df['profit'] = 0
    df.loc[df['product'] == 'mortgage', 'profit'] = ltv_mortgage
    df.loc[df['product'] == 'pension', 'profit'] = ltv_pension
    df.loc[df['product'] == 'savings', 'profit'] = ltv_savings

    model.objective = xsum(df['profit'] * df['score'] * df['x'])

    for channel in df['channel'].unique():
        model += (xsum(df[df['channel'] == channel]['x']) <= limits_and_profit[f'max_{channel_limits[channel]}'])

    for client_id in df['client_id'].unique():
        product_cnt = xsum(df[(df['client_id'] == client_id)]['x'])
        model += (product_cnt <= 1)

    status = model.optimize(max_seconds=300)
    
    del df
    
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        return [var.x for var in model.vars]
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print('No feasible solution found')
        return []


def random_mailing(frame: pd.DataFrame, limits: dict) -> list:
    """
    Генерирует случайные решения для рассылки с учетом ограничений
    
    :param frame: DataFrame с информацией о клиентах, продуктах и каналах связи
    :param limits: Словарь с ограничениями на количество коммуникаций
    :return: Список решений (1 - отправлять, 0 - не отправлять)
    """
    df = frame.copy()
    random_decision = []
    client_offers = {}
    channel_counts = {
        'sms': 0,
        'calls': 0,
        'emails': 0
    }
    
    shuffled_df = df.sample(frac=1).reset_index(drop=True)
    
    for idx, row in shuffled_df.iterrows():
        client_id = row['client_id']
        channel = row['channel']
        
        if (client_id in client_offers) or (channel_counts[channel] >= limits[f'max_{channel_limits[channel]}']):
            random_decision.append(0)
        else:
            if random.random() < 0.5:
                random_decision.append(1)
                client_offers[client_id] = True
                channel_counts[channel] += 1
            else:
                random_decision.append(0)
    
    while len(random_decision) < len(df):
        random_decision.append(0)
        
    return random_decision[:len(df)]