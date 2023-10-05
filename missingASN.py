import csv
import paramiko
import os
import logging

# Setup logging
logging.basicConfig(filename='C:\\tmp\\spencersMissingASNs\\sftp_search.log', level=logging.INFO)

# Initialize a dictionary to store the remote paths for each order number
remote_paths = {}

# Read orderNumbers from the CSV
try:
    with open('your_file.csv', 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # skip the header
        for row in reader:
            if row and len(row) > 0:
                remote_paths[row[0]] = None  # Initialize to None, will update later
    logging.info(f"Successfully read {len(remote_paths)} order numbers from CSV.")
except Exception as e:
    logging.exception("An error occurred while reading the CSV file.")

# Connect to the SFTP server
# Connect to the SFTP server
try:
    transport = paramiko.Transport(('sftp.foo.bar', 22))
    transport.connect(username='user', password='password')
    sftp = paramiko.SFTPClient.from_transport(transport)
    logging.info("Successfully connected to SFTP server.")
except paramiko.AuthenticationException:
    logging.error("Authentication failed, please verify your credentials.")
except Exception as e:
    logging.exception("An error occurred while connecting to the SFTP server.")


# Loop through directory in SFTP
try:
    for filename in sftp.listdir('/remote/directory/'):
        for order_number in remote_paths.keys():
            if order_number in filename:
                remote_paths[order_number] = f"/remote/directory/{filename}"
                logging.info(f"Found matching file {filename} for order number {order_number}.")

                # Download the file
                local_file_path = os.path.join('C:\\tmp\\spencersMissingASNs\\', filename)
                sftp.get(remote_paths[order_number], local_file_path)
                logging.info(f"Downloaded {filename} to {local_file_path}.")
except Exception as e:
    logging.exception("An error occurred while searching and downloading files.")

# Close the SFTP connection
if sftp: sftp.close()
if transport: transport.close()
logging.info("SFTP connection closed.")

# Update the CSV file with the remote paths
try:
    with open('venv\\missingASN\\missingASNs.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers + ['RemotePath'])  # write new header
        for order_number, remote_path in remote_paths.items():
            writer.writerow([order_number] + [remote_path])
    logging.info("CSV updated successfully.")
except Exception as e:
    logging.exception("An error occurred while writing to the CSV file.")
