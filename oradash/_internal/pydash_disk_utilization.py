import imaplib
import email
import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Base directory for attachments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACHMENTS_BASE = os.path.join(BASE_DIR, "attachments")

# Function to clear the folder
def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove the folder and its contents
    os.makedirs(path, exist_ok=True)  # Recreate the folder

# Function to select a label
def select_label(mail, label_name):
    print(f"Selecting the label '{label_name}'...")
    status, count = mail.select(label_name)
    if status != "OK":
        print(f"Error selecting label '{label_name}'.")
        return False
    print(f"Label '{label_name}' selected successfully. Total emails: {count[0].decode()}")
    return True

# Function to search for emails with a specific subject and download the latest attachment
def search_and_download(mail, subject_line, save_path):
    print(f"Searching for emails with subject: {subject_line}")
    today_imap = datetime.now().strftime("%d-%b-%Y")  # e.g., 24-Nov-2024
    status, messages = mail.search(None, f'(ON {today_imap} SUBJECT "{subject_line}")')

    if status != "OK":
        print(f"Error searching for emails with subject '{subject_line}'.")
        return
    
    email_ids = messages[0].split()
    print(f"Total matching emails for subject '{subject_line}': {len(email_ids)}")
    
    # Process only the latest matching email
    if email_ids:
        print("Processing the latest matching email...")
        latest_email_id = email_ids[-1]  # Get the latest email ID
        status, data = mail.fetch(latest_email_id, "(RFC822)")
        if status != "OK":
            print(f"Error fetching email ID {latest_email_id.decode()}.")
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
        print(f"No emails found with subject '{subject_line}'.")

# Function to process a single client
def process_client(client):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("dbsrvalerts@gsl.in", "uysq fnhz waqq pmzi")
        print(f"Processing client: {client['name']}")

        # Clear folder before processing
        clear_folder(client["folder"])
        if select_label(mail, client["label"]):
            search_and_download(mail, client["subject"], client["folder"])
        else:
            print(f"Skipping {client['name']} section due to label selection failure.")
        
        mail.logout()
    except Exception as e:
        print(f"Error processing client {client['name']}: {e}")

# Main function to run the script
def main():
    clients = [
        {"name": "ARISU", "label": "DBA_ARISU", "subject": f"ARU-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "ARISU", "longquery")},
        {"name": "BIGMARTPRD", "label": "DBA_Bigmart", "subject": f"MMT-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "BIGMART(PRD)", "longquery")},
        {"name": "CHUNMUN", "label": "DBA_Chunmun", "subject": f"CHUNMUN-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CHUNMUN", "longquery")},
        {"name": "CITYKART", "label": "DBA_CityKart", "subject": f"CITYKART-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CITYKART", "longquery")},
        {"name": "GURRAM", "label": "DBA_Gurram", "subject": f"GRM-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "GURRAM", "longquery")},
          {"name": "MAYASHEEL", "label": "DBA_Mayasheel", "subject": f"MYS-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MAYASHEEL", "longquery")},
        {"name": "MUFTIPRD", "label": "DBA_Mufti", "subject": f"MUFTI-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MUFTI(PRD)", "longquery")},
        {"name": "MRPL", "label": "DBA_MRPL", "subject": f"MRL-GINESYS DATABASE LONG QUERY {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "MRPL", "longquery")},
        {"name": "SHREE", "label": "DBA_Shree", "subject": f"SHR-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SHREE", "longquery")},
        {"name": "RSBROTHERSPRD", "label": "DBA_RSBrothers", "subject": f"RSB-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "RSBROTHERS(PRD)", "longquery")},
        {"name": "RSBROTHERSMIS", "label": "DBA_RSBrothers", "subject": f"RSB-GINMIS DATABASE LONGQUERY INFORMATION {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "RSBROTHERS(MIS)", "longquery")},
        {"name": "SKECHERS", "label": "DBA_Skechers", "subject": f"SKH-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SKECHERS", "longquery")},
        {"name": "SOCHPRD", "label": "DBA_Soch", "subject": f"SCH-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "SOCH(PRD)", "longquery")},
        {"name": "STYLEBAAZARPRD", "label": "DBA_Stylebazar", "subject": f"STL-PRD: LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "STYLEBAAZAR(PRD)", "longquery")},
        {"name": "CBMRETAIL", "label": "DBA_CBMH", "subject": f"CBMH-INFO: GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "CBMRETAIL", "longquery")},
        {"name": "VMARTPRD", "label": "DBA_Vmart", "subject": f"VMART-GINESYS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "VMART(PRD)", "longquery")},
        {"name": "VMARTMIS", "label": "DBA_Vmart", "subject": f"VMART-GINMIS DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "VMART(MIS)", "longquery")},
        {"name": "VMARTDR", "label": "DBA_Vmart", "subject": f"VMART-GINESYS_DR DATABASE LONG QUERY INFO {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "VMART(DR)", "longquery")},
        {"name": "BIBA", "label": "DBA_BIBA", "subject": f"BIBA-INFO: LONGQUERY INFORMATION {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "BIBA", "longquery")},
        {"name": "RANGREETI", "label": "DBA_RANGREETI", "subject": f"BAPL-INFO: LONGQUERY INFORMATION {datetime.now().strftime('%d%m%y')}", "folder": os.path.join(ATTACHMENTS_BASE, "RANGREETI", "longquery")},
    ]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_client, clients)

if __name__ == "__main__":
    main()
