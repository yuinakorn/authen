import requests


def check_permis(hcode, cid):
    url = f"https://exp.cmhis.org/query/user_authen_cid/{hcode}?cid={cid}"

    response = requests.request("GET", url, headers={}, data={})

    print(response.text)
    data = response.json()
    # position_allow = ["พยาบาล", "นายแพทย์"]
    position_allow = ["นักวิชาการ"]

    # Check if position starts with "พยาบาล" or "นายแพทย์"
    matching_positions = [item for item in data if
                          item["position"] and isinstance(item["position"], str) and item["position"].startswith(
                              tuple(position_allow))]
    result = "1" if len(matching_positions) > 0 else "0"

    return {"position_exists": result}
