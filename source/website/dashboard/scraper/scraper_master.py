import io
import math

import requests
from PIL import Image
from requests_html import HTMLSession
import re
import openai


def construct_search_url(search_term):
    return "https://www.google.com/search?tbm=isch&q=" + search_term


def create_master_html(search_term):
    # The url to the main search page
    search_url = construct_search_url(search_term)

    # The requests html for main search page
    session = HTMLSession()
    result = session.get(search_url)

    # The resultant string does in fact contain full res image files
    return result.html.html


def get_origin_html(origin_link):
    session = HTMLSession()
    try:
        result = session.get(origin_link)
    except:
        print(origin_link)

    return result.html.html
    # return requests.get(origin_link).text


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


# Create a block of text that is a segment of the full html file that contains the data for a single image
def create_segmented_html_block(start_key, text, start_sentinel="{", end_sentinel="}", start_mod=2):
    start_key -= start_mod
    counter_key = start_key
    bracket_val = -1

    while bracket_val != 0:
        counter_key += 1
        if text[counter_key] == start_sentinel:
            bracket_val -= 1
        elif text[counter_key] == end_sentinel:
            bracket_val += 1

    return text[start_key:counter_key+1]


def find_link_h_w_in_block(block):
    left_bracket_counter = 0
    counter = 0
    while left_bracket_counter < 4:
        if block[counter] == "[":
            left_bracket_counter += 1
        counter += 1

    link_h_w = block[counter + 1: counter + block[counter:].find("]")].split(",")
    if len(link_h_w) > 3:
        link = "".join(link_h_w[:-2])
        h, w = link_h_w[-2], link_h_w[-1]
        link_h_w = [link, h, w]

    link_h_w[0] = link_h_w[0][:-1]
    return link_h_w


def find_alt_text(html_block, alt_key="2008", key_len=13):
    start_index = html_block.find(alt_key) + key_len
    counter = start_index
    while html_block[counter] != "]":
        counter += 1
    return html_block[start_index:counter-1]


def find_origin_alt_text_tag(image_link, origin_link):
    origin_html = get_origin_html(origin_link)

    image_link_locations = [m.start() for m in re.finditer(image_link, origin_html)]
    alt_tag_locations = [m.start() for m in re.finditer("alt=\"", origin_html)] + \
                        [m.start() for m in re.finditer("imageAlt=\"", origin_html)]
    non_html_alt_tag = [m.start() for m in re.finditer("altText\":\"", origin_html)]

    if len(image_link_locations) == 0 or len(alt_tag_locations) == 0:
        return "FAILURE"

    alt_text_collection = {}
    for alt_tag in alt_tag_locations:
        r_str = ""
        quote_counter = 0
        counter = alt_tag
        while quote_counter != 2:
            if origin_html[counter] == "\"":
                quote_counter += 1
            if quote_counter == 1:
                r_str += origin_html[counter]
            counter += 1

        if len(r_str[1:]) > 0:
            alt_text_collection[alt_tag] = r_str[1:]

    for alt_tag in non_html_alt_tag:
        r_str = ""
        quote_counter = 0
        counter = alt_tag
        while quote_counter != 3:
            if origin_html[counter] == "\"":
                quote_counter += 1
            if quote_counter == 2:
                r_str += origin_html[counter]
            counter += 1
        if len(r_str[1:]) > 0:
            alt_text_collection[alt_tag] = r_str[1:]

    try:
        closest_list = [(alt_text_collection[find_closest(link_loc, alt_text_collection.keys())], abs(find_closest(link_loc, alt_text_collection.keys()) - link_loc))
                    for link_loc in image_link_locations]
    except KeyError:
        return "FAILURE"
    # print("closest:", closest_list)
    closest_list = sorted(closest_list, key=lambda x: x[1])
    print("closest:", closest_list)
    print("answer:", closest_list[0][0])
    print("image_link_locations:", image_link_locations)
    print("alt_text_collection:", alt_text_collection)
    print(origin_html)
    print()

    return closest_list[0][0]



def find_origin_link(html_block, origin_key="2003"):
    print(find_alt_text(html_block, origin_key, 12).split(",")[1])
    return find_alt_text(html_block, origin_key, 12).split(",")[1][1:-1]


def generate_block_list(search_term, image_key="444383007", alt_text_key="2008", site_origin_key="2003"):
    # the requested resultant html script
    html_text = create_master_html(search_term)

    # The list of the locations of the key within the html script
    image_key_list = [m.start() for m in re.finditer(image_key, html_text)]

    block_list = []
    for image_key in image_key_list:
        block = create_segmented_html_block(image_key, html_text)
        if alt_text_key in block and site_origin_key in block:
            block_list.append(block)

    return block_list


def find_pertinent_data(search_term, super_search):
    block_list = generate_block_list(search_term)

    r_dict = {}
    for num, block in enumerate(block_list):
        link, h, w = find_link_h_w_in_block(block)
        alt_text = find_alt_text(block)
        origin_link = find_origin_link(block)

        if origin_link[:4] != "http":
            continue

        origin_alt_text = find_origin_alt_text_tag(link, origin_link)
        print(origin_alt_text)
        print(link)
        if origin_alt_text == "FAILURE":
            continue

        r_dict[search_term + str(num)] = {"image_link": link, "height": int(h),
                                          "width": int(w), "alt_text": alt_text,
                                          "super_search": super_search,
                                          "origin_link": origin_link,
                                          "origin_alt_text": origin_alt_text}

        # input()

    return r_dict


def chat_gpt_subcategory_generation(super_search, sub_cat_count=10):
    API_KEY_darturi = "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"

    # Load API key
    openai.api_key = API_KEY_darturi

    response = openai.Completion.create(model="text-davinci-003",
                                        prompt="Return a list of the " + str(sub_cat_count) + " most common types of " + super_search + " separated by commas. If there is no suitable answer return \"Error\"",
                                        temperature=0, max_tokens=100)

    if response == "Error":
        return "Error"
    return response["choices"][0]["text"].strip().split(",")


def fetch_alt_text_slice(origin_html, start_index):
    quote_count = 0
    counter = start_index
    alt_text = ""
    while quote_count < 3:
        if origin_html[counter] == "\"":
            quote_count += 1
        if quote_count == 2:
            alt_text += origin_html[counter]
        counter += 1
    return alt_text[1:]


def find_closest(target_num, num_list):
    closest_num = math.inf
    for num in num_list:
        if abs(target_num - num) < abs(target_num - closest_num):
            closest_num = num
    return closest_num


# block = generate_block_list("Cats")[0]
# print(find_origin_link(block))
master_dict = find_pertinent_data("Cats", "Dogs")
print("length:", len(master_dict))
print(master_dict)
origin1 = master_dict["Cats0"]["origin_link"]
image_link1 = master_dict["Cats0"]["image_link"]
# origin_html_block = get_origin_html(origin1)

"""origin_alt_text_block_segment_generation(image_link1, origin_html_block)"""

# get_origin_alt_text(origin1, image_link1)

print()




