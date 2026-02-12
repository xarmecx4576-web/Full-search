// geocode_function.py

import requests

API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'


def geocode(address):
    geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json'
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    features = json_response['response']['GeoObjectCollection']['featureMember']
    return features[0]['GeoObject'] if features else None


def coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()
    return float(toponym_longitude), float(toponym_lattitude)

def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()

    ll = ','.join([toponym_longitude, toponym_lattitude])
    envelope = toponym['boundeBy']['Envelope']

    l, b = envelope['lowerCorner'].split(" ")
    r, t = envelope['upperCorner'].split(" ")

    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    span = f'{dx},{dy}'

    return ll,span


//map_api_show.py

import arcade
import requests
import sys
import os

API_KEY_STATIC = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'MAP'
MAP_FILE = 'map.png'


class GameView(arcade.Window):
    def __init__(self, width, height, title, ll_spn=None, add_params=None):
        super().__init__(width, height, title)
        self.ll_spn = ll_spn
        self.add_params = add_params
        self.background = None

    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                (self.width - self.background.width) // 2,
                (self.height - self.background.height) // 2,
                self.background.width,
                self.background.height),
        )

    def get_image(self):
        if self.ll_spn:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&{self.ll_spn}"
        else:
            map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&"

        if self.add_params:
            map_request += '&' + self.add_params
        response = requests.get(map_request)

        if not response:
            print('Ошибка выполнения запроса:')
            print(map_request)
            print('Http статус:', response.status_code, '(', response.reason, ')')
            sys.exit(1)

        try:
            with open(MAP_FILE, 'wb') as file:
                file.write(response.content)
        except IOError as ex:
            print('Ошибка записи временного файла:', ex)

        self.background = arcade.load_texture(MAP_FILE)



def show_map(ll_spn=None, add_params=None):
    main(ll_spn, add_params)

def main(ll_spn=None, add_params=None):
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, ll_spn, add_params)
    gameview.setup()
    arcade.run()
    os.remove(MAP_FILE)

if __name__ == '__main__':
    show_map('ll=37.530887,55.703118&spn=0.002,0.002')


// full_search.py

import sys

from geocode_function import coordinates, geocode, get_ll_span
from map_api_show import show_map


def main():
    toponym_to_find = " ".join(sys.argv[1:])

    if toponym_to_find:
        lat, lon = coordinates(toponym_to_find)
        ll_spn = f'll={lat},{lon}&spn=0.005,0.005'
        show_map(ll_spn)

        ll, spn = get_ll_span(toponym_to_find)
        ll_spn = f'll={ll}&spn={spn}'
        show_map(ll_spn)

        point_param = f'pt={ll}'
        show_map(ll_spn, add_params=point_param)
    else:
        print('No data')
