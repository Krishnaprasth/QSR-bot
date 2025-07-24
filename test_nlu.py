from nlp_pipeline import predict

tests = [
    "Which store had max Net Sales in 2021-Apr?",
    "Overall SSG in FY25",
    "Rank stores by Rent in 2022-Dec descending",
    "Trend of Outlet EBITDA for HSR",
    "Compare COGS vs Rent for KOR in Mar 2025"
]

for q in tests:
    intent, slots = predict(q)
    print(f"Q: {q}")
    print(f"→ Intent: {intent}")
    print(f"→ Slots: {slots}\n")