import pandas as pd
import joblib

products = ['mortgage', 'pension', 'savings']
channels = ['sms', 'calls', 'emails']
channel_limits = {
    'sms': 'sms',
    'calls': 'calls',
    'emails': 'emails'
}

def load_models():
    return {
        'mortgage': {
            'model': joblib.load('Tests/Boosting/calibrated_models/mortgage_model.pkl'),
            'calibrator': joblib.load('Tests/Boosting/calibrated_models/mortgage_platt.pkl')
        },
        'pension': {
            'model': joblib.load('Tests/Boosting/calibrated_models/pension_model.pkl'),
            'calibrator': joblib.load('Tests/Boosting/calibrated_models/pension_platt.pkl')
        },
        'savings': {
            'model': joblib.load('Tests/Boosting/calibrated_models/savings_model.pkl'),
            'calibrator': joblib.load('Tests/Boosting/calibrated_models/savings_platt.pkl')
        }
    }

def prepare_data(data_path='Data/unknown_behaviors.csv'):
    """Подготавливает данные для анализа с учетом каналов коммуникации"""
    unknown_data = pd.read_csv(data_path)
    customer_id = unknown_data['customer_id']
    X = unknown_data.drop(columns=['customer_id'])
    
    models = load_models()
    
    base_scores = {
        'mortgage': models['mortgage']['calibrator'].predict_proba(X)[:, 1],
        'pension': models['pension']['calibrator'].predict_proba(X)[:, 1],
        'savings': models['savings']['calibrator'].predict_proba(X)[:, 1]
    }
    
    # корректировка скоров (пока что так, потом мб что-то более умное)
    channel_effectiveness = {
        'mortgage': {'sms': 0.9, 'calls': 1.2, 'emails': 1.0},
        'pension': {'sms': 0.8, 'calls': 1.1, 'emails': 1.3},
        'savings': {'sms': 1.0, 'calls': 0.9, 'emails': 1.1}
    }
    
    final_rows = []
    for i, client_id in enumerate(customer_id):
        for product in products:
            base_score = base_scores[product][i]
            for channel in channels:
                channel_score = base_score * channel_effectiveness[product][channel]
                channel_score = max(0, min(1, channel_score))
                
                final_rows.append({
                    'client_id': client_id,
                    'product': product,
                    'channel': channel,
                    'score': channel_score,
                    'base_score': base_score
                })
    
    return pd.DataFrame(final_rows)