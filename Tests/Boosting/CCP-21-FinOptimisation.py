import pandas as pd
import numpy as np
from mip import Model, MAXIMIZE, CBC, BINARY, OptimizationStatus, xsum

G_Mortgage = 200
G_Pension = 120
G_Savings = 100

channel_limits = {
    'email': 100,
    'sms': 100,
    'push': 500
}

preds = pd.read_csv("predictions.csv")

np.random.seed(42) 
channels = ['email', 'sms', 'push']
preds['channel'] = np.random.choice(channels, size=len(preds))

df = preds.copy()
df_long = df.melt(id_vars=["customer_id", "channel"], 
                  value_vars=["Mortgage", "Pension", "Savings"],
                  var_name="product", value_name="prob")

profit_map = {
    "Mortgage": G_Mortgage,
    "Pension": G_Pension,
    "Savings": G_Savings
}
df_long["score"] = df_long["prob"] * df_long["product"].map(profit_map)
df_long["client_id"] = df_long["customer_id"]
df_long.reset_index(drop=True, inplace=True)

def optimize(df: pd.DataFrame, channel_limits: dict) -> pd.DataFrame:
    model = Model(sense=MAXIMIZE, solver_name=CBC)
    
    x = [model.add_var(var_type=BINARY) for _ in range(df.shape[0])]
    df["x"] = x
    
    model.objective = xsum(df["score"][i] * x[i] for i in range(df.shape[0]))
    
    for channel in df["channel"].unique():
        indices = df[df["channel"] == channel].index
        model += xsum(x[i] for i in indices) <= channel_limits.get(channel, 0)
    
    for client_id, group in df.groupby("client_id").groups.items():
        model += xsum(x[i] for i in group) <= 1

    status = model.optimize(max_seconds=300)

    if status in [OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]:
        df["selected"] = [int(var.x) for var in model.vars]
        return df[df["selected"] == 1][["customer_id", "product"]].reset_index(drop=True)
    else:
        print("No feasible solution found")
        return pd.DataFrame()

result_df = optimize(df_long, channel_limits)

result_df.to_csv("final_offers.csv", index=False)