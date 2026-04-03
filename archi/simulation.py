


class HANAdatabase:

    
    def __init__(self):
        self.tables = {
            "kna1": [], "vbak": [], "vbap": [],   
        }

    def insert(self, table, record):
        self.tables[table].append(record)
        print(f"HANA: Persisted to {table}: {record}")

    def select(self, table, where_key=None, where_val=None):
      rows = self.tables[table]
      if where_key:
          rows = [r for r in rows if r.get(where_key) == where_val]
      return rows
    





class ABAPApplicationServer:
   
    def __init__(self, database):
        self.db = database

    def create_customer(self, customer_id, name, country):
       
        print(f"\n ABAP: validating customer data")
        if not customer_id or not name:
            raise ValueError("customer id,name required")
        if len(customer_id) > 10:
            raise ValueError("customer id 10 chars max")

        record = {
            "kunnr": customer_id, "name1": name,     "land1": country,       
        }
        
        self.db.insert("kna1", record)
        print(f"ABAP: customer {customer_id} done,created successfully")
        
        return record



    def create_sales_order(self, order_id, customer_id, items):
        print(f"\n ABAP: proces sales order{order_id}")

      
        customers = self.db.select("kna1", "kunner", customer_id)
        if not customers:
            raise ValueError(f"customer{customer_id}not found in kna1")

        total=sum(item["price"]*item["qty"] for item in items)

        header= {"vbeln":order_id,"kunner":customer_id,"netwr":total}
        self.db.insert("vbak",header)

        for i, item in enumerate(items, 1):
            row = {
                "vbeln": order_id,"posnr": str(i * 10).zfill(6),  "matnr": item["material"],  "kwmeng": item["qty"],"netpr": item["price"],
            }
            self.db.insert("vbap", row)

        print(f"ABAP: order {order_id} total:${total:,.2f}")
        
        return order_id




class FioriUI:
  
    def __init__(self, app_server):
        self.abap = app_server

    def user_creates_customer(self, cust_id, name, country):
        print(f"\n{'='*50}")
        print(f"FIORI: user subm: new Customer")
        print(f"   id : {cust_id}")
        print(f"  name        : {name}")
        print(f"  country     : {country}")
        self.abap.create_customer(cust_id, name, country)

    def user_creates_order(self, order_id, cust_id, items):
        print(f"\n{'='*50}")
        print(f"FIORI: user subm: new sales order")
        self.abap.create_sales_order(order_id, cust_id, items)

    def user_views_orders(self, customer_id):
        print(f"\n{'='*50}")
        print(f"FIORI: displaying orders for customer {customer_id}:")
        orders = self.abap.db.select("vbak", "kunnr", customer_id)
        for i in orders:
            print(f"  Order: {i['vbeln']} | total: ${i['netwr']:,.2f}")



#
if __name__ == "__main__":
    print("SAP 3-TIER ARCHITECTURE SIMULATION")
    print("Initializing system...\n")

    hana   = HANAdatabase()
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

#
    fiori.user_views_orders("c001")

    print(f"\n{'='*50}")
    print("simulation done,all data persisted in HANA")




