import imaplib
import email
import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base directory for saving attachments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACHMENTS_BASE = os.path.join(BASE_DIR, "attachments")

# Function to clear the folder
def clear_folder(path):
    try:
        if os.path.exists(path):
            print(f"Clearing folder: {path}...")
            shutil.rmtree(path)  # Remove the folder and its contents
        os.makedirs(path, exist_ok=True)  # Recreate the folder
        print(f"Folder ready: {path}")
    except Exception as e:
        print(f"Error clearing folder {path}: {e}")

# Function to process a single client
def process_client(client):
    try:
        print(f"Processing client: {client['name']}")

        # Connect to Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("dbsrvalerts@gsl.in", "uysq fnhz waqq pmzi")

        # Select the label for the client
        label = client["label"]
        print(f"Selecting the label '{label}'...")
        status, count = mail.select(label)
        if status != "OK":
            print(f"Error selecting label '{label}'. Skipping...")
            mail.logout()
            return

        print(f"Label selected successfully. Total emails: {count[0].decode()}")

        # Process each subject line for the client
        for subject in client["subjects"]:
            subject_line = subject["subject"]
            folder_path = os.path.join(ATTACHMENTS_BASE, client["name"], subject["folder"])

            # Ensure the folder is ready
            clear_folder(folder_path)

            print(f"Searching for emails with subject containing: {subject_line}")
            status, messages = mail.search(None, f'(ON {datetime.now().strftime("%d-%b-%Y")} SUBJECT "{subject_line}")')
            if status != "OK":
                print(f"Error searching for emails with subject '{subject_line}'. Skipping...")
                continue

            email_ids = messages[0].split()
            print(f"Total matching emails for subject '{subject_line}': {len(email_ids)}")

            # Process only the latest matching email
            if email_ids:
                print("Processing the latest matching email...")
                latest_email_id = email_ids[-1]  # Get the latest email ID
                status, data = mail.fetch(latest_email_id, "(RFC822)")
                if status != "OK":
                    print(f"Error fetching email ID {latest_email_id.decode()}. Skipping...")
                    continue

                # Parse the email
                msg = email.message_from_bytes(data[0][1])
                email_subject = msg["subject"]
                print(f"Email subject: {email_subject}")

                # Save attachments in the appropriate folder
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        filepath = os.path.join(folder_path, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Attachment saved: {filepath}")
            else:
                print(f"No emails found with subject '{subject_line}'.")

        mail.logout()
    except Exception as e:
        print(f"Error processing client {client['name']}: {e}")

# Main function to handle parallel processing
def main():
    print("Starting Gmail sync...")

    # Define the client configurations
    clients = [
    {
        "name": "ARISU",
        "label": "DBA_ARISU",
        "subjects": [
            {"subject": "ARU-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "ARISU", "arc_gap")},
            {"subject": f"ARU-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "ARISU", "arc_apply")}
        ]
    },
    {
        "name": "Bigmart",
        "label": "DBA_Bigmart",
        "subjects": [
            {"subject": "MMT-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "Bigmart", "arc_gap")},
            {"subject": f"MMT-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "Bigmart", "arc_apply")}
        ]
    },
    {
        "name": "CHUNMUN",
        "label": "DBA_Chunmun",
        "subjects": [
            {"subject": "CNM-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "CHUNMUN", "arc_gap")},
            {"subject": f"CNM-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CHUNMUN", "arc_apply")}
        ]
    },
    {
        "name": "CITYKART",
        "label": "DBA_CityKart",
        "subjects": [
            {"subject": "CKT-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "CITYKART", "arc_gap")},
            {"subject": f"CKT-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CITYKART", "arc_apply")}
        ]
    },
    {
        "name": "GURRAM",
        "label": "DBA_Gurram",
        "subjects": [
            {"subject": "GRM-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "GURRAM", "arc_gap")},
            {"subject": f"GRM-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "GURRAM", "arc_apply")}
        ]
    },
    {
        "name": "MAYASHEEL",
        "label": "DBA_Mayasheel",
        "subjects": [
            {"subject": "MYS-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "MAYASHEEL", "arc_gap")},
            {"subject": f"MYS-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MAYASHEEL", "arc_apply")}
        ]
    },
    {
        "name": "MRPL",
        "label": "DBA_MRPL",
        "subjects": [
            {"subject": "MRL-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "MRPL", "arc_gap")},
            {"subject": f"MRL-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MRPL", "arc_apply")}
        ]
    },
    {
        "name": "MUFTI",
        "label": "DBA_Mufti",
        "subjects": [
            {"subject": "MFT-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "MUFTI", "arc_gap")},
            {"subject": f"MFT-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MUFTI", "arc_apply")}
        ]
    },
    {
        "name": "RSBROTHERS",
        "label": "DBA_RSBrothers",
        "subjects": [
            {"subject": "RSB-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "RSBROTHERS", "arc_gap")},
            {"subject": f"RSB-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "RSBROTHERS", "arc_apply")}
        ]
    },
    {
        "name": "SHREE",
        "label": "DBA_Shree",
        "subjects": [
            {"subject": "SHR-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "SHREE", "arc_gap")},
            {"subject": f"SHR-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SHREE", "arc_apply")}
        ]
    },
    {
        "name": "SKECHERS",
        "label": "DBA_Skechers",
        "subjects": [
            {"subject": "SKH-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "SKECHERS", "arc_gap")},
            {"subject": f"SKH-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SKECHERS", "arc_apply")}
        ]
    },
    {
        "name": "SOCH",
        "label": "DBA_Soch",
        "subjects": [
            {"subject": "SCH-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "SOCH", "arc_gap")},
            {"subject": f"SCH-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SOCH", "arc_apply")}
        ]
    },
    {
        "name": "STYLEBAAZAR",
        "label": "DBA_Stylebazar",
        "subjects": [
            {"subject": "STL-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "STYLEBAAZAR", "arc_gap")},
            {"subject": f"STL-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "STYLEBAAZAR", "arc_apply")}
        ]
    },
    {
        "name": "CBMRETAIL",
        "label": "DBA_CBMH",
        "subjects": [
            {"subject": "CBMH-INFO: ARCH APPLIED GAP", "folder": os.path.join(ATTACHMENTS_BASE, "CBMRETAIL", "arc_gap")},
            {"subject": f"CBMH-STANDBY: ARCH APPLIED ON STANDBY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CBMRETAIL", "arc_apply")}
        ]
    },
    {
        "name": "BIBA",
        "label": "DBA_BIBA",
        "subjects": [
            {"subject": "BIBA-INFO: APPLIED ARCH GAP", "folder": os.path.join(ATTACHMENTS_BASE, "BIBA", "arc_gap")}
        ]
    },
    {
        "name": "RANGREETI",
        "label": "DBA_RANGREETI",
        "subjects": [
            {"subject": "BAPL-INFO: APPLIED ARCH GAP", "folder": os.path.join(ATTACHMENTS_BASE, "RANGREETI", "arc_gap")}
        ]
    },
    {
        "name": "VMART",
        "label": "DBA_Vmart",
        "subjects": [
            {"subject": "VMART-STANDBY DR SYNC INFO", "folder": os.path.join(ATTACHMENTS_BASE, "VMART", "arc_gap")}
        ]
    }
]

    # Use ThreadPoolExecutor to process clients in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_client, client): client for client in clients}

        # Wait for all threads to complete and handle exceptions
        for future in as_completed(futures):
            client = futures[future]
            try:
                future.result()  # Retrieve result or handle exceptions if needed
            except Exception as e:
                print(f"Error processing client {client['name']}: {e}")

    print("All clients processed.")

if __name__ == "__main__":
    main()
