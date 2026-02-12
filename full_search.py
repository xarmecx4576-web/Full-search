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



if __name__ == '__main__':
    main()
