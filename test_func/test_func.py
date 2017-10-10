# -*- coding: utf-8 -*-
import sqlite3
import requests
import json
import time
from time import sleep


class TestException(Exception):
    pass


# Step 1
def check_exist_database(db_name):
    """Check: connect to DB"""
    try:
        db_name = db_name.encode('utf-8')
        conn = sqlite3.connect(db_name)
        print(('Successful cnnection to {}'.format(db_name)))
        conn.close()
        return
    except:
        raise TestException("{} dosen't exist".format(db_name))


# Step 2
def select_from_db(db_name, new_client_name, new_client_balance):
    """
    Check: is client with positive balance in database.
    If not that client will create.
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    x = cur.execute('SELECT * FROM balances WHERE balance > 0')
    rows = x.fetchone()
    if not rows:
        try:
            # Get client id and balance
            new_client_balance = float(new_client_balance.encode('utf-8'))
            new_client_name = new_client_name.encode('utf-8')
            cur.execute("INSERT INTO clients (client_name) VALUES "
                        "({!r})".format(new_client_name))
            new_client_id = cur.lastrowid
            cur.execute("INSERT INTO balances (clients_client_id, balance) "
                        "VALUES ({}, {})".format(new_client_id,
                                                 new_client_balance))
            conn.commit()
            print("Client with so balance is not in {0}. Client with name {1} "
                  "and balance {2} was created"
                  .format(db_name, new_client_name, new_client_balance))
            rows = (new_client_id, new_client_balance)
        except:
            conn.rollback()
            raise TestException("Can't to add new client {} with balance {} "
                                "in {}".format(new_client_id,
                                               new_client_balance, db_name))
        finally:
            cur.close()
            conn.close()
    return rows


# Step 3
def get_client_services(url, client_id):
    """Get list of services by client_id"""
    url = url + '/client/services'
    headers = {'Content-Type': 'application/json'}
    data = {"client_id": client_id}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    client_services = response.json().get('items')
    print("Client with id={} have list of the services {}"
          .format(client_id, client_services))
    return(client_services)


# Step 4
def get_list_available_services(url):
    """Get list of available services"""
    url = url + '/services'
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    services_list = response.json().get('items')
    print('List of available services is {}'.format(services_list))
    return(services_list)


# Step 5
def find_service_for_client(client_services, all_services, client_id):
    """Find a service that the client doesn't use"""
    # Get set of client_service_id
    client_service_ids = {client_service.get(u'id')
                          for client_service in client_services}
    # Find service that client don't use
    for service in all_services:
        if service.get(u'id') not in client_service_ids:
            service_id_service_cost = [service.get(u'id'),
                                       service.get(u"cost")]
            return (service_id_service_cost)
    raise TestException('Client {} use all of available services'
                        .format(client_id))


# Step 6
def add_service_to_client_fun(url, client_id, service_id):
    """Add the service to the client"""
    url = url + '/client/add_service'
    headers = {'Content-Type': 'application/json'}
    data = {"client_id": client_id, "service_id": service_id}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 202:
        print('Start adding service {} to client {}'
              .format(service_id, client_id))
        return
    else:
        raise TestException('Server response is incorrect')


# Step 7
def is_service_add_to_client(url, client_id, service_id):
    """Check that new service add to client services list while 60 s"""
    url = url + '/client/services'
    headers = {'Content-Type': 'application/json'}
    data = {"client_id": client_id}
    start_time = time.time()
    is_service_add = False
    while time.time() - start_time <= 60 and not is_service_add:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        client_services = response.json()['items']
        for client_service in client_services:
            client_service_id = client_service.get(u'id')
            if client_service_id == service_id:
                is_service_add = True
                break
        sleep(1)
    if is_service_add:
        print('Check: service {} was added to client {}'
              .format(service_id, client_id))
        return
    else:
        raise TestException("Service {} wasn't added to client {} in 60 s"
                            .format(service_id, client_id))


# Step 8
def get_new_balance(db_name, client_id):
    """Get new balance of the client"""
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    x = cur.execute('SELECT balance FROM balances WHERE CLIENTS_CLIENT_ID = {}'
                    .format(client_id))
    new_balance = x.fetchone()
    cur.close()
    conn.close()
    return new_balance[0]


# Step 9
def correctness_of_balace(final_balance, start_balance,
                          servise_cost):
    """Check correcness of balace value"""
    if final_balance == start_balance - servise_cost:
        return ('TEST SUCCESSFUL')
    else:
        raise TestException("We didn't subtract service cost "
                            "from balance value")
