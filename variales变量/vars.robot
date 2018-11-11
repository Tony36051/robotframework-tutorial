*** Settings ***
Library  ../ExtLibrarys/VarLibrary.py
Variables  ../Variables/vars.py  # 变量文件名不要跟类名一样

*** Test Cases ***
变量名忽略大小写/下划线/空格
    ${a_boy}    set variable  tony
    should be equal as strings  tony  ${a_boy}
    should be equal as strings  tony  ${A_boy}
    should be equal as strings  tony  ${aboy}
    should be equal as strings  tony  ${ABOY}
    LOG     ${CURDIR}  # 特殊例子

Scalar标量
    ${GREET}    set variable  Hello
    ${NAME}     set variable  world
    Log    Hello, world!!           # 常量
    Log    ${GREET}, ${NAME}!!      # 变量

List列表变量
    @{user}    create list  robot  secret
    Login    robot    secret
    Login   @{user}  # 等同上一个

List变量关键字传参, 列表可扩展性
    Show list    @{LIST}    more    args
    Show list    ${SCALAR}    @{LIST}    constant
    Show list    @{LIST}    @{ANOTHER}    @{ONE MORE}

List变量访问, 变量索引
    ${index}    set variable  1
    Show list  @{LIST}[0]  @{LIST}[1]  @{LIST}[-1]
    should be equal as strings  @{LIST}[${INDEX}]  ${LIST[${INDEX}]}  # 两种不同写法

Dict字典变量
    ${key}  set variable  name
    Login   password=secret  name=robot  # 命名参数, 顺序无关
    Login   &{user1}
    Login   &{user1}[${key}]  &{user1}[password]  # 还可以${user1.name}和${user1['name']}

Dict变量关键字传参, 可扩展性
    Login  robot  &{password_part}  # 如python, 位置参数-列表参数-命名参数
    Login  &{name_part}  password=secret   #合并
    Login  &{name_part}  &{password_part}  #合并

字符串连接
    [Documentation]  传参给关键字和函数需要注意, 连接后入参为字符串
    ${STR}      set variable  Hello world!!
    ${str_type}  get type    ${STR}                 # str类型
    ${list_type}  get type    ${LIST}               # list类型, 使用@会展开成n个参数
    ${user1_type}  get type  ${user1}                # dict类型,使用&会展开为命名参数
    ${concat_str_type}  get type  str: ${STR}       # str类型
    ${concat_list_type}  get type  list: @{LIST}    # str类型
    ${concat_dict_type}  get type  dict: &{user1}   # str类型
    should contain  ${str_type}  str
    should contain  ${list_type}  list
    should contain  ${user1_type}  dict
    should contain  ${concat_str_type}  str
    should contain  ${concat_list_type}  str
    should contain  ${concat_dict_type}  str

扩展语法:MyObject
    Log    ${OBJECT.name}
    Log    ${OBJECT.eat('Cucumber')}
    Log    ${DICTIONARY[2]}

扩展语法:String
    ${string} =    Set Variable    abc
    Log    ${string.upper()}      # Logs 'ABC'
    Log    ${string * 2}          # Logs 'abcabc'

扩展语法:Number
    ${number} =    Set Variable    ${-2}
    Log    ${number * 10}         # Logs -20
    Log    ${number.__abs__()}    # Logs 2

扩展语法:赋值
    ${OBJECT.name} =    Set Variable    New name
    ${OBJECT.new_attr} =    Set Variable    New attribute
    should be equal as strings  ${OBJECT}  New name
    should be equal as strings  ${OBJECT.new_attr}  New attribute

扩展语法:嵌套
    ${OBJECT.name} =    Set Variable    T-800
    ${key} =    Set Variable    name
    ${T-800 HOME}  set variable  /home/T-800
    should be equal as strings  ${OBJECT.${key}}  T-800
    should be equal as strings  ${${OBJECT.name} HOME}  /home/T-800

*** Keywords ***
Login
    [Arguments]    ${name}  ${password}
    should be equal as strings  ${name}  robot
    should be equal as strings  ${password}  secret

Show list
    [Arguments]  @{obj}
    Log  list: @{obj}

*** Variables ***
${SCALAR}    3.1415926
@{LIST}     1st  2nd  3rd
@{ANOTHER}  4th  5th
@{ONE MORE}  6th
&{user1}     name=robot  password=secret
&{name_part}     name=robot
&{password_part}     password=secret
