import requests
import json

BASE_URL = 'http://localhost:5000'


def test_get_all_heroes():
    response = requests.get(f'{BASE_URL}/heroes')
    print(f"GET /heroes: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_get_hero_by_id(hero_id):
    response = requests.get(f'{BASE_URL}/heroes/{hero_id}')
    print(f"GET /heroes/{hero_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_create_hero():
    new_hero = {
        "hero_id": 21,
        "hero_name": "Fanny",
        "role": "Assassin"
    }
    response = requests.post(f'{BASE_URL}/heroes', json=new_hero)
    print(f"POST /heroes: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_update_hero(hero_id):
    update_data = {
        "hero_name": "Updated Hero",
        "role": "Fighter"
    }
    response = requests.put(f'{BASE_URL}/heroes/{hero_id}', json=update_data)
    print(f"PUT /heroes/{hero_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_delete_hero(hero_id):
    response = requests.delete(f'{BASE_URL}/heroes/{hero_id}')
    print(f"DELETE /heroes/{hero_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_xml_response():
    headers = {'Accept': 'application/xml'}
    response = requests.get(f'{BASE_URL}/heroes', headers=headers)
    print(f"GET /heroes (XML): {response.status_code}")
    print(response.text)


if __name__ == '__main__':
    print("Testing Heroes REST API\n")
    test_get_all_heroes()
    print("\n" + "="*50 + "\n")
    test_get_hero_by_id(1)
    print("\n" + "="*50 + "\n")
    test_xml_response()
