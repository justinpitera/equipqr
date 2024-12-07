import requests

# API endpoint
url = "https://0.0.0.0:7878/api/gse/issues/submit"

# Data for the request
payload = {
    "gse_id": "GSE12345",
    "is_operable": True,
    "issue_description": "This is a test issue with an image and a video.",
}

# Files to upload
files = {
    "attachments": [
        ("attachments", ("image.png", open("image.png", "rb"), "image/png")),
        ("attachments", ("video.mp4", open("video.mp4", "rb"), "video/mp4")),
    ]
}

# SSL verification (skip for testing only)
verify_ssl = False

try:
    # Send POST request
    response = requests.post(
        url,
        data={
            "gse_id": payload["gse_id"],
            "is_operable": str(payload["is_operable"]),  # Convert boolean to string
            "issue_description": payload["issue_description"],
        },
        files=files["attachments"],
        verify=verify_ssl,
    )

    # Print response details
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("An error occurred:", e)
finally:
    # Close all file streams to prevent resource leaks
    for _, file_obj, _ in files["attachments"]:
        file_obj.close()
