import pandas as pd
from optimizer import optimize
import joblib

unknown_data = pd.read_csv('source/Data/unknown_behaviors.csv')

model_mortgage = joblib.load('source/Tests/Boosting/calibrated_models/mortgage_model.pkl')
calibrator_mortgage = joblib.load('source/Tests/Boosting/calibrated_models/mortgage_platt.pkl')

model_pension = joblib.load('source/Tests/Boosting/calibrated_models/pension_model.pkl')
calibrator_pension = joblib.load('source/Tests/Boosting/calibrated_models/pension_platt.pkl')

model_savings = joblib.load('source/Tests/Boosting/calibrated_models/savings_model.pkl')
calibrator_savings = joblib.load('source/Tests/Boosting/calibrated_models/savings_platt.pkl')

mortgage_scores = calibrator_mortgage.predict_proba(unknown_data.drop(columns=['customer_id']))[:, 1]
pension_scores = calibrator_pension.predict_proba(unknown_data.drop(columns=['customer_id']))[:, 1]
savings_scores = calibrator_savings.predict_proba(unknown_data.drop(columns=['customer_id']))[:, 1]

final_rows = []
for client_id, mortgage_score, pension_score, savings_score in zip(unknown_data['customer_id'], mortgage_scores, pension_scores, savings_scores):
    for product in ['mortgage', 'pension', 'savings']:
        for channel in ['sms', 'calls', 'emails']:
            final_rows.append({
                'client_id': client_id,
                'product': product,
                'channel': channel,
                'score': mortgage_score if product == 'mortgage' else pension_score if product == 'pension' else savings_score
            })

df = pd.DataFrame(final_rows)

optimization_params = {
    'ltv_mortgage': 30000,
    'ltv_pension': 24000,
    'ltv_savings': 3500,
    'max_sms': 5000,
    'max_calls': 750000,
    'max_emails': 2000,
    'sms_cost': 0.7,
    'call_cost': 2.9,
    'email_cost': 0.004
}

optimal_decisions = optimize(df, optimization_params)
df['selected'] = optimal_decisions

selected_clients = df[df['selected'] == 1][['client_id', 'product', 'channel', 'score']]
selected_clients.to_csv('source/Data/selected_clients.csv', index=False)

print(f"Сохранено {len(selected_clients)} записей в selected_clients.csv")