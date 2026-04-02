


class HANADatabase:

    

    def __init__(self):
        self.tables = {
            "KNA1": [], "VBAK": [], "VBAP": [],   
        }



    def insert(self, table, record):
        self.tables[table].append(record)
        print(f"  [HANA] Persisted to {table}: {record}")



    def select(self, table, where_key=None, where_val=None):
      
      rows = self.tables[table]
      if where_key:
          rows = [r for r in rows if r.get(where_key) == where_val]
      return rows
    





class ABAPApplicationServer:
   
    def __init__(self, database):
        self.db = database

    def create_customer(self, customer_id, name, country):
        # Simulate ABAP validation logic
        print(f"\n[ABAP] Validating customer data...")
        
        if not customer_id or not name:
            raise ValueError("Customer ID and name are required")
        if len(customer_id) > 10:
            raise ValueError("Customer ID max 10 chars (SAP rule)")

        record = {
            "KUNNR": customer_id, "NAME1": name,     "LAND1": country,       
        }
        
        self.db.insert("KNA1", record)
        print(f"[ABAP] Customer {customer_id} created successfully.")
        return record

    def create_sales_order(self, order_id, customer_id, items):
        print(f"\n[ABAP] Processing sales order {order_id}...")

      
        customers = self.db.select("KNA1", "KUNNR", customer_id)
        if not customers:
            raise ValueError(f"Customer {customer_id} not found in KNA1")

        total = sum(item["price"] * item["qty"] for item in items)

       
    
        header = {"VBELN": order_id, "KUNNR": customer_id, "NETWR": total}
        self.db.insert("VBAK", header)

       
        for i, item in enumerate(items, 1):
            row = {
                "VBELN": order_id,"POSNR": str(i * 10).zfill(6),  "MATNR": item["material"],  "KWMENG": item["qty"],"NETPR": item["price"],
            }
            self.db.insert("VBAP", row)

        print(f"[ABAP] Order {order_id} total: ${total:,.2f}")
        return order_id





class FioriUI:
  
    def __init__(self, app_server):
        self.abap = app_server

    def user_creates_customer(self, cust_id, name, country):
        print(f"\n{'='*50}")
        print(f"[FIORI] User submitted: New Customer Form")
        print(f"  Customer ID : {cust_id}")
        print(f"  Name        : {name}")
        print(f"  Country     : {country}")
        self.abap.create_customer(cust_id, name, country)

    def user_creates_order(self, order_id, cust_id, items):
        print(f"\n{'='*50}")
        print(f"[FIORI] User submitted: New Sales Order Form")
        self.abap.create_sales_order(order_id, cust_id, items)

    def user_views_orders(self, customer_id):
        print(f"\n{'='*50}")
        print(f"[FIORI] Displaying orders for customer {customer_id}:")
        orders = self.abap.db.select("VBAK", "KUNNR", customer_id)
        for i in orders:
            print(f"  Order: {i['VBELN']} | Total: ${i['NETWR']:,.2f}")




if __name__ == "__main__":
    print("SAP 3-TIER ARCHITECTURE SIMULATION")
    print("Initializing system...\n")

    hana   = HANADatabase()
    abap   = ABAPApplicationServer(hana)
    fiori  = FioriUI(abap)

    fiori.user_creates_customer("C001", "Ahmed Trading Co.", "EG")


    fiori.user_creates_order(
        order_id="4500000001",
        cust_id="C001",
        items=[
            {"material": "LAPTOP-01", "qty": 5,  "price": 1200},
            {"material": "MOUSE-01",  "qty": 10, "price": 25},
        ]
    )


    fiori.user_views_orders("C001")

    print(f"\n{'='*50}")
    print("Simulation complete. All data persisted in HANA.")




