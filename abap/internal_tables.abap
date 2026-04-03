
REPORT zday2_internal_tables.

TYPES: BEGIN OF ty_customer,
         kunnr TYPE kunnr,   name1 TYPE name1,   land1 TYPE land1,    netwr TYPE netwr,    
       END OF ty_customer.

DATA: lt_customers TYPE TABLE OF ty_customer,  
      ls_customer  TYPE ty_customer.            

DATA: lt_kna1 TYPE TABLE OF kna1,   
      ls_kna1 TYPE kna1.

SELECT kunnr name1 land1
  FROM kna1
  INTO TABLE @lt_customers       
  WHERE land1 = 'eg'
  ORDER BY name1.

IF sy-subrc <> 0.
  WRITE: / 'no customers found in egypt'.
  RETURN.
ENDIF.

WRITE: / 'customers found:', lines( lt_customers ). 

LOOP AT lt_customers INTO ls_customer.

  * sy-tabix = current row index (like enumerate() in Python)
  WRITE: / sy-tabix, ls_customer-kunnr, ls_customer-name1.

ENDLOOP.


CLEAR ls_customer.                 
ls_customer-kunnr = 'c999'.
ls_customer-name1 = 'test customer'.
ls_customer-land1 = 'eg'.
APPEND ls_customer TO lt_customers. 

WRITE: / 'after append:', lines( lt_customers ),'rows'.


READ TABLE lt_customers INTO ls_customer
  WITH KEY kunnr = 'c001'.

IF sy-subrc = 0.
  WRITE: / 'found:', ls_customer-name1.
ELSE.
  WRITE: / 'not found'.
ENDIF.

READ TABLE lt_customers INTO ls_customer
  WITH KEY kunnr = 'c001'.
IF sy-subrc = 0.
  ls_customer-name1 = 'updated name'.
  MODIFY lt_customers FROM ls_customer
    TRANSPORTING name1              
    WHERE kunnr = 'c001'.
ENDIF.


DELETE lt_customers WHERE land1 = 'ae'.

WRITE: / 'after delete:', lines( lt_customers ),'rows remain'.


SORT lt_customers BY name1 ASCENDING.


DATA: ls_one TYPE ty_customer.

SELECT SINGLE kunnr name1
  FROM kna1
  INTO @ls_one
  WHERE kunnr = '0000001001'.

IF sy-subrc = 0.
  WRITE: / 'single result:', ls_one-name1.
ENDIF.