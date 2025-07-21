import re
from logic_templates import *

def route_query(query, df):
    q = query.lower()

    match = re.search(r"net sales in fy(\d{2}) for (\w+)", q)
    if match:
        fy = f"FY{match.group(1)}"
        store = match.group(2).upper()
        return get_metric_by_store_and_fy(df, "Net Sales", store, fy)

    if "top" in q and "ssg" in q:
        match = re.search(r"fy(\d{2})", q)
        if match:
            to_fy = f"FY{match.group(1)}"
            from_fy = f"FY{int(match.group(1)) - 1}"
            return top_ssg_stores(df, from_fy, to_fy)

    return None