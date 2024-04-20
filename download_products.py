import requests
import re

class ProductNotReadyException(Exception):
    pass

def find_latest_products_from_prod_url(prod_url : str):

    if not prod_url.endswith("/"):
        prod_url = prod_url + "/"

    available_days = prod_url
    available_days_text = requests.get(available_days).text
    available_days_matched = [r.replace("\"",'') for r in re.findall(r'\"gfs.\d+\/\"', available_days_text)]
    available_days_matched_reversed = list(reversed(available_days_matched))

    for available_day_matched_reversed in available_days_matched_reversed:
        day_prod_url = f"{prod_url}{available_day_matched_reversed}"
        day_prod_url_txt = requests.get(day_prod_url).text
        hours_in_day = [r.replace('>','') for r in re.findall(r'>\d+', day_prod_url_txt)]

        for hour_in_day in hours_in_day:
            prod_at_hour_in_day_url = day_prod_url + hour_in_day + "/atmos/"
            prod_at_hour_in_day = requests.get(prod_at_hour_in_day_url).text
            finds = [f.replace('\"','') for f in re.findall(r'\"gfs\.t\d+z\.pgrb2\.1p00\.f\d+\"', prod_at_hour_in_day)]

            if len(finds) == 129:
                return [day_prod_url + hour_in_day + f"/atmos/{f}" for f in finds]
            else:
                raise ProductNotReadyException()
            
    return None

base_url ="/mnt/noaa/DATA/"
products_to_download = find_latest_products_from_prod_url("https://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod")
for product_to_download in products_to_download:
    file_name = product_to_download[product_to_download.rindex('/')+1:]
    destination_file_path = base_url + file_name
    print(f"Downloading {product_to_download} to {destination_file_path}")
    response = requests.get(product_to_download)
    with open(destination_file_path, mode="wb") as fout:
        fout.write(response.content)
    



