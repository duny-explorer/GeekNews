from math import cos, pi
import requests
import sys
from distance import lonlat_distance


def coordinates(data):
    try:
        answer = requests.get(
            "https://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format("+".join(data)))

        if answer:
            json_answer = answer.json()
            pos = json_answer["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            return [float(i) for i in pos.split()]
        else:
            print("Ошибка выполнения запроса")
            print("Http статус:", answer.status_code, "(", answer.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")
        sys.exit(1)


def f(x):
    return (R + x) ** 2 - (((R + 525) ** 2 +
                            (R + x) ** 2 - 2 * cos(180 * L / (pi * R)) * (R + x) * (R + 525)) ** 0.5 - d) ** 2 \
           - (R + 525) ** 2 + d ** 2  # Когда сокращала, лучше не выглядело


R = 6371000
coord1 = (37.611704, 55.819721)
coord2 = coordinates(sys.argv[1:])
d = 3600 * 525 ** 0.5
l_max = (d ** 2 - 525 ** 2) ** 0.5
L = lonlat_distance(coord1, coord2)
print(L, l_max)
if L <= l_max:
    print(0)
else:
    res = 0

    while True:
        print(f(res), f(res + 0.02))
        if res > 1000:
            print("Вряд ли антенна больше 1 км существует")
            break
        elif f(res) * f(res + 0.02) < 0:
            print(res, 123)
            print("Высота антенны:", res + 0.01)
            break

        res += 0.02
