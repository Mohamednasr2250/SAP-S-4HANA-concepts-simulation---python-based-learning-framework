
REPORT zhello_sap.


DATA: lv_name    TYPE string,
      lv_count   TYPE int4,lv_date    TYPE dats,lv_amount  TYPE p DECIMALS 2.

lv_name  = 'SAP ABAP'.
lv_count = 42.
lv_date  = sy-datum.    
lv_amount = '1500.75'.

WRITE: / 'hello from SAP'.
WRITE: / 'name  :', lv_name.
WRITE: / 'count :', lv_count.
WRITE: / 'today :', lv_date.
WRITE: / 'amount:', lv_amount.


WRITE: / 'User    :', sy-uname.
WRITE: / 'Client  :', sy-mandt.

IF lv_count > 10.  
  WRITE: / 'count greater than 10'.
ELSEIF lv_count = 0.
  WRITE: / 'zero count'.
ELSE.
  WRITE: / 'small count'.
ENDIF.

DATA: lv_i TYPE int4.
DO 3 TIMES.
  lv_i = sy-index.   
  WRITE: / 'iteration:', lv_i.
ENDDO.