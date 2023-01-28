import io
import requests
from PIL import Image
from requests_html import HTMLSession


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
def create_segmented_html_block(start_key, text):
    start_key -= 2
    counter_key = start_key
    bracket_val = -1

    while bracket_val != 0:
        counter_key += 1
        if text[counter_key] == "{":
            bracket_val -= 1
        elif text[counter_key] == "}":
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


def find_alt_text(alt_key, block):
    start_index = block.find(alt_key) + 13
    counter = start_index
    while block[counter] != "]":
        counter += 1
    return block[start_index:counter-1]


def find_pertinent_data(search_term):
    # The keys within the html
    image_key = "444383007"
    alt_text_key = "2008"

    # the requested resultant html script
    html_text = create_master_html(search_term)

    # The list of the locations of the key within the html script
    image_key_list = [m.start() for m in re.finditer(image_key, html_text)]

    block_list = []
    for image_key in image_key_list:
        block = create_segmented_html_block(image_key, html_text)
        if alt_text_key in block:
            block_list.append(block)

    r_dict = {}
    for num, block in enumerate(block_list):
        link, h, w = find_link_h_w_in_block(block)
        alt_text = find_alt_text(alt_text_key, block)

        r_dict[search_term + str(num)] = {"image_link": link, "height": int(h), "width": int(w), "alt_text": alt_text}

    return r_dict