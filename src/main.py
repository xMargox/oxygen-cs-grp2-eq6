from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
import os
import psycopg2


class Main:
    def __init__(self):
        self._hub_connection = None
        self.HOST = "http://34.95.34.5"  # Setup your host here
        self.TOKEN = os.environ["TOKEN"]  # Setup your token here
        self.TICKETS = os.environ.get("TICKETS", 2)  # Setup your tickets here
        self.T_MAX = os.environ.get("T_MAX", 21)  # Setup your max temperature here
        self.T_MIN = os.environ.get("T_MIN", 15)  # Setup your min temperature here
        self.DATABASE = None  # Setup your database here

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()

    def setup(self):
        self.setSensorHub()

    def start(self):
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setSensorHub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.onSensorDataReceived)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def onSensorDataReceived(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])
            #self.send_temperature_to_fastapi(date, dp)
            self.analyzeDatapoint(date, dp)
        except Exception as err:
            print(err)

    def analyzeDatapoint(self, date, data):
        if float(data) >= float(self.T_MAX):
            self.sendActionToHvac(date, "TurnOnAc", self.TICKETS)
        elif float(data) <= float(self.T_MIN):
            self.sendActionToHvac(date, "TurnOnHeater", self.TICKETS)

    def send_event_to_database(self, timestamp, event):
        try:
            # Create the connection to the database
            connection_string = "host=localhost port=5432 dbname=OxygenOS user=postgres password=postgres"
            connection = psycopg2.connect(connection_string)

            # Create a cursor to execute SQL commands
            cursor = connection.cursor()

            # Check if the table exists, and create it if it doesn't
            table_name = "oxygen_events"
            check_table_query = f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='{table_name}')"
            cursor.execute(check_table_query)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                create_table_query = f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    timestamp_column TIMESTAMP NOT NULL,
                    event_column TEXT NOT NULL
                )
                """
                cursor.execute(create_table_query)
                connection.commit()
                print(f"Table '{table_name}' created successfully.")

            # Define the SQL query to insert the event data into the database table
            insert_query = f"INSERT INTO {table_name} (timestamp_column, event_column) VALUES (%s, %s);"

            # Execute the query with the timestamp and event data
            cursor.execute(insert_query, (timestamp, event))

            # Commit the changes to the database
            connection.commit()

            # Close the cursor and the connection
            cursor.close()
            connection.close()

            print("Event registered in the database.")

        except psycopg2.Error as e:
            print("Error occurred during the database operation:", e)

    def sendActionToHvac(self, date, action, nbTick):
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{nbTick}")
        details = json.loads(r.text)
        self.send_event_to_database(date[:19], details["Response"])
        print(details['Response'])

if __name__ == "__main__":
    main = Main()
    main.start()
