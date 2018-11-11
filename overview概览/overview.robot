*** Settings ***
Library    OperatingSystem
Suite Setup    Clear database

*** Test Cases ***
Login with nobody
    ${resp}    Login    nobody    P4ssw0rd
    should be equal as strings    ${resp}    Access Denied

Create and log in
    ${resp}    Create user  Tony    P4ssw0rd
    should be equal  ${resp}    SUCCESS
    ${resp}    Login          Tony  P4ssw0rd
    should be equal as strings  ${resp}     Logged In

*** Keywords ***
Clear database
    remove file     ${database_path}

Run target
    [Arguments]     ${option}   ${username}     ${password}     ${new_password}=${None}
    ${full_path}    set variable     ${targets_dir}${/}login.py
    ${resp}   run  python ${full_path} ${option} ${username} ${password}
    [Return]  ${resp}

Create user
    [Arguments]  ${username}    ${password}
    ${resp}  Run target  create  ${username}    ${password}
    [Return]  ${resp}

Login
    [Arguments]  ${username}    ${password}
    ${resp}  Run target  login    ${username}     ${password}
    [Return]  ${resp}

Change password
    [Arguments]  ${username}    ${password}     ${new_password}
    ${resp}  Run target  change-password  ${username}   ${password}    ${new_password}
    [Return]  ${resp}

*** Variables ***
${targets_dir}      ${CURDIR}${/}..${/}targets
${database_path}    ${temp_dir}${/}robotframework-quickstart-db.txt