

@AbapCatalog.sqlViewName: 'ZEMP_BASIC'
@AbapCatalog.compiler.compareFilter: true
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Employee Basic View'

define view Z_Emp_Basic
  as select from zemployees
{
  key emp_id                        as EmployeeId,
      first_nm                      as FirstName,
      last_nm                       as LastName,
      dept_id                       as DepartmentId,
      salary                        as Salary,
      hire_date                     as HireDate,
      status                        as Status
}


@AbapCatalog.sqlViewName: 'ZEMP_COMP'
@EndUserText.label: 'Employee Composite View'

define view Z_Emp_Composite
  as select from Z_Emp_Basic as emp


  association [0..1] to Z_Dept_Basic as _Department
    on emp.DepartmentId = _Department.DepartmentId

{
  key emp.EmployeeId,
      emp.FirstName,
      emp.LastName,

      concat(emp.FirstName, ' ', emp.LastName) as FullName,

      emp.DepartmentId,
      emp.Salary,
      emp.HireDate,

      case emp.Status
        when 'A' then 'Active'
        when 'I' then 'Inactive'
        when 'T' then 'Terminated'
        else          'Unknown'
      end                           as StatusText,

      _Department
}


@AbapCatalog.sqlViewName: 'ZEMP_CONS'
@EndUserText.label: 'Employee Consumption View'

@OData.publish: true

@UI.headerInfo: {
  typeName:       'Employee',
  typeNamePlural: 'Employees',
  title:          { value: 'FullName' }
}

define view Z_Emp_Consumption
  as select from Z_Emp_Composite
{
     

  @UI.lineItem:       [{ position: 10, label: 'ID'         }]
  @UI.selectionField: [{ position: 10                       }]
  key EmployeeId,

  @UI.lineItem: [{ position: 20, label: 'Full Name' }]
      FullName,

  @UI.lineItem:       [{ position: 30, label: 'Department' }]
  @UI.selectionField: [{ position: 20                       }]
      DepartmentId,

  @UI.lineItem: [{ position: 40, label: 'Status' }]
  @UI.selectionField: [{ position: 30            }]
      StatusText,

  @UI.lineItem: [{ position: 50, label: 'Salary' }]
      Salary, HireDate,

  _Department.DepartmentName  as DepartmentName,
  _Department.CostCenter      as CostCenter
}