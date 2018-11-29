*** Settings ***
Library             ExcelRobot
*** Test Cases ***
Write Excel
    ${xls}  set variable  d:\\towrite.xls
    ${xlsx}  set variable  d:\\towrite.xlsx
    Open Excel To Write  ${xlsx}
#    write to cell  Sheet1  0  0  A1  still have bug
    write to cell  Sheet1  0  1  B2
#    write to cell  Sheet1  2  1  C2
    Write To Cell By Name  Sheet1  A1  a11byname
    Write To Cell By Name  Sheet1  C1  c11byname
    Save Excel