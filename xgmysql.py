# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
from pythonping import ping
import concurrent.futures
import time

def ping_host(ip):
    try:
        response = ping(ip, count=4, timeout=1)
        if response.success():
            return f"{response.rtt_avg_ms} ms"
        else:
            return "no connect"
    except Exception as e:
        return "no connect"

def update_delay(connection, uid, delay):
    try:
        cursor = connection.cursor()
        if delay == "no connect":
            delay_value = "0"
        else:
            delay_value = delay.split(' ')[0]  # Assuming delay is a string like "100 ms"
        sql_update_query = "UPDATE list SET delay1 = %s WHERE uid = %s"
        cursor.execute(sql_update_query, (delay_value, uid))
        connection.commit()
    except Error as e:
        print(f"Error updating database: {e}")
    finally:
        if cursor:
            cursor.close()

def connect_fetch():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='192.168.192.64',
            user='dragon',
            password='1bJPGc2E',
            database='openvpn_list',
            charset='utf8mb4'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT uid, IP FROM list")
            rows = cursor.fetchall()

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ip = {executor.submit(ping_host, row[1]): row for row in rows}
                for future in concurrent.futures.as_completed(future_to_ip):
                    row = future_to_ip[future]
                    uid, ip = row
                    delay = future.result()
                    update_delay(connection, uid, delay)

    except Error as e:
        print(f"mysql no{e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("mysql con not")

if __name__ == '__main__':
    while True:  # Keep running the script indefinitely
        try:
            connect_fetch()
        except Exception as e:
            print(f"An error occurred: {e}")
        print("Waiting for 30 minutes before next execution.")
        time.sleep(1800)  # Wait for 1800 seconds (30 minutes) before next execution

