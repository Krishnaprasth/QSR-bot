
def format_month(month_str):
    # Convert '21-Apr' to 'Apr-2021'
    if "-" in month_str:
        parts = month_str.split("-")
        return f"{parts[1]}-20{parts[0]}"
    return month_str
