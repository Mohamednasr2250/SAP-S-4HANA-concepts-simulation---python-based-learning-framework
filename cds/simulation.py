

DB = {
    "ZEMPLOYEES": [
        {"EMP_ID": "E001", "FIRST_NM": "Ahmed",  "LAST_NM": "Hassan",
         "DEPT_ID": "D01", "SALARY": 85000, "HIRE_DATE": "20210315", "STATUS": "A"},
        {"EMP_ID": "E002", "FIRST_NM": "Sara",   "LAST_NM": "Khalil",
         "DEPT_ID": "D02", "SALARY": 92000, "HIRE_DATE": "20190801", "STATUS": "A"},
        {"EMP_ID": "E003", "FIRST_NM": "Omar",   "LAST_NM": "Fawzi",
         "DEPT_ID": "D01", "SALARY": 78000, "HIRE_DATE": "20220601", "STATUS": "A"},
        {"EMP_ID": "E004", "FIRST_NM": "Nour",   "LAST_NM": "Saad",
         "DEPT_ID": "D03", "SALARY": 110000,"HIRE_DATE": "20180201", "STATUS": "I"},
    ],
    "ZDEPARTMENTS": [
        {"DEPT_ID": "D01", "DEPT_NAME": "Finance",    "COST_CENTER": "CC-FIN-001"},
        {"DEPT_ID": "D02", "DEPT_NAME": "Sales",      "COST_CENTER": "CC-SLS-002"},
        {"DEPT_ID": "D03", "DEPT_NAME": "Technology", "COST_CENTER": "CC-TEC-003"},
    ],
    "ZLOCATIONS": [
        {"DEPT_ID": "D01", "CITY": "Cairo",  "FLOOR": "3rd"},
        {"DEPT_ID": "D02", "CITY": "Cairo",  "FLOOR": "5th"},
        {"DEPT_ID": "D03", "CITY": "Alex",   "FLOOR": "2nd"},
    ]
}



class Z_Emp_Basic:
 
    def select(self, where=None):
        rows = DB["ZEMPLOYEES"].copy()
        if where:
            for k, v in where.items():
                rows = [r for r in rows if r.get(k) == v]
        return rows


class Z_Dept_Basic:
 
    def select(self, where=None):
        rows = DB["ZDEPARTMENTS"].copy()
        if where:
            for k, v in where.items():
                rows = [r for r in rows if r.get(k) == v]
        return rows



class Z_Emp_Composite:
   
  
    def __init__(self):
        self._emp_view  = Z_Emp_Basic()
        self._dept_view = Z_Dept_Basic()

    def _resolve_association(self, dept_id):

        depts, _ = self._dept_view.select(where={"DEPT_ID": dept_id}), 0
        return depts[0] if depts[0] else None

    def _resolve_association(self, dept_id):
        results = [d for d in DB["ZDEPARTMENTS"] if d["DEPT_ID"] == dept_id]
        return results[0] if results else None

    def _status_text(self, status_code):
     
        mapping = {"A": "Active", "I": "Inactive", "T": "Terminated"}
        return mapping.get(status_code, "Unknown")

    def select(self, where=None, include_dept=False):
        employees = self._emp_view.select(where=where)
        result = []

        for emp in employees:
            row = {
                "EMP_ID":      emp["EMP_ID"],
                "FIRST_NM":    emp["FIRST_NM"],
                "LAST_NM":     emp["LAST_NM"],
                "FULL_NAME":   f"{emp['FIRST_NM']} {emp['LAST_NM']}",
                "DEPT_ID":     emp["DEPT_ID"],
                "SALARY":      emp["SALARY"],
                "HIRE_DATE":   emp["HIRE_DATE"],
                "STATUS_TEXT": self._status_text(emp["STATUS"]),
            }

            if include_dept:
                dept = self._resolve_association(emp["DEPT_ID"])
                if dept:
                    row["DEPT_NAME"]    = dept["DEPT_NAME"]
                    row["COST_CENTER"]  = dept["COST_CENTER"]

            result.append(row)

        return result



class Z_Emp_Consumption:
   
    ANNOTATIONS = {
        "@OData.publish": True,
        "@EndUserText.label": "Employee Overview",
        "@UI.lineItem": [
            {"position": 10, "label": "Employee ID"},
            {"position": 20, "label": "Full Name"},
            {"position": 30, "label": "Department"},
            {"position": 40, "label": "Status"},
            {"position": 50, "label": "Salary"},
        ],
        "@UI.selectionField": [
            {"position": 10, "element": "DEPT_ID"},
            {"position": 20, "element": "STATUS_TEXT"},
        ]
    }

    def __init__(self):
        self._composite = Z_Emp_Composite()

    def get_list(self, filters=None):
        """Simulates Fiori list view reading from OData"""
        return self._composite.select(where=filters, include_dept=True)

    def get_odata_endpoint(self):
        return "/sap/opu/odata/sap/Z_EMP_CONSUMPTION_SRV/EmployeeSet"



def run_layer1():
    print("\n" + "═"*55)
    print("LAYER 1: Basic View — raw table data")
    print("═"*55)
    view = Z_Emp_Basic()
    rows = view.select()
    for r in rows:
        print(f"  {r['EMP_ID']} | {r['FIRST_NM']:<8} {r['LAST_NM']:<10} | {r['DEPT_ID']}")


def run_layer2():
    print("\n" + "═"*55)
    print("LAYER 2: Composite View — joins + calculations")
    print("═"*55)
    view = Z_Emp_Composite()
    rows = view.select(include_dept=True)
    for r in rows:
        print(f"  {r['EMP_ID']} | {r['FULL_NAME']:<18} | "
              f"{r.get('DEPT_NAME','?'):<12} | {r['STATUS_TEXT']}")


def run_layer3_fiori():
    print("\n" + "═"*55)
    print("LAYER 3: Consumption View — what Fiori sees via OData")
    print("═"*55)
    view = Z_Emp_Consumption()

    print(f"  OData endpoint: {view.get_odata_endpoint()}")
    print(f"\n  Annotations active:")
    for k, v in view.ANNOTATIONS.items():
        print(f"    {k}: {v}")

    print(f"\n  Fiori List — Active employees only:")
    rows = view.get_list(filters={"STATUS": "A"})
    print(f"  {'ID':<6} {'Full Name':<20} {'Dept':<14} {'Status':<10} {'Salary':>10}")
    print(f"  {'-'*62}")
    for r in rows:
        print(f"  {r['EMP_ID']:<6} {r['FULL_NAME']:<20} "
              f"{r.get('DEPT_NAME','?'):<14} {r['STATUS_TEXT']:<10} "
              f"${r['SALARY']:>9,}")


def run_association_demo():
    print("\n" + "═"*55)
    print("ASSOCIATION DEMO — lazy vs eager fetch")
    print("═"*55)
    print("  Without _dept navigation (no JOIN needed):")
    view = Z_Emp_Composite()
    rows = view.select(include_dept=False)
    for r in rows:
        print(f"    {r['EMP_ID']} | {r['FULL_NAME']:<18} | dept_id={r['DEPT_ID']}")

    print("\n  With _dept navigation (JOIN executes now):")
    rows = view.select(include_dept=True)
    for r in rows:
        print(f"    {r['EMP_ID']} | {r['FULL_NAME']:<18} | "
              f"{r.get('DEPT_NAME','?')} ({r.get('COST_CENTER','?')})")


if __name__ == "__main__":
    print("DAY 3 — CDS VIEWS SIMULATION")
    print("VDM: Basic → Composite → Consumption")
    run_layer1()
    run_layer2()
    run_layer3_fiori()
    run_association_demo()
    print("\n" + "═"*55)
    print("You now understand CDS layering, associations,")
    print("annotations, and how Fiori consumes CDS views.")
    print("═"*55)