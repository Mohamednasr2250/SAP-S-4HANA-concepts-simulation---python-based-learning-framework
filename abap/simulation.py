

from dataclasses import dataclass, field
from typing import List, Optional


RAW_DB = {
    "kna1": [  
        {"kunnr": "c001", "name1": "ahmed trading",    "land1": "eg", "kunnr_group": "a"},
        {"kunnr": "c002", "name1": "Sara exports",     "land1": "eg", "kunnr_group": "b"},
        {"kunnr": "c003", "name1": "nile corp",        "land1": "eg", "kunnr_group": "a"},
        {"kunnr": "c004", "name1": "gulf traders",     "land1": "ae", "kunnr_group": "a"},
        {"kunnr": "c005", "name1": "beirut supplies",  "land1": "lb", "kunnr_group": "b"},
    ],
    "vbak": [  
        {"vbeln": "4500000001", "kunnr": "c001", "netwr": 125000, "waerk": "usd"},
        {"vbeln": "4500000002", "kunnr": "c001", "netwr":  87500, "waerk": "usd"},
        {"vbeln": "4500000003", "kunnr": "c002", "netwr":  45000, "waerk": "usd"},
        {"vbeln": "4500000004", "kunnr": "c003", "netwr": 200000, "waerk": "usd"},
        {"vbeln": "4500000005", "kunnr": "c004", "netwr":  33000, "waerk": "usd"},
    ],
}


def abap_select(fields, from_table, where=None, single=False, order_by=None):
  
    rows = RAW_DB.get(from_table, [])

    if where:
        for key, val in where.items():
            rows = [r for r in rows if r.get(key) == val]

    if order_by:
        rows = sorted(rows, key=lambda r: r.get(order_by, ""))

    if fields != "*":
        field_list = [f.strip() for f in fields.split(",")]
        rows = [{f: r[f] for f in field_list if f in r} for r in rows]

    sy_subrc = 0 if rows else 4

    if single:
        return rows[0] if rows else None, sy_subrc

    return rows, sy_subrc  


def abap_read_table(lt_table, key_field, key_value):

    result = next((r for r in lt_table if r.get(key_field) == key_value), None)
    sy_subrc = 0 if result else 4
    return result, sy_subrc


def abap_delete_where(lt_table, field, value):
    
    before = len(lt_table)
    lt_table = [r for r in lt_table if r.get(field) != value]
    print(f"  [delete where {field}={value}] removed {before - len(lt_table)} row(s)")
    return lt_table

##
def program_1_basic_loop():
    print("\n" + "═"*55)
    print("program 1: select all egyptian customers and loop at")
    print("═"*55)

  
    lt_customers, sy_subrc = abap_select(
        fields="kunnr, name1, land1",
        from_table="kna1",
        where={"land1": "eg"}
    )

    if sy_subrc == 0:
        print(f"  select done {len(lt_customers)} row(s) found.\n")
    else:
        print("  no data here sy-subrc = 4")
        return

  
    for ls_customer in lt_customers:        
        cust_id   = ls_customer["kunnr"]  
        cust_name = ls_customer["name1"]   
        country   = ls_customer["land1"]  
        print(f"  {cust_id} | {cust_name:<20} | {country}")


#

def program_2_select_single():
    print("\n" + "═"*55)
    print("PROGRAM 2: SELECT SINGLE — fetch one customer by ID")
    print("═"*55)

    target_id = "C002"

    ls_customer, sy_subrc = abap_select(
        fields="KUNNR, NAME1",
        from_table="KNA1",
        where={"KUNNR": target_id},
        single=True
    )

    if sy_subrc == 0:
        print(f"  Found: {ls_customer['KUNNR']} — {ls_customer['NAME1']}")
    else:
        print(f"  Customer {target_id} not found. sy-subrc = 4")


def program_3_append():
    print("\n" + "═"*55)
    print("PROGRAM 3: Build internal table with APPEND")
    print("═"*55)

   
    lt_report = []   
    ls_report = {}   

    lt_customers, _ = abap_select("*", "KNA1", where={"LAND1": "EG"})
    lt_orders, _    = abap_select("*", "VBAK")

    for ls_customer in lt_customers:

        cust_orders = [o for o in lt_orders
                       if o["KUNNR"] == ls_customer["KUNNR"]]

        total = sum(o["NETWR"] for o in cust_orders)

        ls_report = {
            "KUNNR":       ls_customer["KUNNR"],
            "NAME1":       ls_customer["NAME1"],
            "ORDER_COUNT": len(cust_orders),
            "TOTAL_VALUE": total,
        }

        lt_report.append(ls_report)

    lt_report.sort(key=lambda r: r["TOTAL_VALUE"], reverse=True)

    print(f"  {'Customer':<8} {'Name':<22} {'Orders':>6} {'Total Value':>12}")
    print(f"  {'-'*52}")
    for row in lt_report:
        print(f"  {row['KUNNR']:<8} {row['NAME1']:<22} "
              f"{row['ORDER_COUNT']:>6} ${row['TOTAL_VALUE']:>11,.0f}")


def program_4_read_table():
    print("\n" + "═"*55)
    print("PROGRAM 4: READ TABLE WITH KEY")
    print("═"*55)

    lt_customers, _ = abap_select("*", "KNA1")

   
    ls_customer, sy_subrc = abap_read_table(lt_customers, "KUNNR", "C003")

    if sy_subrc == 0:
        print(f"  READ TABLE succeeded:")
        print(f"  → {ls_customer['KUNNR']} | {ls_customer['NAME1']}")
    else:
        print("  Not found in internal table.")

    ls_missing, sy_subrc2 = abap_read_table(lt_customers, "KUNNR", "C999")
    if sy_subrc2 != 0:
        print(f"\n  READ TABLE for C999: not found, sy-subrc = {sy_subrc2}")



def program_5_delete():
    print("\n" + "═"*55)
    print("PROGRAM 5: DELETE lt_table WHERE condition")
    print("═"*55)

    lt_customers, _ = abap_select("*", "KNA1")
    print(f"  Before delete: {len(lt_customers)} customers")

    lt_customers = abap_delete_where(lt_customers, "LAND1", "AE")

    print(f"  After delete:  {len(lt_customers)} customers")
    for r in lt_customers:
        print(f"  → {r['KUNNR']} | {r['NAME1']} | {r['LAND1']}")

if __name__ == "__main__":
    print("DAY 2 — ABAP INTERNAL TABLES SIMULATION")
    program_1_basic_loop()
    program_2_select_single()
    program_3_append()
    program_4_read_table()
    program_5_delete()
    print("\n" + "═"*55)
    print("All programs complete. You now understand ABAP's")
    print("core data pattern: SELECT → LOOP → Process → Output")
    print("═"*55)
    #