import json
import os
import requests
from dotenv import load_dotenv
from geopy import distance
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def read_json(path):
    with open(path, "r", encoding="CP1251") as file:
        return json.loads(file.read())


def get_coffee(coffee_shops, coords):
    struct = list()
    for shop in coffee_shops:
        dist = distance.distance(coords, [shop["Latitude_WGS84"], shop["Longitude_WGS84"]]).km
        struct.append({"distance": dist,
                       "latitude": shop["Latitude_WGS84"],
                       "longitude": shop["Longitude_WGS84"],
                       "name": shop["Name"]
                       })

    return struct


def get_dist_coffee(shop):
    return shop["distance"]


def create_map(map, coords, coffee_shops):
    folium.Marker(
        location=coords,
        tooltip="Вы тут)",
        popup="Да да, вы тут))",
        icon=folium.Icon(color="red"),
    ).add_to(map)

    for shop in coffee_shops:
        folium.Marker(
            location=[shop["latitude"], shop["longitude"]],
            tooltip=shop["name"],
            popup=f"По прямой {shop["distance"]}км",
            icon=folium.Icon(color="blue"),
        ).add_to(map)


def main():
    load_dotenv()
    apikey = os.environ["API_MAP"]

    my_place = input("Где вы примерно?")
    coords = fetch_coordinates(apikey, my_place)
    coords = list(coords)
    coords[0], coords[1] = coords[1], coords[0]

    coffee_shops = read_json("coffee.json")
    coffee_shops = get_coffee(coffee_shops, coords)
    coffee_shops.sort(key=get_dist_coffee)

    map = folium.Map(coords)
    create_map(map, coords, coffee_shops[:5])
    map.save("index.html")


if __name__ == '__main__':
    main()