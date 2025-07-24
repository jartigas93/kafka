import requests
import datetime
import time
import os
from quixstreams import Application
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class OpenSkyClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = 'https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token'
        self.access_token = None
        self.token_expiration = None

    def get_app(self):
        app = Application(broker_address=os.getenv("KAFKA_BROKER"),
                 loglevel="DEBUG",
                 )

        return app

    def get_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        r = requests.post(self.token_url, headers=headers, data=data)
        if r.ok:
            t = r.json()
            self.access_token = t['access_token']
            expires_in = t.get('expires_in', 1800)

            self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in - 30)
            print(f"[TOKEN] valido hasta {self.token_expiration}")
        else:
            raise Exception(f"Error token: {r.status_code} {r.text}")

    def ensure_token(self):
        if self.access_token is None or datetime.datetime.utcnow() >= self.token_expiration:
            self.get_token()

    def get_states(self):
        self.ensure_token()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        r = requests.get(
            "https://opensky-network.org/api/states/all",
            headers=headers,
        )

        # Si nos devuelve 401 intentamos renovar y reintentar una vez
        if r.status_code == 401:
            print("[API] Token expirado. Renovando…")
            self.get_token()
            return self.get_states()
        r.raise_for_status()
        return r.json().get('states', [])
    
def main():
    client = OpenSkyClient(
        client_id = os.getenv('CLIENT_ID'),
        client_secret = os.getenv('CLIENT_SECRET')
    )

    kafka_app = client.get_app()

    with kafka_app.get_producer() as producer:

        while True:
            try:
                states = client.get_states()
                if states:

                    for s in states:
                        msg = {
                            'icao24':   s[0],
                            'callsign': s[1].strip() if s[1] else None,
                            'lat':      s[6],
                            'lon':      s[5],
                            'alt_geo':  s[13],
                            'on_ground':s[8],
                            'time':     s[3]
                        }

                        producer.produce(
                        topic="aircrafts_states",
                        value=json.dumps(msg).encode("utf-8"),
                        )
                else:
                    print("No se han detectado vuelos. Reintentando en 15s… ")
                    time.sleep(15)

            except Exception as e:
                print("¡Error!", e)
            time.sleep(30)


if __name__ == "__main__":
    main()