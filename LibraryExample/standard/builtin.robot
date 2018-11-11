
*** Test Cases ***
失败信息
    [Documentation]  很多关键字可以自定义失败时的错误信息
#    fail  错误信息: 我是自己失败的.
    pass execution  对应的,这可以直接以通过结果结束测试.

evaluate计算表达式
    [Documentation]  非常多关键字需要计算表达式的值, 如条件执行run keyword if等
    run keyword if  os.sep=='/'  log  running on *unix  # 系统路径分隔符是判断win/*unix平台的一个方法
    ${name}  set variable  Tony
    run keyword if  '${name}'=='Tony'  log  valid user!  # 字符串变量需要被引号包裹
    run keyword if  $name =='Tony'  log  valid user!  # 在被evaluate的时候, 变量可以不用花括号包裹, 此时绝对不要用引号

布尔表达式
    [Documentation]  很多关键词的参数需要传递布尔值, 只建议用${TRUE}和${FALSE}
    run keyword and ignore error  should be equal  aa  bb  MyError  values=True  # 日志可以见到: MyError: aa != bb
    run keyword and ignore error  should be equal  aa  bb  MyError  values=non-empty string  # 日志可以见到: MyError: aa != bb
    run keyword and ignore error  should be equal  aa  bb  MyError  values=${TRUE}  # 日志可以见到: MyError: aa != bb
    run keyword and ignore error  should be equal  aa  bb  MyError  values=${42}  # 日志可以见到: MyError: aa != bb
#    run keyword if  non-empty string  log  This's WRONG!  # 非空字符串不能在run keyword if中使用

