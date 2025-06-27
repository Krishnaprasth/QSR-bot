
def simulate_scenario(df, cost_head, cap_value):
    df_sim = df.copy()
    affected = df_sim['Metric'] == cost_head
    df_sim.loc[affected, 'Amount'] = df_sim.loc[affected, 'Amount'].clip(upper=cap_value)
    return df_sim
