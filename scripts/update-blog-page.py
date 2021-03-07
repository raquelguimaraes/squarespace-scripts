import os
import requests
import csv

squarespace_root_site = os.getenv('SQUARESPACE_ROOT_SITE')
squarespace_blog_id = os.getenv('SQUARESPACE_BLOG_ID')
squarespace_blog_post_id = os.getenv('SQUARESPACE_BLOG_POST_ID')
squarespace_cookie_header = os.getenv('SQUARESPACE_COOKIE_HEADER')

update_mode = os.getenv('UPDATE_MODE', 'APPEND')
tags_to_update = os.getenv('TAGS_TO_UPDATE', '')
categories_to_update = os.getenv('CATEGORIES_TO_UPDATE', '')

if not squarespace_root_site or not squarespace_blog_id or not squarespace_cookie_header or not squarespace_blog_post_id or update_mode not in ['APPEND', 'OVERRIDE']:
    print("INVALID CONFIGURATION")
    exit(1)

crumbs_token = [token for token in squarespace_cookie_header.split(';') if token.startswith(' crumb=')]
if len(crumbs_token) != 1:
    print("INVALID COOKIE CONFIGURATION")
    exit(1)

csrf_token = crumbs_token[0].split('=')[1]

url = f"https://{squarespace_root_site}/api/content/blogs/{squarespace_blog_id}/text-posts/{squarespace_blog_post_id}"

headers = {
    'cookie': squarespace_cookie_header,
    'x-csrf-token': csrf_token,
}

squarespace_get_response = requests.get(url, headers=headers)

blog_entry = squarespace_get_response.json()

if squarespace_get_response.status_code != 200:
    print(f"Unable to communicate with squarespace to get blog post information :(\nStatus Code:{squarespace_get_response.status_code}")
else:
    print('Successfully fetch blog post information from squarespace')

if update_mode == 'OVERRIDE':
    blog_entry['tags'] = tags_to_update.split(',')
    blog_entry['categories'] = categories_to_update.split(',')
else:
    final_tags = set(blog_entry['tags'] + tags_to_update.split(','))
    final_categories = set(blog_entry['categories'] + categories_to_update.split(','))
    blog_entry['tags'] = list(final_tags)
    blog_entry['categories'] = list(final_categories)

squarespace_put_response = requests.put(url, json=blog_entry, headers=headers)

if squarespace_put_response.status_code == 200 and 'error' not in squarespace_put_response.json():
    print('Successfully updated blog post information from squarespace')
else:
    print(f"Unable to communicate with squarespace to update blog post information :(\nResponse Result: {squarespace_put_response.json()}")
