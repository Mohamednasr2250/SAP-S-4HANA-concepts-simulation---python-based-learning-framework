

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import date


class Domain:
 
    def __init__(self, name, data_type, length, values=None):
        self.name      = name       
        self.data_type = data_type 
        self.length    = length     
        self.values    = values     

    def validate(self, value):
        if self.values and value not in self.values:
            raise ValueError(
                f"Domain {self.name}: '{value}' not in allowed values "
                f"{list(self.values.keys())}"
            )
        if self.data_type == "NUMC":
            if not str(value).isdigit():
                raise ValueError(f"Domain {self.name}: must be numeric digits")
        return True

    def __repr__(self):
        return f"Domain({self.name}: {self.data_type}({self.length}))"



DOMAIN_MANDT    = Domain("MANDT",    "CHAR", 3)    
DOMAIN_EMP_ID   = Domain("ZEMP_ID",  "NUMC", 6)    
DOMAIN_NAME     = Domain("ZNAME",    "CHAR", 40)   
DOMAIN_DEPT_ID  = Domain("ZDEPT_ID", "CHAR", 4)    
DOMAIN_SALARY   = Domain("ZSALARY",  "CURR", 13)   
DOMAIN_CUKY     = Domain("CUKY",     "CHAR", 5)   
DOMAIN_DATS     = Domain("DATS",     "DATS", 8)   
DOMAIN_STATUS   = Domain(            
    "ZDOMAIN_STATUS", "CHAR", 1,
    values={
        "A": "Active",
        "I": "Inactive",
        "T": "Terminated"
    }
)



class DataElement:
 
    def __init__(self, name, domain, short_label, medium_label, long_label):
        self.name         = name         
        self.domain       = domain        
        self.short_label  = short_label   
        self.medium_label = medium_label  
        self.long_label   = long_label    

    def validate(self, value):
        return self.domain.validate(value)

    def __repr__(self):
        return f"DataElement({self.name} → {self.domain.name})"


DE_CLIENT     = DataElement("MANDT",      DOMAIN_MANDT,
                            "Client",     "Client",          "SAP Client")
DE_EMP_ID     = DataElement("ZEMP_ID",    DOMAIN_EMP_ID,
                            "Emp.ID",     "Employee ID",     "Unique Employee Identifier")
DE_FIRST_NM   = DataElement("ZFIRST_NM",  DOMAIN_NAME,
                            "First Name", "First Name",      "Employee First Name")
DE_LAST_NM    = DataElement("ZLAST_NM",   DOMAIN_NAME,
                            "Last Name",  "Last Name",       "Employee Last Name")
DE_DEPT_ID    = DataElement("ZDEPT_ID",   DOMAIN_DEPT_ID,
                            "Dept",       "Department",      "Department Code")
DE_SALARY     = DataElement("ZSALARY",    DOMAIN_SALARY,
                            "Salary",     "Monthly Salary",  "Gross Monthly Salary")
DE_CURRENCY   = DataElement("ZWAERK",     DOMAIN_CUKY,
                            "Curr.",      "Currency",        "Currency Key")
DE_HIRE_DATE  = DataElement("ZHIRE_DATE", DOMAIN_DATS,
                            "Hire Date",  "Date of Hire",    "Employee Start Date")
DE_STATUS     = DataElement("ZEMP_STAT",  DOMAIN_STATUS,
                            "Status",     "Emp. Status",     "Employment Status")




class DDICStructure:

    def __init__(self, name, components: dict):

        self.name       = name
        self.components = components

    def create_instance(self, **kwargs):
     
        instance = {}
        for field_name, data_element in self.components.items():
            value = kwargs.get(field_name, None)
            if value is not None:
                data_element.validate(value)
            instance[field_name] = value
        return instance

    def __repr__(self):
        fields = list(self.components.keys())
        return f"Structure({self.name}: {fields})"


ZS_ADDRESS = DDICStructure("ZS_ADDRESS", {
    "STREET":   DataElement("ZSTREET",  DOMAIN_NAME, "Street", "Street", "Street Name"),
    "CITY":     DataElement("ZCITY",    DOMAIN_NAME, "City",   "City",   "City Name"),
    "COUNTRY":  DataElement("ZCOUNTRY", DOMAIN_DEPT_ID, "Cntry", "Country", "Country Code"),
    "POSTCODE": DataElement("ZPOSTCD",  DOMAIN_EMP_ID, "Post", "Postcode", "Postal Code"),
})



class TransparentTable:
   
 
    def __init__(self, name, fields: dict, key_fields: list, foreign_keys=None):
        self.name         = name
        self.fields       = fields        
        self.key_fields   = key_fields    
        self.foreign_keys = foreign_keys or {}  

       
        self._storage = {}  

    def _validate_record(self, record: dict, fk_registry: dict = None):
        for field_name, data_element in self.fields.items():
            if field_name in record:
                data_element.validate(record[field_name])

        if fk_registry and self.foreign_keys:
            for fk_field, ref_table_name in self.foreign_keys.items():
                fk_value = record.get(fk_field)
                ref_table = fk_registry.get(ref_table_name)
                if ref_table and fk_value:
                    client = record.get("MANDT", "100")
                    exists = any(
                        r.get(fk_field) == fk_value
                        for r in ref_table._storage.get(client, [])
                    )
                    if not exists:
                        raise ValueError(
                            f"FK violation: {fk_field}='{fk_value}' not found "
                            f"in {ref_table_name}"
                        )

    def insert(self, record: dict, client="100", fk_registry=None):
        
        record["MANDT"] = client
        self._validate_record(record, fk_registry)

        if client not in self._storage:
            self._storage[client] = []

        for existing in self._storage[client]:
            if all(existing.get(k) == record.get(k) for k in self.key_fields):
                raise ValueError(
                    f"Duplicate key: {[record.get(k) for k in self.key_fields]}"
                )

        self._storage[client].append(record.copy())
        return True

    def select(self, client="100", where=None):
       
        rows = self._storage.get(client, []).copy()
        if where:
            for field_name, value in where.items():
                rows = [r for r in rows if r.get(field_name) == value]
        sy_subrc = 0 if rows else 4
        return rows, sy_subrc

    def count(self, client="100"):
        return len(self._storage.get(client, []))

    def __repr__(self):
        total = sum(len(v) for v in self._storage.values())
        return f"Table({self.name}: {total} records across all clients)"



ZDEPARTMENTS = TransparentTable(
    name="ZDEPARTMENTS",
    fields={
        "MANDT":     DE_CLIENT,
        "DEPT_ID":   DE_DEPT_ID,
        "DEPT_NAME": DE_FIRST_NM,
        "COST_CTR":  DE_DEPT_ID,
    },
    key_fields=["MANDT", "DEPT_ID"]  
)

ZEMPLOYEES = TransparentTable(
    name="ZEMPLOYEES",
    fields={
        "MANDT":     DE_CLIENT,
        "EMP_ID":    DE_EMP_ID,
        "FIRST_NM":  DE_FIRST_NM,
        "LAST_NM":   DE_LAST_NM,
        "DEPT_ID":   DE_DEPT_ID,  
        "SALARY":    DE_SALARY,
        "CURRENCY":  DE_CURRENCY,
        "HIRE_DATE": DE_HIRE_DATE,
        "STATUS":    DE_STATUS, 
    },
    key_fields=["MANDT", "EMP_ID"],
    foreign_keys={"DEPT_ID": "ZDEPARTMENTS"} 
)

FK_REGISTRY = {
    "ZDEPARTMENTS": ZDEPARTMENTS,
    "ZEMPLOYEES":   ZEMPLOYEES,
}




def run_ddic_simulation():
    print("\n" + "═"*55)
    print("LAYER 1+2: Domains and Data Elements")
    print("═"*55)
    print("  Domains defined:")
    for d in [DOMAIN_EMP_ID, DOMAIN_STATUS, DOMAIN_SALARY]:
        print(f"    {d}")
    print("\n  Data Elements defined:")
    for de in [DE_EMP_ID, DE_STATUS, DE_SALARY]:
        print(f"    {de} | Labels: '{de.short_label}' / '{de.long_label}'")

    print("\n" + "═"*55)
    print("LAYER 3: Structure (ZS_ADDRESS)")
    print("═"*55)
    print(f"  {ZS_ADDRESS}")
    addr = ZS_ADDRESS.create_instance(
        STREET="26 July St", CITY="Cairo", COUNTRY="EG", POSTCODE="123456"
    )
    print(f"  Sample instance: {addr}")
    print("  (No database table — pure type definition)")

    print("\n" + "═"*55)
    print("LAYER 4: Transparent Table — INSERT records")
    print("═"*55)

    print("\n  Inserting into ZDEPARTMENTS (client 100 = production):")
    departments = [
        {"DEPT_ID": "D001", "DEPT_NAME": "Finance",    "COST_CTR": "CC01"},
        {"DEPT_ID": "D002", "DEPT_NAME": "Sales",      "COST_CTR": "CC02"},
        {"DEPT_ID": "D003", "DEPT_NAME": "Technology", "COST_CTR": "CC03"},
    ]
    for dept in departments:
        ZDEPARTMENTS.insert(dept, client="100")
        print(f"    Inserted dept: {dept['DEPT_ID']} | {dept['DEPT_NAME']}")

    print(f"\n  Inserting into ZEMPLOYEES (with FK validation):")
    employees = [
        {"EMP_ID":"000001","FIRST_NM":"Ahmed","LAST_NM":"Hassan",
         "DEPT_ID":"D001","SALARY":85000,"CURRENCY":"USD",
         "HIRE_DATE":"20210315","STATUS":"A"},
        {"EMP_ID":"000002","FIRST_NM":"Sara","LAST_NM":"Khalil",
         "DEPT_ID":"D002","SALARY":92000,"CURRENCY":"USD",
         "HIRE_DATE":"20190801","STATUS":"A"},
        {"EMP_ID":"000003","FIRST_NM":"Omar","LAST_NM":"Fawzi",
         "DEPT_ID":"D001","SALARY":78000,"CURRENCY":"EGP",
         "HIRE_DATE":"20220601","STATUS":"I"},
    ]
    for emp in employees:
        ZEMPLOYEES.insert(emp, client="100", fk_registry=FK_REGISTRY)
        print(f"    Inserted: {emp['EMP_ID']} | "
              f"{emp['FIRST_NM']} {emp['LAST_NM']} | "
              f"dept={emp['DEPT_ID']} ✓ FK valid")

    print("\n" + "═"*55)
    print("Domain Validation — STATUS field")
    print("═"*55)
    print("  Trying to insert employee with STATUS='X' (invalid)...")
    try:
        ZEMPLOYEES.insert({
            "EMP_ID":"000099","FIRST_NM":"Test","LAST_NM":"User",
            "DEPT_ID":"D001","SALARY":50000,"CURRENCY":"USD",
            "HIRE_DATE":"20240101","STATUS":"X"  
        }, client="100", fk_registry=FK_REGISTRY)
    except ValueError as e:
        print(f"  ✗ Caught domain violation: {e}")

    print("\n  Trying to insert employee with DEPT_ID='D999' (FK violation)...")
    try:
        ZEMPLOYEES.insert({
            "EMP_ID":"000098","FIRST_NM":"Bad","LAST_NM":"Ref",
            "DEPT_ID":"D999","SALARY":50000,"CURRENCY":"USD",
            "HIRE_DATE":"20240101","STATUS":"A" 
        }, client="100", fk_registry=FK_REGISTRY)
    except ValueError as e:
        print(f"  ✗ Caught FK violation: {e}")

    print("\n" + "═"*55)
    print("Client Separation — same table, different clients")
    print("═"*55)

    ZDEPARTMENTS.insert(
        {"DEPT_ID":"T001","DEPT_NAME":"Test Finance","COST_CTR":"TC01"},
        client="200"  
    )
    prod_count = ZDEPARTMENTS.count(client="100")
    test_count = ZDEPARTMENTS.count(client="200")
    print(f"  Client 100 (production) departments: {prod_count}")
    print(f"  Client 200 (test)       departments: {test_count}")
    print(f"  → Same ZDEPARTMENTS table, completely separate data")

    print("\n" + "═"*55)
    print("SELECT from ZEMPLOYEES")
    print("═"*55)
    rows, sy_subrc = ZEMPLOYEES.select(client="100")
    print(f"  sy-subrc = {sy_subrc}")
    print(f"  {'EMP_ID':<8} {'Name':<18} {'Dept':<6} {'Status':<8} {'Salary':>10}")
    print(f"  {'-'*52}")
    for r in rows:
        print(f"  {r['EMP_ID']:<8} "
              f"{r['FIRST_NM']+' '+r['LAST_NM']:<18} "
              f"{r['DEPT_ID']:<6} {r['STATUS']:<8} ${r['SALARY']:>9,}")

    print(f"\n  {ZEMPLOYEES}")
    print(f"  {ZDEPARTMENTS}")


if __name__ == "__main__":
    print("DAY 5 — SAP DATA MODELLING SIMULATION")
    print("DDIC: Domain → Data Element → Structure → Transparent Table")
    run_ddic_simulation()
    print("\n" + "═"*55)
    print("DDIC is the backbone of all SAP data.")
    print("Everything starts here before any ABAP code touches it.")
    print("═"*55)