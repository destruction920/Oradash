import imaplib
import email
import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Function to clear the folder
def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove the folder and its contents
    os.makedirs(path, exist_ok=True)  # Recreate the folder

# Function to search for emails with specific subjects and download the latest attachment
def search_and_download(mail, label, subject_variants, save_path):
    try:
        print(f"Selecting the label '{label}'...")
        status, count = mail.select(label)
        if status != "OK":
            print(f"Error selecting label '{label}'. Skipping...")
            return

        print(f"Label selected successfully. Total emails: {count[0].decode()}")
        today_imap = datetime.now().strftime("%d-%b-%Y")  # e.g., 03-Dec-2024

        for subject_line in subject_variants:
            print(f"Searching for emails with subject: {subject_line}")
            status, messages = mail.search(None, f'(ON {today_imap} SUBJECT "{subject_line}")')

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
                    return

                # Parse the email
                msg = email.message_from_bytes(data[0][1])
                print(f"Email subject: {msg['subject']}")
                print(f"Email date: {msg['date']}")

                # Save attachments in the appropriate folder
                attachment_found = False
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        filepath = os.path.join(save_path, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Attachment saved: {filepath}")
                        attachment_found = True
                if not attachment_found:
                    print(f"No attachments found in email with subject: {msg['subject']}")
            else:
                print(f"No emails found with subject '{subject_line}' for today's date.")
    except Exception as e:
        print(f"Error processing label '{label}': {e}")

# Function to process a single client
def process_client(client):
    try:
        print(f"Processing client: {client['name']}")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("dbsrvalerts@gsl.in", "uysq fnhz waqq pmzi")

        for subject in client["subjects"]:
            # Clear the folder before downloading new files
            clear_folder(subject["folder"])
            # Search and download the emails for the subject
            search_and_download(mail, client["label"], subject["subject_variants"], subject["folder"])

        mail.logout()
        print(f"Completed processing client: {client['name']}")
    except Exception as e:
        print(f"Error processing client '{client['name']}': {e}")

# Main function to run all clients in parallel
def main():
    # Dynamically determine the base directory for attachments
    base_directory = os.path.dirname(os.path.abspath(__file__))
    attachments_base = os.path.join(base_directory, "attachments")

    clients = [
    {
        "name": "ARISU",
        "label": "DBA_ARISU",
        "subjects": [
            {
                "subject_variants": [
                    f"ARU-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "ARISU", "tablespace"),
            },
            {
                "subject_variants": ["ARU-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "ARISU", "rman"),
            },
        ],
    },
    {
        "name": "CHUNMUN",
        "label": "DBA_Chunmun",
        "subjects": [
            {
                "subject_variants": [
                    f"CHUNMUN-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "CHUNMUN", "tablespace"),
            },
            {
                "subject_variants": ["CNM-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "CHUNMUN", "rman"),
            },
        ],
    },
    {
        "name": "CITYKART",
        "label": "DBA_CityKart",
        "subjects": [
            {
                "subject_variants": [
                    f"CITYKART-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "CITYKART", "tablespace"),
            },
            {
                "subject_variants": ["CKT-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "CITYKART", "rman"),
            },
        ],
    },
    {
        "name": "BIGMART",
        "label": "DBA_Bigmart",
        "subjects": [
            {
                "subject_variants": [
                    f"MMT-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "BIGMART", "tablespace"),
            },
            {
                "subject_variants": ["MMT-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "BIGMART", "rman"),
            },
        ],
    },
    {
        "name": "RSBROTHERS",
        "label": "DBA_RSBrothers",
        "subjects": [
            {
                "subject_variants": [
                    "RSB-INFO: PROD DB UNCOMP RMAN BACKUP COMPLETE",
                    "RSB-INFO: PROD DB COMP RMAN BACKUP COMPLETE",
                ],
                "folder": os.path.join(attachments_base, "RSBROTHERS", "rman"),
            },
            {
                "subject_variants": [
                    f"RSB-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "RSBROTHERS", "tablespace"),
            },
        ],
    },
    {
        "name": "GURRAM",
        "label": "DBA_Gurram",
        "subjects": [
            {
                "subject_variants": [
                    f"GRM-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "GURRAM", "tablespace"),
            },
            {
                "subject_variants": ["GRM-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "GURRAM", "rman"),
            },
        ],
    },
    {
        "name": "MAYASHEEL",
        "label": "DBA_Mayasheel",
        "subjects": [
            {
                "subject_variants": [
                    f"MYS-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "MAYASHEEL", "tablespace"),
            },
            {
                "subject_variants": ["MYS-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "MAYASHEEL", "rman"),
            },
        ],
    },
    {
        "name": "MRPL",
        "label": "DBA_MRPL",
        "subjects": [
            {
                "subject_variants": [
                    f"MRL-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "MRPL", "tablespace"),
            },
            {
                "subject_variants": ["MRL-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "MRPL", "rman"),
            },
        ],
    },
    {
        "name": "MUFTI",
        "label": "DBA_Mufti",
        "subjects": [
            {
                "subject_variants": [
                    f"MUFTI-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "MUFTI", "tablespace"),
            },
            {
                "subject_variants": ["MUFTI-INFO: PROD-GINESYS DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "MUFTI", "rman"),
            },
        ],
    },
    {
        "name": "SHREE",
        "label": "DBA_Shree",
        "subjects": [
            {
                "subject_variants": [
                    f"SHR-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "SHREE", "tablespace"),
            },
            {
                "subject_variants": ["SHR-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "SHREE", "rman"),
            },
        ],
    },
    {
        "name": "SKECHERS",
        "label": "DBA_Skechers",
        "subjects": [
            {
                "subject_variants": [
                    f"SKH-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "SKECHERS", "tablespace"),
            },
            {
                "subject_variants": ["SKH-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "SKECHERS", "rman"),
            },
        ],
    },
    {
        "name": "SOCH",
        "label": "DBA_Soch",
        "subjects": [
            {
                "subject_variants": [
                    f"SCH-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "SOCH", "tablespace"),
            },
            {
                "subject_variants": ["SCH-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "SOCH", "rman"),
            },
        ],
    },
    {
        "name": "STYLEBAAZAR",
        "label": "DBA_Stylebazar",
        "subjects": [
            {
                "subject_variants": [
                    f"STL-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "STYLEBAAZAR", "tablespace"),
            },
            {
                "subject_variants": ["STL-INFO: PROD DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "STYLEBAAZAR", "rman"),
            },
        ],
    },
    {
        "name": "CBMRETAIL",
        "label": "DBA_CBMH",
        "subjects": [
            {
                "subject_variants": [
                    f"CBMH-INFO: GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "CBMRETAIL", "tablespace"),
            },
            {
                "subject_variants": ["CBMH-INFO: RMAN INFORMATION"],
                "folder": os.path.join(attachments_base, "CBMRETAIL", "rman"),
            },
        ],
    },
    {
        "name": "VMART",
        "label": "DBA_Vmart",
        "subjects": [
            {
                "subject_variants": [
                    f"VMART-GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "VMART", "tablespace"),
            },
            {
                "subject_variants": ["VMART-INFO: PROD-GINESYS DB RMAN BACKUP COMPLETE"],
                "folder": os.path.join(attachments_base, "VMART", "rman"),
            },
        ],
    },
    {
        "name": "BIBA",
        "label": "DBA_BIBA",
        "subjects": [
            {
                "subject_variants": [
                    f"BIBA-INFO: GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "BIBA", "tablespace"),
            },
            {
                "subject_variants": ["BIBA-INFO: RMAN INFORMATION"],
                "folder": os.path.join(attachments_base, "BIBA", "rman"),
            },
        ],
    },
    {
        "name": "RANGREETI",
        "label": "DBA_RANGREETI",
        "subjects": [
            {
                "subject_variants": [
                    f"BAPL-INFO: GINESYS DATABASE TABLESPACE INFO {datetime.now().strftime('%d%m%y')}"
                ],
                "folder": os.path.join(attachments_base, "RANGREETI", "tablespace"),
            },
            {
                "subject_variants": ["BAPL-INFO: RMAN INFORMATION"],
                "folder": os.path.join(attachments_base, "RANGREETI", "rman"),
            },
        ],
    },
]


    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_client, clients)

if __name__ == "__main__":
    main()
