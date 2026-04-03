

import time
import re


EMPLOYEES = [
    {"EMP_ID":"E001","FIRST_NM":"Ahmed", "LAST_NM":"Hassan",  "DEPT_ID":"D01","SALARY":85000, "LAND1":"EG"},
    {"EMP_ID":"E002","FIRST_NM":"Sara",  "LAST_NM":"Khalil",  "DEPT_ID":"D02","SALARY":92000, "LAND1":"EG"},
    {"EMP_ID":"E003","FIRST_NM":"Omar",  "LAST_NM":"Fawzi",   "DEPT_ID":"D01","SALARY":78000, "LAND1":"EG"},
    {"EMP_ID":"E004","FIRST_NM":"Nour",  "LAST_NM":"Saad",    "DEPT_ID":"D03","SALARY":110000,"LAND1":"EG"},
    {"EMP_ID":"E005","FIRST_NM":"Karim", "LAST_NM":"Muler",   "DEPT_ID":"D02","SALARY":95000, "LAND1":"AE"},
    {"EMP_ID":"E006","FIRST_NM":"Layla", "LAST_NM":"Mueller", "DEPT_ID":"D01","SALARY":88000, "LAND1":"AE"},
    {"EMP_ID":"E007","FIRST_NM":"Yusuf", "LAST_NM":"Müller",  "DEPT_ID":"D03","SALARY":102000,"LAND1":"LB"},
]



def demo_row_vs_column_store():
    print("\n" + "═"*55)
    print("CONCEPT 1: Row Store vs Column Store")
    print("═"*55)

    print("\n  [ROW STORE] Data layout in memory:")
    print("  (traditional DB — each row stored together)")
    for emp in EMPLOYEES:
        
        print(f"    [{emp['EMP_ID']} | {emp['FIRST_NM']:<6} | "
              f"{emp['LAST_NM']:<8} | {emp['DEPT_ID']} | "
              f"{emp['SALARY']}]  ← entire row loaded")

    print("\n  [COLUMN STORE] Data layout in HANA memory:")
    print("  (each column stored separately — much faster for analytics)")

    emp_ids  = [e["EMP_ID"]  for e in EMPLOYEES]
    salaries = [e["SALARY"]  for e in EMPLOYEES]
    depts    = [e["DEPT_ID"] for e in EMPLOYEES]

    print(f"    EMP_ID column:  {emp_ids}")
    print(f"    SALARY column:  {salaries}")
    print(f"    DEPT_ID column: {depts}")

    print(f"\n  To SUM salaries → HANA reads ONLY salary column:")
    print(f"    Total = {sum(salaries):,}  ← no names/depts loaded at all")
    print(f"\n  This is why HANA analytics are 100-1000x faster.")



class OpenSQL:
 

    def __init__(self, data):
   
        self.data = data

    def select_all(self, where=None):
     
        result = self.data.copy()
        if where:
            for field, value in where.items():
                result = [r for r in result if r.get(field) == value]

       
        sy_subrc = 0 if result else 4
        return result, sy_subrc

    def select_single(self, where):
     
        rows, _ = self.select_all(where=where)
        sy_subrc = 0 if rows else 4
        return (rows[0] if rows else None), sy_subrc

    def aggregate(self, group_by_field, agg_field, functions):
       
        groups = {}
        for row in self.data:
            key = row[group_by_field]
            if key not in groups:
                groups[key] = []
            groups[key].append(row[agg_field])

        result = []
        for key, values in groups.items():
            row = {group_by_field: key}
            if "COUNT" in functions:
                row["COUNT"] = len(values)
            if "AVG" in functions:
                row["AVG"] = sum(values) / len(values)
            if "MAX" in functions:
                row["MAX"] = max(values)
            if "SUM" in functions:
                row["SUM"] = sum(values)
            result.append(row)

        return sorted(result, key=lambda r: r[group_by_field])


class NativeSQL_HANA:


    def fuzzy_search(self, data, field, search_term, threshold=0.7):
     

        def similarity(s1, s2):
            s1_clean = s1.lower().replace('ü','u').replace('ö','o')
            s2_clean = s2.lower().replace('ü','u').replace('ö','o')

            matches = sum(1 for a, b in zip(s1_clean, s2_clean) if a == b)
            max_len = max(len(s1_clean), len(s2_clean))
            return matches / max_len if max_len > 0 else 0

        results = []
        for row in data:
            score = similarity(row[field], search_term)
            if score >= threshold:
                results.append({**row, "_FUZZY_SCORE": round(score, 2)})

        return sorted(results, key=lambda r: r["_FUZZY_SCORE"], reverse=True)



def run_open_sql_demos():
    db = OpenSQL(EMPLOYEES)

    print("\n" + "═"*55)
    print("CONCEPT 2a: Open SQL — SELECT all with WHERE")
    print("═"*55)
   
    lt_result, sy_subrc = db.select_all(where={"DEPT_ID": "D01"})
    print(f"  sy-subrc = {sy_subrc} (0=found, 4=not found)")
    for r in lt_result:
        print(f"  {r['EMP_ID']} | {r['FIRST_NM']:<8} | ${r['SALARY']:,}")

    print("\n" + "═"*55)
    print("CONCEPT 2b: Open SQL — SELECT SINGLE")
    print("═"*55)

    ls_result, sy_subrc = db.select_single(where={"EMP_ID": "E003"})
    if sy_subrc == 0:
        print(f"  Found: {ls_result['EMP_ID']} | "
              f"{ls_result['FIRST_NM']} {ls_result['LAST_NM']}")
    else:
        print("  Not found — sy-subrc = 4")

    print("\n" + "═"*55)
    print("CONCEPT 2c: Open SQL — GROUP BY + Aggregates")
    print("═"*55)
  
    stats = db.aggregate("DEPT_ID", "SALARY", ["COUNT","AVG","MAX","SUM"])
    print(f"  {'Dept':<6} {'Count':>6} {'Avg Salary':>12} "
          f"{'Max Salary':>12} {'Total':>12}")
    print(f"  {'-'*50}")
    for s in stats:
        print(f"  {s['DEPT_ID']:<6} {s['COUNT']:>6} "
              f"${s['AVG']:>11,.0f} "
              f"${s['MAX']:>11,} "
              f"${s['SUM']:>11,}")


def run_native_sql_demo():
    print("\n" + "═"*55)
    print("CONCEPT 3: Native SQL — HANA Fuzzy Search")
    print("═"*55)
    print("  Searching for 'Muller' with FUZZY(0.7)...")
    print("  (finds Mueller, Müller, Muler automatically)\n")

    hana = NativeSQL_HANA()

    results = hana.fuzzy_search(EMPLOYEES, "LAST_NM", "Muller", threshold=0.7)

    print(f"  {'EMP_ID':<8} {'Last Name':<12} {'Fuzzy Score':>12}")
    print(f"  {'-'*34}")
    for r in results:
        print(f"  {r['EMP_ID']:<8} {r['LAST_NM']:<12} "
              f"{r['_FUZZY_SCORE']:>12.2f}")
    print(f"\n  All 3 'Muller' variants found despite different spellings.")


if __name__ == "__main__":
    print("DAY 4 — SAP HANA & SQL SIMULATION")
    demo_row_vs_column_store()
    run_open_sql_demos()
    run_native_sql_demo()
    print("\n" + "═"*55)
    print("HANA = in-memory + column store = ultra-fast analytics.")
    print("Open SQL = safe + portable. Native SQL = HANA power.")
    print("═"*55)