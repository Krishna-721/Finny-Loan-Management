# Simulated PAN database (KYC + credit info)

MOCK_PAN_DB = {
    "ABCDE1234F": {
        "name": "Rohit Sharma",
        "credit_score": 780,
        "existing_emi": 5000,
        "preapproved_limit": 400000
    },
    "XYZAB1234C": {
        "name": "Anita Kapoor",
        "credit_score": 640,
        "existing_emi": 10000,
        "preapproved_limit": 120000
    },
    "LMNOP5678D": {
        "name": "Vikram Singh",
        "credit_score": 720,
        "existing_emi": 7000,
        "preapproved_limit": 300000
    },
    "QWERT4321Z": {
        "name": "Sneha Patel",
        "credit_score": 680,
        "existing_emi": 8000,
        "preapproved_limit": 250000
    },
    "PQRST9876Y": {
        "name": "Amit Joshi",
        "credit_score": 590,
        "existing_emi": 12000,
        "preapproved_limit": 100000
    }

}

def fetch_pan_details(pan):
    pan = pan.upper().strip()
    return MOCK_PAN_DB.get(pan)
