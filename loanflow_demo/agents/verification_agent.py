from core.mock_bureau import fetch_pan_details

def verify_pan(pan):
    result = fetch_pan_details(pan)
    if not result:
        return None, "PAN not found in system."

    return result, None
