import json
import re

def process_item(item):
    # Extract price from name if price is missing
    price_match = re.search(r'\d{1,3}(?:,\s?\d{1,2}|\s?[€e])', item['name'])
    if price_match and item.get('price') == "U":
        item['price'] = price_match.group(0).replace('€', '').replace('e', '').strip()
        item['name'] = item['name'].replace(price_match.group(0), '').strip()

    if item.get('price'):
        item['price'] = item['price'].replace('€', '').replace('e', '').strip()
    
    # Clean non-printing characters
    item['name'] = re.sub(r'[\x00-\x1F\x7F-\x9F]+', ' ', item['name'])
    item['info'] = re.sub(r'[\x00-\x1F\x7F-\x9F]+', ' ', item['info'])

    # Extract allergens from name and info
    allergen_pattern = r'\b(?:L|M|G|V|VE|GL|VEG|VL|K|P|VS)\b'
    allergens_name = re.findall(allergen_pattern, item['name'], flags=re.IGNORECASE)
    allergens_info = re.findall(allergen_pattern, item['info'], flags=re.IGNORECASE)
    
    allergens = list(set([allergen.upper() for allergen in allergens_info + allergens_name]))
    
    item['name'] = re.sub(allergen_pattern, '', item['name'], flags=re.IGNORECASE)
    item['info'] = re.sub(allergen_pattern, '', item['info'], flags=re.IGNORECASE)

    if allergens:
        item['allergens'] = allergens
    else:
        item['allergens'] = []

    # Clean name and info from unnecessary characters and whitespaces
    def clean_text(text):
        if text == 'U':
            return text
        text = re.sub(r'\s\|\s', ' tai ', text)
        text = re.sub(r'[^a-zA-ZäöåÄÖÅ\s]', '', text)
        text = re.sub(r'\b[a-zA-ZäöåÄÖÅ],?\b', '', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    item['name'] = clean_text(item['name'])
    item['info'] = clean_text(item['info'])

    return item

def write_processed_json():
    # Load data
    with open('menu_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Process data
    for restaurant, menu in data.items():
        data[restaurant] = [process_item(item) for item in menu]

    # Save processed data
    with open('menu_data_processed.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Succesfully wrote processed data to file")

# if __name__ == "__main__":
#     write_processed_json()