
REPORT zhello_sap.


DATA: lv_name    TYPE string,
      lv_count   TYPE int4,
      lv_date    TYPE dats,
      lv_amount  TYPE p DECIMALS 2.

lv_name   = 'SAP ABAP Learner'.
lv_count  = 42.
lv_date   = sy-datum.    
lv_amount = '1500.75'.

WRITE: / 'Hello from SAP!'.
WRITE: / 'Name    :', lv_name.
WRITE: / 'Count   :', lv_count.
WRITE: / 'Today   :', lv_date.
WRITE: / 'Amount  :', lv_amount.


WRITE: / 'User    :', sy-uname.
WRITE: / 'Client  :', sy-mandt.

IF lv_count > 10.
  WRITE: / 'Count is greater than 10'.
ELSEIF lv_count = 0.
  WRITE: / 'Count is zero'.
ELSE.
  WRITE: / 'Count is small'.
ENDIF.

DATA: lv_i TYPE int4.
DO 3 TIMES.
  lv_i = sy-index.   
  WRITE: / 'Iteration:', lv_i.
ENDDO.