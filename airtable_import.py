"""
Copy Kellogg Prof data into an Airtable DB for our Research Support CRM
"""
from csv_professor_sheet import SpreadSheet
from web_util import get_json, get_tree, css_select
import getpass
import requests
import json

def airtable_import():
    # load kellogg prof data
    profs = SpreadSheet().read_profs()
    profs = [p for p in profs if p.school=="Northwestern"]
    # prompt for airtable api key
    airtable_API_key = getpass.getpass("Enter your AirTable API key: ")

    # get iterate through all customers in airtable
    customers = []
    base_url = "https://api.airtable.com/v0/apptzGHIQmdYv9F1i/Customers?view=Grid%%20view&api_key=%s"
    offset = None
    while True:
        if offset:
            base_url += "&offset=" + offset
        response = get_json(base_url % airtable_API_key)
        customers.extend(response["records"])
        if "offset" not in response:
            break
        offset = response["offset"]

    for customer in customers:
        if "Professor" in customer["fields"]["Role"]:
            print("found professor: " + customer["fields"]["Full Name"])
            netId = customer["fields"]["NetId"]
            matching_profs = [p for p in profs if netId in p.faculty_directory_url]
            if len(matching_profs) == 0:
                print("WARNING: not present in Google Sheets")
                continue
            prof = matching_profs[0]
            # update the professor's airtable record
            update_body = {
                "fields": {
                    "Directory URL": prof.faculty_directory_url
                }
            }
            photo_url = get_photo_url(prof)
            if photo_url:
                update_body["fields"]["Photo"] = [{
                    "url": get_photo_url(prof),
                    "filename": netId + "_headshot.jpg"
                }]
            if prof.google_scholar_url:
                update_body["fields"]["Scholar URL"] = prof.google_scholar_url
            if prof.cv_url:
                update_body["fields"]["CV"]: [{
                    "url": prof.cv_url,
                }]
            r = requests.patch("https://api.airtable.com/v0/apptzGHIQmdYv9F1i/Customers/" + customer["id"],
                               data=json.dumps(update_body),
                               headers={"Content-type": "application/json",
                                        "Authorization": "Bearer " + airtable_API_key})
            if r.status_code != 200:
                print("ERROR: response code %d" % r.status_code)
                print(r.text)


def get_photo_url(prof):
    img_tags = css_select(get_tree(prof.faculty_directory_url), "img.profileImg")
    if len(img_tags) == 0:
        return None
    return "https://www.kellogg.northwestern.edu" + img_tags[0].get("src")


if __name__ == '__main__':
    airtable_import()