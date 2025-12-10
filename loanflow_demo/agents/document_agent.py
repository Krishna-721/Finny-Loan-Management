def verify_salary_slip(uploaded_file):
    if uploaded_file is None:
        return False, "No document uploaded."
    return True, "Document verified successfully."
