import requests
import os
import json

from time import sleep

class XIVApiNotFoundException(Exception):
    pass

class XIVApiWrapper:
    BASE_URL = "https://xivapi.com"
    ENDPOINTS = {
        "classjob": "/classjob",
        "search": "/search",
        "classjobcategory": "/classjobcategory"
    }
    REQUEST_PER_SECOND = 20

    try:
        API_KEY = os.environ['XIV_API_KEY']
    except KeyError:
        print("environment variable XIV_API_KEY undefined, please define it.")
        exit()

    def _retrieve_all_from_search_request(request):
        number_retrieved = 0
        results = []

        results_total = float("inf")
        request_count = 0
        while number_retrieved < results_total:
            if request_count == XIVApiWrapper.REQUEST_PER_SECOND:
                sleep(1)
                request_count = 0
            request_result = request(number_retrieved)
            request_count += 1
            pagination = request_result['Pagination']
            number_retrieved += pagination['Results']
            results_total = pagination['ResultsTotal']
            results.extend(request_result['Results'])
        return results

    def _post_search_request(indexes, columns, filters):
        def request(from_position):
            data = {
                "private_key": XIVApiWrapper.API_KEY,
                "indexes": ",".join(indexes),
                "columns": ",".join(columns),
                "body": {
                    "query": {
                        "bool": {
                            "filter": filters
                        }
                    },
                    "from": from_position,
                    "size": 100,
                },
            }

            search_url = XIVApiWrapper.compute_url(
                           XIVApiWrapper.ENDPOINTS['search']
                         )

            return requests.post(search_url, json=data).json()
        return request

    def compute_url(endpoint):
        return "{}{}".format(XIVApiWrapper.BASE_URL, endpoint)

    def get_all_actions():
        indexes=("Action",)
        columns=(
            "ID",
            "Name_de",
            "Name_en",
            "Name_fr",
            "Name_ja",
        )

        return XIVApiWrapper._retrieve_all_from_search_request(
            XIVApiWrapper._post_search_request(
                indexes,
                columns,
                {}
            )
        )


if __name__ == "__main__":
    DEFAULT_ACTION_LIST_FILENAME = "actions_list.json"
    DEFAULT_ACTION_NAMES_DICT_FILENAME = "action_names_dict.json"

    print("retrieving every actions...")
    actions_list = XIVApiWrapper.get_all_actions()
    
    print("actions retrieved, now creating json files...")
    action_names_dict = {}
    for index, action in enumerate(actions_list):
        action_names_dict[action['Name_de']] = index
        action_names_dict[action['Name_en']] = index
        action_names_dict[action['Name_fr']] = index
        action_names_dict[action['Name_ja']] = index

    with open(DEFAULT_ACTION_LIST_FILENAME, mode="w") as file:
        json.dump(actions_list, file)

    with open(DEFAULT_ACTION_NAMES_DICT_FILENAME, mode="w") as file:
        json.dump(action_names_dict, file)