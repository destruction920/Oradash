import os
import chardet

def convert_logs_to_utf8(directory):
    """
    Converts all log files in the given directory to UTF-8 encoding.
    
    Args:
        directory (str): The directory containing log files.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Skipping...")
        return

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Only process .log or .txt files
        if file_name.lower().endswith((".log", ".txt")):
            try:
                # Detect file encoding
                with open(file_path, "rb") as file:
                    raw_data = file.read()
                    detected_encoding = chardet.detect(raw_data)["encoding"]
                    print(f"Detected encoding for {file_path}: {detected_encoding}")

                # Read the file with its detected encoding
                with open(file_path, "r", encoding=detected_encoding) as file:
                    content = file.read()

                # Write the content back to the file in UTF-8 encoding
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

                print(f"Converted {file_path} to UTF-8 successfully.")

            except Exception as e:
                print(f"Error converting {file_path} to UTF-8: {e}")

def main():
    # Base directory for attachments
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ATTACHMENTS_BASE = os.path.join(BASE_DIR, "attachments")

    # Define client directories dynamically
    clients = [
        {"name": "CBMRETAIL", "folder": os.path.join(ATTACHMENTS_BASE, "CBMRETAIL", "longquery")},
        {"name": "BIBA", "folder": os.path.join(ATTACHMENTS_BASE, "BIBA", "longquery")},
        {"name": "RANGREETI", "folder": os.path.join(ATTACHMENTS_BASE, "RANGREETI", "longquery")}
    ]

    # Process each client directory
    for client in clients:
        print(f"Processing directory for client: {client['name']}")
        convert_logs_to_utf8(client["folder"])

if __name__ == "__main__":
    main()
