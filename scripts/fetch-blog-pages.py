import os
import requests
import csv

squarespace_root_site = os.getenv('SQUARESPACE_ROOT_SITE')
squarespace_blog_id = os.getenv('SQUARESPACE_BLOG_ID')
squarespace_cookie_header = os.getenv('SQUARESPACE_COOKIE_HEADER')

page_length = os.getenv('SQUARESPACE_PAGE_LENGTH', 20)

if not squarespace_root_site or not squarespace_blog_id or not squarespace_cookie_header:
    print("INVALID CONFIGURATION")
    exit(1)

url_without_pagination = f"https://{squarespace_root_site}/api/content/blogs/{squarespace_blog_id}/posts?limit={page_length}&fields=title,id,recordType,tags,categories"

headers = {'cookie': squarespace_cookie_header}

pages_mapping = []

url = url_without_pagination

print("Starting fetching information from Squarespace")

while True:
    squarespace_response = requests.get(url, headers=headers)

    if squarespace_response.status_code != 200:
        print(f"Unable to communicate with squarespace :(\nStatus Code:{squarespace_response.status_code}")
        break

    squarespace_response_as_json = squarespace_response.json()

    for result in squarespace_response_as_json.get('results'):
        page_obj = {
            'id': result.get('id'),
            'title': result.get('title'),
            'tags': result.get('tags'),
            'categories': result.get('categories'),
        }

        pages_mapping.append(page_obj)

    if not squarespace_response_as_json.get('hasNextPage'):
        break

    next_page_start = squarespace_response_as_json.get('nextPageStart')

    url_with_pagination = f"{url_without_pagination}&start={next_page_start}"
    url = url_with_pagination


print(f"Successfully fetched information from {len(pages_mapping)} pages")

print('Writing to output file')
with open('/app/output/blog_pages_with_tags_and_categories.csv', 'w', newline='') as csvfile:
    fieldnames = ['id', 'title', 'tags', 'categories']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for mapped_page in pages_mapping:
        writer.writerow(mapped_page)

print('Successfully finished writing to output file')
