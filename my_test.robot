*** Settings ***
Library     Collections
Library     test_func/test_func.py


*** Variables ***
${DB_NAME} =                web/clients.db
${Local_host_port}          http://localhost:5000
${new_client_name}          Nik Zalman
${new_client_balance}       5


*** Test Cases ***
Step1: Check DB connection
    Check DB connection

Step2: Get client with positive balance
    Get client with positive balance

Step3: Get client services list
    Get client services list

Step4: Get list of all available services
    Get list of all available services

Step5: Find a service that the client does not use
    Find a service that the client does not use

Step6: Add service to client
    Add service to client


Step7: Check that service add to client
    Check that service add to client

Step8: Get new balance of the client
    Get new balance of the client

Step9: Compare start and end value of client's balance
    Compare start and end value of client's balance


*** Keywords ***
Check DB connection
    check_exist_database        ${DB_NAME}

Get client with positive balance
    ${client_id_client_balance} =       select_from_db      ${DB_NAME}      ${new_client_name}      ${new_client_balance}
    ${client_id} =                      Get From List       ${client_id_client_balance}     0
    ${client_balance} =                 Get From List       ${client_id_client_balance}     1
    Set Global Variable       ${client_id}     ${client_id}
    Set Global Variable       ${client_balance}     ${client_balance}

Get client services list
    ${client_services} =        get_client_services     ${Local_host_port}      ${client_id}
    Set Global Variable           ${client_services}      ${client_services}

Get list of all available services
    ${list_available_services} =        get_list_available_services     ${Local_host_port}
    Set Global Variable       ${list_available_services}      ${list_available_services}

Find a service that the client does not use
    ${service_id_service_cost} =         find_service_for_client     ${client_services}      ${list_available_services}     ${client_id}
    ${service_id} =           Get From List       ${service_id_service_cost}      0
    ${service_cost} =         Get From List       ${service_id_service_cost}      1
    Set Global Variable         ${service_id}       ${service_id}
    Set Global Variable         ${service_cost}     ${service_cost}

Add service to client
    add_service_to_client_fun       ${Local_host_port}      ${client_id}        ${service_id}

Check that service add to client
    is_service_add_to_client        ${Local_host_port}      ${client_id}        ${service_id}

Get new balance of the client
    ${new_balance} =        get_new_balance     ${DB_NAME}      ${client_id}
    Set Global Variable       ${new_balance}      ${new_balance}

Compare start and end value of client's balance
    correctness_of_balace        ${new_balance}      ${client_balance}       ${service_cost}


