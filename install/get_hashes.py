

import requests

# Replace with your GitHub repository details
owner = 'JepEtau'
repo = 'external_rehost'
release_tag = 'external'

# URL for the release API
release_url = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{release_tag}'

response = requests.get(release_url)

if response.status_code == 200:
    release_data = response.json()
    assets = release_data.get('assets', [])
    for asset in assets:
        asset_name = asset['name']
        download_url = asset['browser_download_url']

        # Make a HEAD request to the asset URL to get the ETag (file hash)
        asset_response = requests.head(download_url)

        if 'etag' in asset_response.headers:
            etag = asset_response.headers['etag']
            print(f"Asset: {asset_name}, ETag (hash): {etag}")
        else:
            print(f"No ETag found for asset: {asset_name}")
else:
    print(f"Error fetching release data: {response.status_code}")

