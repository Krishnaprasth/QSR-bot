import pandas as pd
import numpy as np

stores = ['KOR','HSR','ITPL']
months = ['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']
metrics = ["Net Sales", "Rent", "Labor Cost", "CAM", "Utility Cost", "Aggregator commission", "Marketing & advertisement", "GST"]

rows = []
for fy in ['FY 2023-24','FY 2024-25']:
    for store in stores:
        for month in months:
            for metric in metrics:
                if metric == "Net Sales":
                    amount = np.random.randint(50,500)
                elif metric == "GST":
                    amount = np.random.randint(5,25)
                else:
                    amount = np.random.randint(5,50)
                rows.append([store, fy, month, metric, amount])
df = pd.DataFrame(rows, columns=['Store','FY','Month','Metric','Amount'])
df.to_csv('sales_data.csv', index=False)
print("Generated sample sales_data.csv")