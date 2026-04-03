
REPORT zday2_internal_tables.

TYPES: BEGIN OF ty_customer,
         kunnr TYPE kunnr,   
         name1 TYPE name1,    
         land1 TYPE land1,  
         netwr TYPE netwr,    
       END OF ty_customer.

DATA: lt_customers TYPE TABLE OF ty_customer,  
      ls_customer  TYPE ty_customer.            

DATA: lt_kna1 TYPE TABLE OF kna1,   
      ls_kna1 TYPE kna1.

SELECT kunnr name1 land1
  FROM kna1
  INTO TABLE @lt_customers       
  WHERE land1 = 'EG'
  ORDER BY name1.

IF sy-subrc <> 0.
  WRITE: / 'No customers found for Egypt'.
  RETURN.
ENDIF.

WRITE: / 'Customers found:', lines( lt_customers ). 

LOOP AT lt_customers INTO ls_customer.

  * sy-tabix = current row index (like enumerate() in Python)
  WRITE: / sy-tabix, ls_customer-kunnr, ls_customer-name1.

ENDLOOP.


CLEAR ls_customer.                 
ls_customer-kunnr = 'C999'.
ls_customer-name1 = 'Test Customer'.
ls_customer-land1 = 'EG'.
APPEND ls_customer TO lt_customers. 

WRITE: / 'After append:', lines( lt_customers ), 'rows'.


READ TABLE lt_customers INTO ls_customer
  WITH KEY kunnr = 'C001'.

IF sy-subrc = 0.
  WRITE: / 'Found:', ls_customer-name1.
ELSE.
  WRITE: / 'Not found'.
ENDIF.

READ TABLE lt_customers INTO ls_customer
  WITH KEY kunnr = 'C001'.
IF sy-subrc = 0.
  ls_customer-name1 = 'Updated Name'.
  MODIFY lt_customers FROM ls_customer
    TRANSPORTING name1              
    WHERE kunnr = 'C001'.
ENDIF.


DELETE lt_customers WHERE land1 = 'AE'.

WRITE: / 'After delete:', lines( lt_customers ), 'rows remain'.


SORT lt_customers BY name1 ASCENDING.


DATA: ls_one TYPE ty_customer.

SELECT SINGLE kunnr name1
  FROM kna1
  INTO @ls_one
  WHERE kunnr = '0000001001'.

IF sy-subrc = 0.
  WRITE: / 'Single result:', ls_one-name1.
ENDIF.