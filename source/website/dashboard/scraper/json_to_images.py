import requests
import io
from PIL import Image
import json
import os


def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = download_path + "/" + file_name

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print("SUCCESS")
    except Exception as e:
        print("FAILED -", e)


with open("sample3.json", 'r') as f:
    json_data = json.load(f)

    category_list = set([json_data[key]["super_search"] for key in json_data])
    category_dict = {}
    for category in category_list:
        category_dict[category] = 0

    if not os.path.exists("database_results"):
        os.mkdir("database_results")
    path_to_dir = os.path.realpath("database_results")

    for key in json_data:
        current_image_data = json_data[key]
        download_image(path_to_dir, current_image_data["image_link"], current_image_data["super_search"] +
                       "_" + str(category_dict[current_image_data["super_search"]]))
        category_dict[current_image_data["super_search"]] += 1



    print(category_dict)
    print(json_data)


