import requests


def get_ibb_metro_datasets():
    url = "https://data.ibb.gov.tr/api/3/action/package_search?q=metro"
    response = requests.get(url, timeout=(5, 20))
    response.raise_for_status()
    packages = response.json()["result"]["results"]

    metro_lines = []
    for package in packages:
        for resource in package.get("resources", []):
            if resource.get("format", "").lower() in ("json", "geojson"):
                metro_lines.append(
                    {
                        "name": package.get("title", "İsimsiz veri"),
                        "url": resource["url"],
                    }
                )

    return metro_lines


if __name__ == "__main__":
    try:
        for line in get_ibb_metro_datasets():
            print(f"{line['name']}: {line['url']}")
    except requests.exceptions.RequestException as error:
        print(f"İBB verisi alınamadı: {error}")