import tkinter as tk
import os
import re
import subprocess
import chardet
import logging
import stat
from tkinter import messagebox
from tkinter import ttk  # Import ttk for Scrollbar
import ttkbootstrap as tb
from ttkbootstrap import Style






# Initialize main window
root = tb.Window(themename="cosmo")  # Modern theme
root.title(" ")
root.state('zoomed')  # Open in fullscreen

# Use the script's directory to locate the icon file
base_directory = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(base_directory, "excalibur.ico")  # Path to your .ico file

if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)  # For Windows
    except Exception as e:
        print(f"Error setting iconbitmap: {e}")
else:
    print(f"Icon file not found: {icon_path}")
    # Fallback to an image-based icon for other platforms
    fallback_icon_path = os.path.join(base_directory, "custom_icon.png")
    if os.path.exists(fallback_icon_path):
        icon_img = tk.PhotoImage(file=fallback_icon_path)
        root.iconphoto(True, icon_img)
    else:
        print("Fallback icon file not found.")

# Variables
archive_seq_prod = tk.StringVar(value=" ")
archive_seq_backup = tk.StringVar(value=" ")
arc_applied_backup = tk.StringVar(value=" ")
finished_apply = tk.StringVar(value=" ")
gap = tk.StringVar(value=" ")
error_recorded = tk.StringVar(value=" ")


# Variables for BIGMART
bigmart_archive_seq_prod = tk.StringVar(value=" ")
bigmart_archive_seq_backup = tk.StringVar(value=" ")
bigmart_arc_applied_backup = tk.StringVar(value=" ")
bigmart_finished_apply = tk.StringVar(value=" ")
bigmart_gap = tk.StringVar(value=" ")
bigmart_error_recorded = tk.StringVar(value=" ")

backup_status_arisu = tk.StringVar(value="")
error_recorded_rman_arisu = tk.StringVar(value="")
rman_log_path_arisu = None

backup_status_bigmart = tk.StringVar(value="")
error_recorded_rman_bigmart = tk.StringVar(value="")
rman_log_path_bigmart = None

# Log file paths for BIGMART
bigmart_arc_gap_log_path = None
bigmart_arc_apply_log_path = None

# Variables for ARISU
gap = tk.StringVar(value="")

# Variables for BIGMART
bigmart_gap = tk.StringVar(value="")

long_query_data = None
blocking_session_data = None
mv_session_data = None
# Dynamically find the script's base directory

base_directory = os.path.dirname(os.path.abspath(__file__))

# Global variables for scrollable tablespace section
tablespace_canvas = None
tablespace_scrollbar = None
tablespace_scrollable_frame = None

# Initialize empty fields for RMAN Backup
backup_status = tk.StringVar(value="")  # Initially empty
error_recorded_rman = tk.StringVar(value="")
rman_log_path = None  # No log file initially


tablespace_data_global = []  # Initially empty
tablespace_alert_log_path = None

# Add a global variable to store BIGMART tablespace data
bigmart_tablespace_data_global = []  # For BIGMART data
bigmart_tablespace_alert_log_path = None  # Separate log path for BIGMART

long_query_data = None
blocking_session_data = None
last_disk_utilization_data = None  # Global variable to store disk utilization data
last_disk_utilization_data_production = None
last_disk_utilization_data_backup = None
last_load_average_content = None

client_sync_status = {}  # Tracks whether each client's log has been synced

def open_log_file(file_path):
    if os.path.exists(file_path):
        print(f"Opening log file: {file_path}")
        os.startfile(file_path)  # Opens the file with the default application
    else:
        print(f"Log file not found: {file_path}")

# Log file paths (dynamic after sync)
arc_gap_log_path = None
arc_apply_log_path = None

# Create top frame for header and sync button
top_frame = tk.Frame(root, bg="#FF9900", height=50)
top_frame.pack(side="top", fill="x")

current_archive_data = []  # Initially empty
temp_tablespace_data = []  # Initially empty

# Global variables
long_query_data = []
blocking_session_data = []
mv_session_data = []
current_archive_data = []
temp_tablespace_data = []
undo_segment_data = []





# Add header label
header_label = tk.Label(top_frame, text="Oradash", bg="#FF9900", fg="white", font=("Arial", 20, "bold"))
header_label.pack(side="left", padx=10)

# Add sync button
sync_button = tk.Button(top_frame, text="Sync", command=lambda: sync_action(), font=("Arial", 10))
sync_button.pack(side="right", padx=10)

# Create section frame for menu buttons
menu_frame = tk.Frame(root, height=50)
menu_frame.pack(side="top", fill="x", pady=5)

# Create placeholder for content
content_frame = tk.Frame(root)
content_frame.pack(fill="both", expand=True)

# Create frames for each section
arc_gap_frame = tk.Frame(content_frame)
rman_backup_frame = tk.Frame(content_frame)
tablespace_frame = tk.Frame(content_frame)
long_query_frame = tk.Frame(content_frame)
disk_utilization_frame = tk.Frame(content_frame)

# Status label
status_label = tk.Label(root, text="Press Sync to fetch updated data", fg="blue", font=("Arial", 10))
status_label.pack(side="bottom", pady=5)

############################################################################ARC GAP AND APPLY CLIENT ADDITION##################################
clients_data = [
    {
        "name": "ARISU",
        "seq_prod_var": archive_seq_prod,
        "seq_backup_var": archive_seq_backup,
        "applied_backup_var": arc_applied_backup,
        "finished_var": finished_apply,
        "gap_var": gap,
        "error_var": error_recorded,
    },
    {
        "name": "BIGMART",
        "seq_prod_var": bigmart_archive_seq_prod,
        "seq_backup_var": bigmart_archive_seq_backup,
        "applied_backup_var": bigmart_arc_applied_backup,
        "finished_var": bigmart_finished_apply,
        "gap_var": bigmart_gap,
        "error_var": bigmart_error_recorded,
    },
    {
        "name": "CHUNMUN",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
  {
        "name": "CITYKART",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "GURRAM",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "MAYASHEEL",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },

{
        "name": "MRPL",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "MUFTI",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "RSBROTHERS",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "SHREE",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "SKECHERS",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "SOCH",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "STYLEBAAZAR",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
        "name": "CBMRETAIL",  # Add CHUNMUN
        "seq_prod_var": tk.StringVar(value=" "),  # Initialize with blank values
        "seq_backup_var": tk.StringVar(value=" "),
        "applied_backup_var": tk.StringVar(value=" "),
        "finished_var": tk.StringVar(value=" "),
        "gap_var": tk.StringVar(value=" "),
        "error_var": tk.StringVar(value=" "),
    },
{
    "name": "BIBA",
    "seq_prod_var": tk.StringVar(value=" "),  # No data for these fields
    "seq_backup_var": tk.StringVar(value=" "),
    "applied_backup_var": tk.StringVar(value=" "),
    "finished_var": tk.StringVar(value=" "),
    "gap_var": tk.StringVar(value=" "),  # Gap field dynamically bound
    "error_var": tk.StringVar(value=" ")  # Error Recorded dynamically bound
},

{
    "name": "RANGREETI",
    "seq_prod_var": tk.StringVar(value=" "),  # No data for these fields
    "seq_backup_var": tk.StringVar(value=" "),
    "applied_backup_var": tk.StringVar(value=" "),
    "finished_var": tk.StringVar(value=" "),
    "gap_var": tk.StringVar(value=" "),  # Gap field dynamically bound
    "error_var": tk.StringVar(value=" ")  # Error Recorded dynamically bound
},
{
    "name": "VMART",
    "seq_prod_var": tk.StringVar(value=" "),  # No data for these fields
    "seq_backup_var": tk.StringVar(value=" "),
    "applied_backup_var": tk.StringVar(value=" "),
    "finished_var": tk.StringVar(value=" "),
    "gap_var": tk.StringVar(value=" "),  # Gap field dynamically bound
    "error_var": tk.StringVar(value=" ")  # Error Recorded dynamically bound
}











]
############################################################################ARC GAP AND APPLY CLIENT ADDITION##################################





from tkinter import StringVar, Label

# Example client data initialization
rman_clients_data = []
for client_name in ["ARISU", "BIGMART", "CHUNMUN", "CITYKART", "GURRAM", "MAYASHEEL", "MRPL", "MUFTI", "RSBROTHERS", "SHREE", "SKECHERS", "SOCH", "STYLEBAAZAR", "CBMRETAIL","BIBA", "RANGREETI", "VMART"]:
    client_data = {
        "name": client_name,
        "backup_status_var": StringVar(),
        "error_recorded_var": StringVar(),
        "backup_status_label": Label(root, textvariable=StringVar()),  # Bind a StringVar
        "error_recorded_label": Label(root, textvariable=StringVar()),  # Bind a StringVar
    }
    rman_clients_data.append(client_data)



tablespace_clients_data = [
    {
        "name": "ARISU",
        "tablespace_data": [],
        "log_path": None,  # Log path for ARISU
    },
    {
        "name": "BIGMART(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },

 {
        "name": "BIGMART(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "CHUNMUN",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "CITYKART",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "GURRAM",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "MAYASHEEL",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "MRPL",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "MUFTI(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "MUFTI(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "RSBROTHERS(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "RSBROTHERS(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "SHREE",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "SKECHERS",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "SOCH(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "SOCH(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "STYLEBAAZAR(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "STYLEBAAZAR(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "CBMRETAIL",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "BIBA",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "RANGREETI",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "VMART(PRD)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
{
        "name": "VMART(MIS)",
        "tablespace_data": [],
        "log_path": None,  # Log path for BIGMART
    },
]



##########################################################LONGQUERY########################
long_query_clients_data = [
    {
        "name": "ARISU",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "BIGMART(PRD)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "BIGMART(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },


{
        "name": "CHUNMUN",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "CITYKART",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "GURRAM",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "GURRAMCTM",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "MAYASHEEL",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "MRPL",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "MUFTI",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "MUFTI(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "RSBROTHERS(PRD)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "RSBROTHERS(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "SHREE",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "SKECHERS",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "SOCH",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "SOCH(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "STYLEBAAZAR(PRD)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "STYLEBAAZAR(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "CBMRETAIL",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "BIBA",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "RANGREETI",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },
{
        "name": "VMART(PRD)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "VMART(MIS)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },

{
        "name": "VMART(DR)",
        "long_query_data": [],
        "blocking_session_data": [],
        "mv_session_data": [],
        "temp_tablespace_data": [],
        "current_archive_data": [],
        "undo_segment_data": [],
        "log_path": None,
    },














    # Add more clients dynamically here
]




client_disk_utilization_data = [
    {
        "name": "ARISU",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "BIGMART(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "CHUNMUN",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "CITYKART",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "GURRAM",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "MAYASHEEL",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "MRPL",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "MUFTI(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "RSBROTHERS(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "RSBROTHERS(MIS)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "SHREE",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "SKECHERS",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "SOCH(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "STYLEBAAZAR(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "CBMRETAIL",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "BIBA",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "RANGREETI",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "VMART(PRD)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "VMART(MIS)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    },
    {
        "name": "VMART(DR)",
        "production": None,
        "backup": None,
        "load_average": None,
        "log_path": None
    }
]
def add_client():
    # Function to add a new client
    new_client_name = new_client_entry.get().strip()
    if new_client_name:
        # Create new StringVars for the new client
        seq_prod_var = tk.StringVar(value=" ")
        seq_backup_var = tk.StringVar(value=" ")
        applied_backup_var = tk.StringVar(value=" ")
        finished_var = tk.StringVar(value=" ")
        gap_var = tk.StringVar(value=" ")
        error_var = tk.StringVar(value=" ")

        # Add the new client to the list
        clients_data.append(
            {
                "name": new_client_name,
                "seq_prod_var": seq_prod_var,
                "seq_backup_var": seq_backup_var,
                "applied_backup_var": applied_backup_var,
                "finished_var": finished_var,
                "gap_var": gap_var,
                "error_var": error_var,
            }
        )
        # Refresh the ARC Gap section to include the new client
        refresh_arc_gap_section()
        new_client_entry.delete(0, tk.END)  # Clear the entry field
        status_label.config(text=f"Client '{new_client_name}' added successfully!", fg="green")
    else:
        status_label.config(text="Please enter a valid client name.", fg="red")




def show_arc_gap_section():
    print("Switching to ARC Gap and Apply Section")  # Debugging
    hide_all_sections()
    arc_gap_frame.pack(fill="both", expand=True)
    refresh_arc_gap_section()

def show_rman_backup_section():
    print("Switching to RMAN Backup Section")  # Debugging
    hide_all_sections()
    rman_backup_frame.pack(fill="both", expand=True)
    refresh_rman_backup_section()

def show_tablespace_section():
    print("Switching to Tablespaces Section")  # Debugging
    hide_all_sections()
    tablespace_frame.pack(fill="both", expand=True)
    refresh_tablespace_section()

def show_long_query_section():
    print("Switching to Long Query Section")  # Debugging
    hide_all_sections()
    long_query_frame.pack(fill="both", expand=True)
    refresh_long_query_section()

def show_disk_utilization_section():
    print("Switching to Disk utilization Section")  # Debugging
    hide_all_sections()
    disk_utilization_frame.pack(fill="both", expand=True)
    refresh_disk_utilization_section()

# Helper function to hide all sections
def hide_all_sections():
    arc_gap_frame.pack_forget()
    rman_backup_frame.pack_forget()
    tablespace_frame.pack_forget()
    long_query_frame.pack_forget()
    disk_utilization_frame.pack_forget()





arc_gap_button = tk.Button(menu_frame, text="ARC Gap and Apply", command=show_arc_gap_section, font=("Arial", 10))
arc_gap_button.pack(side="left", padx=10)

rman_backup_button = tk.Button(menu_frame, text="RMAN Backup", command=show_rman_backup_section, font=("Arial", 10))
rman_backup_button.pack(side="left", padx=10)

tablespace_button = tk.Button(menu_frame, text="Tablespaces", command=show_tablespace_section, font=("Arial", 10))
tablespace_button.pack(side="left", padx=10)

long_query_button = tk.Button(menu_frame, text="Long Query", command=show_long_query_section, font=("Arial", 10))
long_query_button.pack(side="left", padx=10)

disk_utilization_button = tk.Button(menu_frame, text="Disk Utilization", command=show_disk_utilization_section, font=("Arial", 10))
disk_utilization_button.pack(side="left", padx=10)


def refresh_rman_backup_section():
    global new_rman_client_entry, add_rman_client_button

    # Clear the current content
    for widget in rman_backup_frame.winfo_children():
        widget.destroy()

    # Add headers
    headers = ["Client", "Backup Status", "Error Recorded", "Log Files"]
    column_widths = [15, 90, 10, 12]  # Adjust column widths to allocate more space for Backup Status
    for col, header in enumerate(headers):
        tk.Label(
            rman_backup_frame,
            text=header,
            font=("Arial", 10, "bold"),
            borderwidth=1,
            relief="solid",
            anchor="center",
            width=column_widths[col]
        ).grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

    # Populate RMAN data for each client dynamically
    for row, client_data in enumerate(rman_clients_data, start=1):
        add_rman_row(
            rman_backup_frame,
            row,
            client_data["name"],
            client_data["backup_status_var"],
            client_data["error_recorded_var"],
            client_data.get("log_path", None),
        )

    # Add "Add New Client" section at the bottom
    add_rman_client_frame = tk.Frame(rman_backup_frame)
    add_rman_client_frame.grid(row=len(rman_clients_data) + 1, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

    tk.Label(add_rman_client_frame, text="Add New Client:", font=("Arial", 10)).grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    new_rman_client_entry = tk.Entry(add_rman_client_frame, font=("Arial", 10))
    new_rman_client_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    add_rman_client_button = tk.Button(
        add_rman_client_frame,
        text="Add Client",
        command=add_new_rman_client,
        font=("Arial", 10),
    )
    add_rman_client_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

    # Configure grid weights for better column adjustments
    rman_backup_frame.columnconfigure(0, weight=1)
    rman_backup_frame.columnconfigure(1, weight=4)
    rman_backup_frame.columnconfigure(2, weight=1)
    rman_backup_frame.columnconfigure(3, weight=1)

def add_new_rman_client():
    """Add a new client to the RMAN Backup section."""
    new_client_name = new_rman_client_entry.get().strip()
    if new_client_name:
        # Create new StringVars for the new client
        backup_status_var = tk.StringVar(value=" ")
        error_recorded_var = tk.StringVar(value=" ")

        # Add the new client to the list
        rman_clients_data.append(
            {
                "name": new_client_name,
                "backup_status_var": backup_status_var,
                "error_recorded_var": error_recorded_var,
                "log_path": None,  # Set log path to None initially
            }
        )

        # Refresh the RMAN Backup section to include the new client
        refresh_rman_backup_section()
        new_rman_client_entry.delete(0, tk.END)  # Clear the entry field
        status_label.config(text=f"Client '{new_client_name}' added successfully!", fg="green")
    else:
        status_label.config(text="Please enter a valid client name.", fg="red")


def add_rman_row(frame, row, client_name, backup_status_var, error_recorded_var, log_path):
    from tkinter import ttk
    from ttkbootstrap import Style
    import os

    # Define a function to get theme-specific colors dynamically
    def get_theme_color(base_color):
        theme_colors = {
            "white": "#ffffff",
            "green": "#28a745",
            "yellow": "#ffc107",
            "red": "#dc3545",
            "black": "#000000",
            "blue": "#007bff",
            "grey": "#6c757d",
        }
        color = theme_colors.get(base_color, base_color)
        return color

    # Custom ttk styles
    style = Style()
    style.configure("CustomLabel.TLabel", font=("Arial", 10), borderwidth=1, relief="solid")
    style.configure("CustomBackup.TLabel", font=("Arial", 10), borderwidth=1, relief="solid")

    # Logic to create the Backup Status label with dynamic color
    def create_backup_status_label(parent, value, row, column):
        # Determine the background color based on backup status
        if "COMPLETED" in value.upper():
            bg_color = get_theme_color("green")  # Green for completed backups
        elif "FAILED" in value.upper():
            bg_color = get_theme_color("red")  # Red for failed backups
        elif "RUNNING" in value.upper():
            bg_color = get_theme_color("yellow")  # Yellow for running backups
        else:
            bg_color = get_theme_color("grey")  # Grey for unknown status

        # Create the label with the determined background color
        ttk.Label(parent, text=value, style="CustomBackup.TLabel", foreground="white" if bg_color != "#ffffff" else "black", background=bg_color).grid(
            row=row, column=column, sticky="nsew", padx=5, pady=5
        )

    # Create labels for the row
    ttk.Label(frame, text=client_name, style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=0, sticky="nsew", padx=5, pady=5
    )

    # Create the Backup Status label
    create_backup_status_label(frame, backup_status_var.get(), row, 1)

    # Error Recorded
    ttk.Label(frame, text=error_recorded_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=2, sticky="nsew", padx=5, pady=5
    )

    # Log Files
    log_label = ttk.Label(
        frame,
        text="RMAN Log",
        style="CustomLabel.TLabel",
        foreground=get_theme_color("blue") if log_path else get_theme_color("grey"),
        cursor="hand2" if log_path else "arrow",
        background=get_theme_color("white")
    )
    if log_path and os.path.exists(log_path):  # Ensure the file exists before enabling the link
        log_label.bind("<Button-1>", lambda e: os.startfile(log_path))
    log_label.grid(row=row, column=3, sticky="nsew", padx=5, pady=5)

def refresh_arc_gap_section():
    global new_client_entry, add_client_button
    # Clear the current table
    for widget in arc_gap_frame.winfo_children():
        widget.destroy()

    # Add headers
    headers = ["Client", "Archive Seq at Production DB", "Archive Seq at Backup Server",
               "Arc Applied on Backup DB", "Finished Apply", "Gap", "Error Recorded", "Log Files"]
    for col, header in enumerate(headers):
        tk.Label(arc_gap_frame, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(
            row=0, column=col, sticky="nsew", padx=5, pady=5
        )
    

    # Add rows for each client dynamically
    for row, client_data in enumerate(clients_data, start=1):
        if client_data["name"] in ["BIBA", "RANGREETI", "VMART"]:
            # Use a simplified row for BIBA
            add_biba_row(arc_gap_frame, row, client_data)
        else:
            # Add a full row for other clients
            add_arc_gap_row(
                arc_gap_frame,
                row,
                client_data["name"],
                client_data["seq_prod_var"],
                client_data["seq_backup_var"],
                client_data["applied_backup_var"],
                client_data["finished_var"],
                client_data["gap_var"],
                client_data["error_var"],
                client_data.get("gap_log_path"),  # Use the stored gap log path
                client_data.get("apply_log_path")
            )

    # Create a sub-frame for adding new clients
    add_client_frame = tk.Frame(arc_gap_frame)
    add_client_frame.grid(row=len(clients_data) + 1, column=0, columnspan=8, sticky="nsew", padx=5, pady=5)

    # Add entry field and button for adding new clients
    tk.Label(add_client_frame, text="Add New Client:", font=("Arial", 10)).grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    new_client_entry = tk.Entry(add_client_frame, font=("Arial", 10))  # Dynamically create entry
    new_client_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    add_client_button = tk.Button(
        add_client_frame,
        text="Add Client",
        command=lambda: add_client(new_client_entry),
        font=("Arial", 10),
    )
    add_client_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

def add_biba_row(frame, row, client_data):
    client_name = client_data["name"]
    seq_prod_var = client_data["seq_prod_var"]
    seq_backup_var = client_data["seq_backup_var"]
    gap_var = client_data["gap_var"]
    error_var = client_data["error_var"]
    gap_log_path = client_data.get("gap_log_path")

    # Add Client Name
    tk.Label(frame, text=client_name, font=("Arial", 10), borderwidth=1, relief="solid").grid(
        row=row, column=0, sticky="nsew", padx=5, pady=5
    )

    # Add Production Sequence
    tk.Label(frame, textvariable=seq_prod_var, font=("Arial", 10), borderwidth=1, relief="solid").grid(
        row=row, column=1, sticky="nsew", padx=5, pady=5
    )

    # Add Backup Sequence
    tk.Label(frame, textvariable=seq_backup_var, font=("Arial", 10), borderwidth=1, relief="solid").grid(
        row=row, column=2, sticky="nsew", padx=5, pady=5
    )

    # Leave Empty for Applied and Finished
    for col in range(3, 5):
        tk.Label(frame, text="", font=("Arial", 10), borderwidth=1, relief="solid").grid(
            row=row, column=col, sticky="nsew", padx=5, pady=5
        )

    # Add Gap Field
    tk.Label(frame, textvariable=gap_var, font=("Arial", 10), borderwidth=1, relief="solid").grid(
        row=row, column=5, sticky="nsew", padx=5, pady=5
    )

    # Add Error Field
    tk.Label(frame, textvariable=error_var, font=("Arial", 10), borderwidth=1, relief="solid").grid(
        row=row, column=6, sticky="nsew", padx=5, pady=5
    )
    log_label_text = "DR Gap Log" if client_name == "VMART" else "ARC Gap Log"
    # Add ARC Gap Log Link
    log_label = tk.Label(
        frame,
        text=log_label_text,
        font=("Arial", 10),
        fg="blue" if gap_log_path and os.path.exists(gap_log_path) else "grey",
        cursor="hand2" if gap_log_path and os.path.exists(gap_log_path) else "arrow",
        borderwidth=1,
        relief="flat",
        anchor="center",
    )
    if gap_log_path and os.path.exists(gap_log_path):
        log_label.bind("<Button-1>", lambda e: os.startfile(gap_log_path))
    log_label.grid(row=row, column=7, sticky="nsew", padx=5, pady=5)
    

def process_biba_log(log_content, client_data):
    try:
        current_archive_seq = None
        current_available_archive_seq = None

        # Parse the log content
        for line in log_content.split("\n"):
            line = line.strip()
            if "CURRENT ARCHIVE LOG SEQ NO IS" in line:
                current_archive_seq = int(line.split(":")[-1].strip())
            elif "CURRENT AVAILABLE ARCHIVE LOG SEQ NO IS" in line:
                current_available_archive_seq = int(line.split(":")[-1].strip())

        # Update StringVars for BIBA dynamically
        if current_archive_seq is not None:
            client_data["seq_prod_var"].set(str(current_archive_seq))
        if current_available_archive_seq is not None:
            client_data["seq_backup_var"].set(str(current_available_archive_seq))

        # Calculate the gap
        if current_archive_seq is not None and current_available_archive_seq is not None:
            gap = current_archive_seq - current_available_archive_seq
            client_data["gap_var"].set(str(gap))
        else:
            client_data["gap_var"].set("Invalid Data")

        client_data["error_var"].set("")  # Clear errors if everything is fine
    except Exception as e:
        print(f"Error processing BIBA log: {e}")
        client_data["gap_var"].set("Error")
        client_data["error_var"].set(f"Error: {e}")

def sync_biba_log():
    for client_name in ["BIBA", "RANGREETI"]:  # Handle both BIBA and RANGREETI
        log_directory = os.path.join(base_directory, "attachments",client_name,"arc_gap")

        try:
            if not os.path.exists(log_directory):
                print(f"Log directory {log_directory} does not exist.")
                next(client for client in clients_data if client["name"] == client_name)["error_var"].set("Log Directory Not Found")
                continue

            # Find the latest log file
            log_files = [
                os.path.join(log_directory, f)
                for f in os.listdir(log_directory)
                if f.lower().endswith((".log", ".txt"))
            ]
            if not log_files:
                print(f"No log files found in {log_directory}.")
                next(client for client in clients_data if client["name"] == client_name)["error_var"].set("Log File Not Found")
                continue

            latest_log_file = max(log_files, key=os.path.getmtime)
            print(f"Processing log file for {client_name}: {latest_log_file}")

            # Assign log path to client data
            next(client for client in clients_data if client["name"] == client_name)["gap_log_path"] = latest_log_file

            # Read and process log file
            with open(latest_log_file, "r", encoding="utf-8") as file:
                log_content = file.read()

            process_biba_log(log_content, next(client for client in clients_data if client["name"] == client_name))
            print(f"{client_name} log processed successfully.")

        except Exception as e:
            print(f"Error syncing {client_name} log: {e}")
            next(client for client in clients_data if client["name"] == client_name)["error_var"].set(f"Error: {e}")
def add_client(new_client_entry):
    """Add a new client dynamically."""
    new_client_name = new_client_entry.get().strip()
    if new_client_name:
        # Create new StringVars for the new client
        seq_prod_var = tk.StringVar(value=" ")
        seq_backup_var = tk.StringVar(value=" ")
        applied_backup_var = tk.StringVar(value=" ")
        finished_var = tk.StringVar(value=" ")
        gap_var = tk.StringVar(value=" ")
        error_var = tk.StringVar(value=" ")

        # Add the new client to the list
        clients_data.append(
            {
                "name": new_client_name,
                "seq_prod_var": seq_prod_var,
                "seq_backup_var": seq_backup_var,
                "applied_backup_var": applied_backup_var,
                "finished_var": finished_var,
                "gap_var": gap_var,
                "error_var": error_var,
            }
        )

# Refresh the UI immediately after adding a client
        refresh_arc_gap_section()
        new_client_entry.delete(0, tk.END)  # Clear the entry field	 
        status_label.config(text=f"Client '{new_client_name}' added successfully!", fg="green")
    else:
        status_label.config(text="Please enter a valid client name.", fg="red")

    # Add BIGMART data
    add_arc_gap_row(arc_gap_frame, 2, "BIGMART", bigmart_archive_seq_prod, bigmart_archive_seq_backup,
                    bigmart_arc_applied_backup, bigmart_finished_apply, bigmart_gap, bigmart_error_recorded,
                    bigmart_gap_log_path, bigmart_apply_log_path)


def add_arc_gap_row(frame, row, client_name, seq_prod_var, seq_backup_var, applied_backup_var,
                    finished_var, gap_var, error_var, gap_log_path, apply_log_path):
    from tkinter import ttk
    from ttkbootstrap import Style
    import os

    # Define a function to get theme-specific colors dynamically
    def get_theme_color(base_color):
        theme_colors = {
            "white": "#ffffff",
            "green": "#28a745",
            "yellow": "#ffc107",
            "red": "#dc3545",
            "black": "#000000",
            "blue": "#007bff",
            "grey": "#6c757d",
        }
        color = theme_colors.get(base_color, base_color)
        return color

    # Custom ttk styles
    style = Style()
    style.configure("CustomLabel.TLabel", font=("Arial", 10), borderwidth=1, relief="solid")
    style.configure("CustomGap.TLabel", font=("Arial", 10), borderwidth=1, relief="solid")

    # Specific logic for "Gap"
    def create_gap_label(parent, value, row, column):
        try:
            gap_int = int(value.strip())
            if -50 <= gap_int <= 50:
                bg_color = get_theme_color("green")
            elif 51 <= gap_int <= 100 or -100 <= gap_int <= -51:
                bg_color = get_theme_color("yellow")
            else:
                bg_color = get_theme_color("red")
        except ValueError:
            bg_color = get_theme_color("white")
        
        ttk.Label(parent, text=value, style="CustomGap.TLabel", foreground="white" if bg_color != "#ffffff" else "black", background=bg_color).grid(
            row=row, column=column, sticky="nsew", padx=5, pady=5
        )

    # Create labels for the row
    ttk.Label(frame, text=client_name, style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=0, sticky="nsew", padx=5, pady=5
    )
    ttk.Label(frame, text=seq_prod_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=1, sticky="nsew", padx=5, pady=5
    )
    ttk.Label(frame, text=seq_backup_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=2, sticky="nsew", padx=5, pady=5
    )
    ttk.Label(frame, text=applied_backup_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=3, sticky="nsew", padx=5, pady=5
    )
    ttk.Label(frame, text=finished_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=4, sticky="nsew", padx=5, pady=5
    )

    # Create the gap label
    create_gap_label(frame, gap_var.get(), row, 5)

    # Error Field
    ttk.Label(frame, text=error_var.get(), style="CustomLabel.TLabel", background=get_theme_color("white")).grid(
        row=row, column=6, sticky="nsew", padx=5, pady=5
    )

    # Log Files
    log_frame = ttk.Frame(frame)
    log_frame.grid(row=row, column=7, sticky="nsew", padx=5, pady=5)

    # ARC Gap Log link
    gap_log_label = ttk.Label(
        log_frame,
        text="ARC Gap Log",
        style="CustomLabel.TLabel",
        foreground=get_theme_color("blue") if gap_log_path else get_theme_color("grey"),
        cursor="hand2" if gap_log_path else "arrow",
        background=get_theme_color("white")
    )
    gap_log_label.pack(side="left", padx=5)
    if gap_log_path and os.path.exists(gap_log_path):  # Ensure the file exists before enabling the link
        gap_log_label.bind("<Button-1>", lambda e: os.startfile(gap_log_path))

    # ARC Apply Log link
    apply_log_label = ttk.Label(
        log_frame,
        text="ARC Apply Log",
        style="CustomLabel.TLabel",
        foreground=get_theme_color("blue") if apply_log_path else get_theme_color("grey"),
        cursor="hand2" if apply_log_path else "arrow",
        background=get_theme_color("white")
    )
    apply_log_label.pack(side="left", padx=5)
    if apply_log_path and os.path.exists(apply_log_path):  # Ensure the file exists before enabling the link
        apply_log_label.bind("<Button-1>", lambda e: os.startfile(apply_log_path))



def parse_log_gap(log_directory):
    """
    Parse the LOG_GAP values from the log files in the specified directory.

    Args:
        log_directory (str): Directory where the log files are stored.

    Returns:
        list: A list of LOG_GAP values extracted from the log files.
    """
    log_gap_values = []
    try:
        # Check if the directory exists
        if not os.path.exists(log_directory):
            print(f"Directory not found: {log_directory}")
            return log_gap_values

        # Get the latest log file in the directory
        log_files = [
            os.path.join(log_directory, f)
            for f in os.listdir(log_directory)
            if f.lower().endswith((".log", ".txt"))
        ]

        if not log_files:
            print(f"No log files found in {log_directory}")
            return log_gap_values

        latest_log_file = max(log_files, key=os.path.getmtime)
        print(f"Processing file: {latest_log_file}")

        # Read and parse the latest log file
        with open(latest_log_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                # Skip headers and separators
                if line.strip().startswith('-') or line.strip().startswith('Current Time') or not line.strip():
                    continue
                # Split the line into columns
                columns = line.split()
                if len(columns) >= 6:  # Ensure there are enough columns
                    log_gap = columns[5]  # LOG_GAP is the 6th column
                    if log_gap.isdigit():  # Ensure it is a valid number
                        log_gap_values.append(int(log_gap))
        return log_gap_values
    except Exception as e:
        print(f"Error parsing log file: {e}")
        return []

def update_gap_field_ui(client_name, log_gap_values):
    """
    Update the gap field in the UI for the given client with the parsed LOG_GAP values.

    Args:
        client_name (str): Name of the client (e.g., "VMART").
        log_gap_values (list): List of LOG_GAP values extracted from the log.
    """
    try:
        # Find the client in the clients_data
        client_data = next(client for client in clients_data if client["name"] == client_name)
        if log_gap_values:
            # Display the values as a comma-separated string in the gap field
            client_data["gap_var"].set(", ".join(map(str, log_gap_values)))
        else:
            client_data["gap_var"].set("No Data")
    except Exception as e:
        print(f"Error updating gap field for {client_name}: {e}")


def update_gap_field_for_clients(client_names):
    """
    Update the Gap and Error Recorded fields for specified clients based on their log files.
    If 'ok!' and 'error' are both found (case-insensitive), prioritize 'Error'.
    Args:
        client_names (list): List of client names to process (e.g., ["VMART"]).
    """
    for client_name in client_names:
        log_directory = os.path.join(base_directory, "attachments", client_name, "arc_gap")

        print("Log Directory:", log_directory)


        try:
            # Check if the directory exists
            if not os.path.exists(log_directory):
                print(f"{client_name} log directory does not exist.")
                client = next(client for client in clients_data if client["name"] == client_name)
                client["gap_var"].set("Log Directory Not Found")
                client["error_var"].set("Check DR Gap")
                continue

            # Find the latest log file in the directory
            log_files = [
                os.path.join(log_directory, f)
                for f in os.listdir(log_directory)
                if f.lower().endswith((".log", ".txt"))
            ]
            if not log_files:
                print(f"No log files found for {client_name}.")
                client = next(client for client in clients_data if client["name"] == client_name)
                client["gap_var"].set("No Log Found")
                client["error_var"].set("Check DR Gap")
                continue

            # Get the latest log file
            latest_log_file = max(log_files, key=os.path.getmtime)
            print(f"Processing latest log file for {client_name}: {latest_log_file}")

            # Read and search for 'ok!' or 'error' in the log file (case-insensitive)
            found_ok = False
            found_error = False

            with open(latest_log_file, "r", encoding="utf-8") as file:
                lines = file.readlines()

            for line in lines:
                normalized_line = line.lower()  # Convert line to lowercase for case-insensitive comparison
                if "ok!" in normalized_line:  # Check for the word 'ok!' in the log
                    found_ok = True
                if "error" in normalized_line:  # Check for any error in the log
                    found_error = True

            # Update the gap and error fields for the client in the UI
            client = next(client for client in clients_data if client["name"] == client_name)
            if found_error:
                client["gap_var"].set("Error")  # Display 'Error' in the Gap field
                client["error_var"].set("Check DR Gap")  # Set Error Recorded to 'Check DR Gap'
                print(f"Updated {client_name} Gap field with 'Error' and Error Recorded with 'Check DR Gap'.")
            elif found_ok:
                client["gap_var"].set("OK!")  # Display 'OK!' in the Gap field
                client["error_var"].set("")  # Clear the Error Recorded field
                print(f"Updated {client_name} Gap field with 'OK!'.")
            else:
                client["gap_var"].set("Error")  # Default to 'Not OK' if neither is found
                client["error_var"].set("Check DR Log")  # Set Error Recorded to 'Check DR Gap'
                print(f"No 'OK!' or 'Error' found in the log file for {client_name}. Defaulting to 'Not OK'.")

        except Exception as e:
            print(f"Error updating {client_name} Gap field: {e}")
            client = next(client for client in clients_data if client["name"] == client_name)
            client["gap_var"].set(f"Error: {e}")
            client["error_var"].set("Check DR Gap")



def refresh_tablespace_section():
    """
    Refresh the tablespace section to display updated data for all clients with a scrollable UI.
    Ensure the dynamic coloring for rows with a red cell in "Less Space Recorded" is correctly applied in the UI,
    and the log link dynamically updates to blue after sync.
    """
    from tkinter import ttk
    import os

    # Define a function to get theme-specific colors dynamically
    def get_theme_color(base_color):
        theme_colors = {
            "white": "#ffffff",
            "red": "#dc3545",
        }
        return theme_colors.get(base_color, base_color)

    global tablespace_canvas, tablespace_scrollbar, tablespace_scrollable_frame

    # Clear the frame for fresh content
    for widget in tablespace_frame.winfo_children():
        widget.destroy()

    # Create a scrollable canvas
    tablespace_canvas = tk.Canvas(tablespace_frame)
    tablespace_scrollbar = tk.Scrollbar(tablespace_frame, orient="vertical", command=tablespace_canvas.yview)
    tablespace_scrollable_frame = tk.Frame(tablespace_canvas)

    # Configure scrollable frame behavior
    tablespace_scrollable_frame.bind(
        "<Configure>",
        lambda e: tablespace_canvas.configure(scrollregion=tablespace_canvas.bbox("all"))
    )
    tablespace_canvas.create_window((0, 0), window=tablespace_scrollable_frame, anchor="nw")
    tablespace_canvas.configure(yscrollcommand=tablespace_scrollbar.set)

    # Pack canvas and scrollbar into the main frame
    tablespace_canvas.pack(side="left", fill="both", expand=True)
    tablespace_scrollbar.pack(side="right", fill="y")

    # Enable mouse scroll on canvas
    def _on_mouse_wheel(event):
        print(f"DEBUG: Mouse wheel event delta = {event.delta}")
        tablespace_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Redirect scrolling for widgets inside the canvas to the canvas itself
    def bind_mouse_wheel_to_canvas(widget):
        widget.bind("<Enter>", lambda e: tablespace_canvas.bind_all("<MouseWheel>", _on_mouse_wheel))
        widget.bind("<Leave>", lambda e: tablespace_canvas.unbind_all("<MouseWheel>"))

    # Apply mouse wheel scrolling to the entire canvas area
    tablespace_canvas.bind("<Enter>", lambda e: tablespace_canvas.bind_all("<MouseWheel>", _on_mouse_wheel))
    tablespace_canvas.bind("<Leave>", lambda e: tablespace_canvas.unbind_all("<MouseWheel>"))

    # Add sections for each client dynamically
    current_row = 0
    for client_data in tablespace_clients_data:
        # Add client heading
        client_name = client_data["name"]
        client_log_path = client_data["log_path"]

        client_heading_frame = tk.Frame(tablespace_scrollable_frame)
        client_heading_frame.grid(row=current_row, column=0, columnspan=7, sticky="nsew", padx=5, pady=5)

        client_heading_label = tk.Label(
            client_heading_frame,
            text=client_name,
            font=("Arial", 14, "bold"),
            fg="black",
            anchor="w"
        )
        client_heading_label.pack(side="left", padx=5)

        # Add attachment link with full file name
        if client_log_path:
            base_name = os.path.basename(client_log_path)  # Use the full file name
            attachment_text = f"Tablespace Log ({base_name})"
        else:
            attachment_text = "Tablespace Log"

        attachment_link = tk.Label(
            client_heading_frame,
            text=attachment_text,
            font=("Arial", 10),
            fg="blue" if client_log_path else "grey",
            cursor="hand2" if client_log_path else "arrow",
            anchor="e"
        )
        if client_log_path:
            attachment_link.bind("<Button-1>", lambda e, path=client_log_path: os.startfile(path))
        attachment_link.pack(side="right", padx=5)

        # Update the log link color dynamically after sync
        def update_log_link_color():
            if client_log_path:
                attachment_link.configure(fg="blue")
                print(f"DEBUG: Updated log link color for {client_name} to blue.")

        # Simulate updating the link color after sync (call this where sync completes)
        update_log_link_color()

        current_row += 1

        # Add headers for the client
        headers = [
            "Tablespace Name", "Total GB", "Used GB", "Free GB",
            "Tmax Size", "Used%", "Less Space Recorded"
        ]
        column_widths = [20, 15, 15, 15, 15, 10, 25]  # Adjust column widths
        for col, (header, col_width) in enumerate(zip(headers, column_widths)):
            header_label = tk.Label(
                tablespace_scrollable_frame,
                text=header,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                anchor="center",
                bg="lightgrey",
                width=col_width,
                padx=5,
                pady=5,
            )
            header_label.grid(row=current_row, column=col, sticky="nsew", padx=5, pady=5)
            bind_mouse_wheel_to_canvas(header_label)
        current_row += 1

        # Populate tablespace data for the client
        client_tablespace_data = client_data.get("tablespace_data", [])
        for data_row in client_tablespace_data:
            try:
                # Check if the row should be red
                less_space_value = data_row[-1]  # The last column is "Less Space Recorded"
                row_color = get_theme_color("red") if less_space_value.isdigit() and int(less_space_value) <= 20 else get_theme_color("white")

                print(f"DEBUG: Row {current_row}, Less Space Recorded = {less_space_value}, Color = {row_color}")
            except Exception as e:
                print(f"ERROR: Determining color for row {current_row}, data: {data_row}, error: {e}")
                row_color = get_theme_color("white")

            for col, value in enumerate(data_row):
                # Apply row color
                data_label = tk.Label(
                    tablespace_scrollable_frame,
                    text=value,
                    font=("Arial", 10),
                    borderwidth=1,
                    relief="solid",
                    anchor="center",
                    padx=5,
                    pady=5,
                )
                # Force background color to apply using `tk.Label` directly
                data_label.configure(bg=row_color)
                data_label.grid(row=current_row, column=col, sticky="nsew", padx=5, pady=5)
                # Bind mouse wheel scrolling to this widget
                bind_mouse_wheel_to_canvas(data_label)

            current_row += 1  # Move to the next row after processing the current row

    # Ensure the canvas updates its scroll region
    tablespace_canvas.update_idletasks()
    tablespace_canvas.configure(scrollregion=tablespace_canvas.bbox("all"))


def add_new_tablespace_client():
    """Add a new client to the Tablespaces section."""
    new_client_name = new_tablespace_client_entry.get().strip()
    if new_client_name:
        # Add new client to the tablespace client data
        tablespace_clients_data.append(
            {
                "name": new_client_name,
                "tablespace_data": [],
                "log_path": None,  # Set log path to None initially
            }
        )

        # Refresh the Tablespaces section to include the new client
        refresh_tablespace_section()
        new_tablespace_client_entry.delete(0, tk.END)  # Clear the entry field
        status_label.config(text=f"Client '{new_client_name}' added successfully!", fg="green")
    else:
        status_label.config(text="Please enter a valid client name.", fg="red")



def sync_arc_gap():
    status_label.config(text="Syncing ARC Gap and Apply Status...", fg="blue")
    root.update_idletasks()

    try:
        # Execute the external sync script
        script_path = os.path.join(base_directory, "pydash.py")

        print("Script Path:", script_path)  # Path to your script
        subprocess.run(["python", script_path], check=True)
        # Convert downloaded logs to UTF-8
        for client in clients_data:
            client_name = client["name"]
            gap_log_directory = os.path.join(base_directory, "attachments",client_name,"arc_gap")
            apply_log_directory = os.path.join(base_directory, "attachments",client_name,"arc_apply")

            # Convert logs in the gap_log_directory and apply_log_directory to UTF-8
            convert_logs_to_utf8(gap_log_directory)
            convert_logs_to_utf8(apply_log_directory)

        # Process each client dynamically
        for client in clients_data:
            client_name = client["name"]
            gap_log_directory = os.path.join(base_directory, "attachments",client_name,"arc_gap")
            apply_log_directory = os.path.join(base_directory, "attachments",client_name,"arc_apply")

            # Process logs for the client
            try:
                gap_log_path, apply_log_path = process_arc_gap_and_apply(
                    gap_log_directory,
                    apply_log_directory,
                    client["seq_prod_var"],
                    client["seq_backup_var"],
                    client["applied_backup_var"],
                    client["finished_var"],
                    client["gap_var"],
                    client["error_var"]
                )
                # Store log paths in client dictionary
                client["gap_log_path"] = gap_log_path
                client["apply_log_path"] = apply_log_path
                print(f"Sync completed for {client_name}.")
            except Exception as e:
                client["error_var"].set(f"Error: {e}")
                print(f"Error syncing {client_name}: {e}")

        # Refresh the UI for all clients
        refresh_arc_gap_section()

        status_label.config(text="ARC Gap and Apply Sync completed!", fg="green")
    except Exception as e:
        status_label.config(text=f"Error during ARC Gap Sync: {e}", fg="red")
        print(f"Error: {e}")

def convert_logs_to_utf8(directory):
    """
    Converts all log files in the given directory to UTF-8 encoding.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Only process .log or .txt files
        if file_name.lower().endswith((".log", ".txt")):
            try:
                # Read the file with its current encoding (try UTF-8 first, fallback to UTF-16LE)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="utf-16le") as file:
                        content = file.read()

                # Write the content back to the file in UTF-8 encoding
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

                print(f"Converted {file_path} to UTF-8.")
            except Exception as e:
                print(f"Failed to convert {file_path} to UTF-8: {e}")





def process_arc_gap_and_apply(
    gap_log_directory, apply_log_directory,
    seq_prod_var, seq_backup_var, applied_backup_var,
    finished_var, gap_var, error_var
):
    gap_log_path = None
    apply_log_path = None
    try:
        # Initialize variables
        dot_error = False

        # Identify the latest ARC Gap log
        gap_log_files = [f for f in os.listdir(gap_log_directory) if f.endswith((".log", ".txt"))]
        if gap_log_files:
            latest_gap_log = max(gap_log_files, key=lambda x: os.path.getmtime(os.path.join(gap_log_directory, x)))
            gap_log_path = os.path.join(gap_log_directory, latest_gap_log)

            # Convert to UTF-8 and process the ARC Gap log
            convert_log_to_utf8(gap_log_path)
            with open(gap_log_path, "r", encoding="utf-8") as gap_log_file:
                for line in gap_log_file:
                    if "CURRENT ARCHIVE LOG SEQ NO IS" in line:
                        seq_prod_var.set(line.split(":")[-1].strip())
                    if "CURRENT AVAILABLE ARCHIVE LOG SEQ NO IS" in line:
                        seq_backup_var.set(line.split(":")[-1].strip())

        # Identify the latest ARC Apply log
        apply_log_files = [f for f in os.listdir(apply_log_directory) if f.endswith((".log", ".txt"))]
        if apply_log_files:
            latest_apply_log = max(apply_log_files, key=lambda x: os.path.getmtime(os.path.join(apply_log_directory, x)))
            apply_log_path = os.path.join(apply_log_directory, latest_apply_log)

            # Convert to UTF-8 and process the ARC Apply log
            convert_log_to_utf8(apply_log_path)
            with open(apply_log_path, "r", encoding="utf-8") as apply_log_file:
                lines = apply_log_file.readlines()
                last_archive_seq, finished_time = None, None
                for line in lines:
                    if ".arc." in line.lower():
                        dot_error = True
                    if "Last Archive Sequence Applied" in line:
                        last_archive_seq = line.split(":")[-1].strip()
                    if "Finished DATE and TIME" in line:
                        finished_time = lines[lines.index(line) + 2].strip()

                # Update variables
                if last_archive_seq:
                    applied_backup_var.set(last_archive_seq)
                else:
                    applied_backup_var.set("")  # Set empty if not found
                if finished_time:
                    finished_var.set(finished_time)
                else:
                    finished_var.set("")  # Set empty if not found

        # Validate and calculate the gap
        try:
            prod_seq = int(seq_prod_var.get().strip()) if seq_prod_var.get().strip().isdigit() else None
            applied_seq = int(applied_backup_var.get().strip()) if applied_backup_var.get().strip().isdigit() else None

            if prod_seq is None or applied_seq is None:
                raise ValueError("Invalid sequence numbers")

            calculated_gap = prod_seq - applied_seq
            gap_var.set(str(calculated_gap))
        except ValueError:
            gap_var.set("Error")

        # Set error_var based on conditions
        if dot_error:
            error_var.set("Dot Error Found")
        elif seq_prod_var.get().strip() == "" or seq_backup_var.get().strip() == "" or applied_backup_var.get().strip() == "":
            error_var.set("Invalid Values.Check Log")
        else:
            error_var.set("")  # Clear error if no issues

    except Exception as e:
        print(f"Error processing logs for ARC Gap and Apply: {e}")
        error_var.set(f"Error: {e}")

    return gap_log_path, apply_log_path


def convert_log_to_utf8(file_path):
    """
    Converts a single log file to UTF-8 encoding.
    """
    try:
        # Read the file with its current encoding (try UTF-8 first, fallback to UTF-16LE)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-16le") as file:
                content = file.read()

        # Write the content back to the file in UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Converted {file_path} to UTF-8.")
    except Exception as e:
        print(f"Failed to convert {file_path} to UTF-8: {e}")


from datetime import datetime
def clear_rman_backup_section():
    for client_data in rman_clients_data:
        backup_status_label = client_data["backup_status_label"]
        error_recorded_label = client_data["error_recorded_label"]

        # Clear old data
        backup_status_label.config(text="")
        error_recorded_label.config(text="")

def sync_rman_backup():
    status_label.config(text="Syncing RMAN Backup Status data...", fg="blue")
    root.update_idletasks()

    try:
        # Set initial fetching status for all clients
        for client_data in rman_clients_data:
            client_data["backup_status_var"].set("Fetching...")
            client_data["error_recorded_var"].set("")

        # Clear UI to remove old data
        clear_rman_backup_section()
        #Step 1: Run the external script to download the dynamic tablespace logs
        # Construct the path to the pydash_tablespace.py dynamically
        script_path = os.path.join(base_directory, "pydash_tablespace.py")

        print("Script Path:", script_path)
        print("Running dynamic log downloader...")
        subprocess.run(["python", script_path], check=True)
        print("Dynamic tablespace log downloaded successfully.")

        # Step 1: Process the downloaded tablespace logs for all dynamic clients
        sysdate = datetime.now().strftime("%d-%b-%y").strip()  # Current date in log format (e.g., 27-NOV-24)

        # Process each client's RMAN and Tablespace logs
        for client_data in rman_clients_data:
            client_name = client_data["name"]
            log_directory = os.path.join(base_directory, "attachments", client_name, "tablespace")
            rman_log_directory = os.path.join(base_directory, "attachments", client_name, "rman")

            print("Log Directory:", log_directory)
            print("RMAN Log Directory:", rman_log_directory)
            backup_status_var = client_data["backup_status_var"]
            error_recorded_var = client_data["error_recorded_var"]

            # Validate directories
            if not os.path.exists(log_directory):
                print(f"Directory {log_directory} does not exist.")
                backup_status_var.set("Directory Not Found")
                error_recorded_var.set("Check Directory Path")
                continue

            # Process tablespace logs
            try:
                # Detect .log or .txt files
                tablespace_log_files = [
                    f for f in os.listdir(log_directory) if f.lower().endswith((".log", ".txt"))
                ]
                print(f"Files detected in {log_directory}: {tablespace_log_files}")

                if tablespace_log_files:
                    # Get the latest file based on modification time
                    latest_tablespace_log = max(
                        tablespace_log_files, key=lambda x: os.path.getmtime(os.path.join(log_directory, x))
                    )
                    tablespace_log_path = os.path.join(log_directory, latest_tablespace_log)
                    print(f"Processing file: {tablespace_log_path}")

                    # Convert the file to UTF-8 in memory
                    lines = convert_to_utf8(tablespace_log_path)

                    print(f"Contents of {tablespace_log_path}:\n{lines}")
                    found_header = False

                    for i, line in enumerate(lines):
                        if line.strip().startswith("COMMAND_ID"):
                            found_header = True
                            continue
                        if found_header and not line.strip().startswith("----"):
                            parsed_data = line.split(maxsplit=1)[1].strip()
                            backup_date = parsed_data.split()[0].strip()
                            backup_status_var.set(parsed_data)

                            # Check if backup matches today's date
                            # Check if backup matches today's date
                            if backup_date.upper() == sysdate.upper():
                                if "RUNNING" in parsed_data.upper():
                                    error_recorded_var.set("Running")
                                else:
                                    error_recorded_var.set("") if "COMPLETED" in parsed_data.upper() else error_recorded_var.set("Backup Failed")
                            else:
                                error_recorded_var.set("Old Backup")
                            break
                    if not found_header:
                        backup_status_var.set("Invalid Log Format")
                        error_recorded_var.set("Missing COMMAND_ID Header")
                else:
                    # No log files found
                    backup_status_var.set("No Tablespace Logs Found")
                    error_recorded_var.set("No Logs Detected")
            except Exception as e:
                # Handle file reading or parsing errors
                print(f"Error processing tablespace logs for {client_name}: {e}")
                backup_status_var.set("Error")
                error_recorded_var.set(f"Log Processing Error: {e}")

            # Process RMAN logs
            try:
                rman_log_files = [f for f in os.listdir(rman_log_directory) if f.lower().endswith((".log", ".txt"))]
                if rman_log_files:
                    latest_rman_log = max(rman_log_files, key=lambda x: os.path.getctime(os.path.join(rman_log_directory, x)))
                    client_data["log_path"] = os.path.join(rman_log_directory, latest_rman_log)
                else:
                    client_data["log_path"] = None
            except Exception as e:
                client_data["log_path"] = None
                error_recorded_var.set(f"Error processing RMAN logs: {e}")

            # Fallback if no valid data is found
            if backup_status_var.get() == "Fetching...":
                backup_status_var.set("No Valid Data Found")
                error_recorded_var.set("Invalid or Missing Data in Log")

        # Refresh the RMAN Backup section to reflect updated data
        refresh_rman_backup_section()
        root.update_idletasks()

        status_label.config(text="RMAN Backup Status Sync completed!", fg="green")
    except Exception as e:
        status_label.config(text=f"Error during RMAN Backup Status sync: {e}", fg="red")


def convert_to_utf8(file_path):
    """
    Converts the content of a file to UTF-8 encoding.
    Reads the file with the detected encoding and returns the lines as a list.
    """
    try:
        # First try reading the file as UTF-8
        with open(file_path, "r", encoding="utf-8") as file:
            print(f"File {file_path} successfully read as UTF-8.")
            return file.readlines()
    except UnicodeDecodeError:
        print(f"File {file_path} is not UTF-8, trying UTF-16LE.")
        try:
            # If UTF-8 fails, try UTF-16LE
            with open(file_path, "r", encoding="utf-16le") as file:
                content = file.read()
                print(f"File {file_path} successfully read as UTF-16LE. Converting to UTF-8.")
                return content.splitlines()
        except Exception as e:
            print(f"Failed to convert {file_path} to UTF-8: {e}")
            raise

def update_tablespace_ui(arisu_data, bigmart_data):
    """
    Update the UI for both ARISU and BIGMART tablespace data with a scrollable canvas.
    """
    print("Updating Tablespaces UI...")  # Debugging log

    # Clear the existing content
    for widget in tablespace_frame.winfo_children():
        widget.destroy()

    # Create a scrollable canvas
    canvas = tk.Canvas(tablespace_frame)
    scrollbar = ttk.Scrollbar(tablespace_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Bind the scrollable frame to the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Add ARISU data
    arisu_heading_label = tk.Label(
        scrollable_frame,
        text="ARISU",
        font=("Arial", 14, "bold"),
        fg="black",
        anchor="center"
    )
    arisu_heading_label.grid(row=0, column=0, columnspan=7, sticky="nsew", padx=5, pady=5)

    add_tablespace_section(scrollable_frame, 1, arisu_data)

    # Add BIGMART data
    bigmart_heading_label = tk.Label(
        scrollable_frame,
        text="BIGMART",
        font=("Arial", 14, "bold"),
        fg="black",
        anchor="center"
    )
    bigmart_heading_label.grid(row=len(arisu_data) + 3, column=0, columnspan=7, sticky="nsew", padx=5, pady=5)

    add_tablespace_section(scrollable_frame, len(arisu_data) + 4, bigmart_data)

    # Forcefully update the scroll region after rendering all widgets
    tablespace_frame.update_idletasks()  # Ensure all rendering is complete
    canvas.configure(scrollregion=canvas.bbox("all"))  # Update the scroll region
    print("Tablespaces UI updated with ARISU and BIGMART data.")





def sync_tablespace_data():
    """
    Sync tablespace data for all clients and update the UI.
    """
    # Show syncing message
    status_label.config(text="Tablespace data syncing...", fg="blue")
    root.update_idletasks()  # Ensure the UI updates immediately

    try:
        # Run the external script to download the tablespace logs
        print("Running pydash_tablespace_free.py...")
        script_path = os.path.join(base_directory, "pydash_tablespace_free.py")

        print("Script Path:", script_path)
        subprocess.run(["python", script_path], check=True)  # Execute the script
        print("Tablespace log file downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        status_label.config(text="Error running script.", fg="red")
        return

    # Process tablespace data for all clients dynamically
    for client in tablespace_clients_data:
        client_name = client["name"]
        log_directory = os.path.join(base_directory, "attachments", client_name, "tablespace")

        print("Log Directory:", log_directory)

        print(f"Processing data for {client_name}...")  # Debugging output
        tablespace_data, log_path = process_tablespace_data(log_directory, client_name)

        # Update the client's tablespace data and log path
        client["tablespace_data"] = tablespace_data
        client["log_path"] = log_path

        print(f"{client_name} Data: {tablespace_data}")  # Debugging output

    # Update the UI to reflect the data for all clients
    refresh_tablespace_section()

    # Update status label
    status_label.config(text="Tablespaces Sync completed!", fg="green")

def process_tablespace_data(log_directory, client_name):
    try:
        print(f"Processing tablespace data for {client_name}...")
        log_files = [
            os.path.join(log_directory, f)
            for f in os.listdir(log_directory)
            if f.endswith(".log") or f.endswith(".txt")
        ]
        print(f"Log files found in {log_directory}: {log_files}")

        if not log_files:
            print(f"No log files found for {client_name}.")
            return [], None

        latest_log_file = max(log_files, key=os.path.getmtime)
        print(f"Latest log file for {client_name}: {latest_log_file}")

        # Detect file encoding
        with open(latest_log_file, "rb") as file:
            raw_data = file.read()
            encoding_detected = chardet.detect(raw_data)["encoding"]
            print(f"Detected encoding for {latest_log_file}: {encoding_detected}")

        # Parse the log file with the detected encoding
        tablespace_data = []
        with open(latest_log_file, "r", encoding=encoding_detected) as log_file:
            lines = log_file.readlines()
            parsing = False
            for i, line in enumerate(lines):
                line = line.strip()
                print(f"Line {i}: {line}")  # Debugging individual lines

                if line.startswith("TABLESPACE_NAME") and i + 1 < len(lines) and lines[i + 1].startswith("-"):
                    parsing = True
                    continue

                if parsing and not line:
                    break

                if parsing and not line.startswith("-"):
                    columns = line.split()
                    print(f"Parsed columns: {columns}")  # Debugging parsed columns

                    if len(columns) >= 5:
                        try:
                            tmax_size = int(columns[4])
                            used_gb = int(columns[2])
                            less_space = tmax_size - used_gb
                            columns.append(str(less_space))
                        except ValueError:
                            columns.append("")
                    tablespace_data.append(columns)

        print(f"Parsed tablespace data for {client_name}: {tablespace_data}")
        return tablespace_data, latest_log_file
    except Exception as e:
        print(f"Error processing tablespace data for {client_name}: {e}")
        return [], None

def update_tablespace_ui(arisu_data, bigmart_data):
    """
    Update the UI for both ARISU and BIGMART tablespace data.
    """
    print("Updating Tablespaces UI...")  # Debugging log

    # Clear the existing content in the tablespace_frame
    for widget in tablespace_frame.winfo_children():
        widget.destroy()

    # Add the "ARISU" heading
    arisu_heading_label = tk.Label(
        tablespace_frame,
        text="ARISU",
        font=("Arial", 14, "bold"),
        fg="black",
        anchor="center"
    )
    arisu_heading_label.grid(row=0, column=0, columnspan=7, sticky="nsew", padx=5, pady=5)

    # Add ARISU headers and data
    add_tablespace_section(tablespace_frame, 1, arisu_data)

    # Add the "BIGMART" heading
    bigmart_heading_label = tk.Label(
        tablespace_frame,
        text="BIGMART",
        font=("Arial", 14, "bold"),
        fg="black",
        anchor="center"
    )
    bigmart_heading_label.grid(row=len(arisu_data) + 3, column=0, columnspan=7, sticky="nsew", padx=5, pady=5)

    # Add BIGMART headers and data
    add_tablespace_section(tablespace_frame, len(arisu_data) + 4, bigmart_data)

    # Configure column weights for better alignment
    for col in range(7):
        tablespace_frame.columnconfigure(col, weight=1)

    print("Tablespaces UI updated with ARISU and BIGMART data.")


def add_tablespace_section(frame, start_row, data):
    """
    Add a tablespace section to the frame starting at the specified row.
    Includes debugging to trace data and color application.
    """
    headers = [
        "Tablespace Name", "Total GB", "Used GB", "Free GB",
        "Tmax Size", "Used%", "Less Space Recorded"
    ]
    for col, header in enumerate(headers):
        tk.Label(
            frame,
            text=header,
            font=("Arial", 10, "bold"),
            borderwidth=1,
            relief="solid",
            anchor="center",
            bg="lightgrey",
            wraplength=150,
            padx=5,
            pady=5,
        ).grid(row=start_row, column=col, sticky="nsew", padx=5, pady=5)

    for row, tablespace in enumerate(data, start=start_row + 1):
        try:
            print(f"Processing row: {tablespace}")
            less_space_value = tablespace[-1]
            if less_space_value.isdigit():
                less_space = int(less_space_value)
                row_color = "red" if less_space <= 20 else "white"
            else:
                row_color = "white"  # Default color for non-numeric or missing values
            print(f"Row color: {row_color} for less_space_value: {less_space_value}")

        except Exception as e:
            print(f"Error determining row color: {e}")
            row_color = "white"

        for col, value in enumerate(tablespace):
            tk.Label(
                frame,
                text=value,
                font=("Arial", 10),
                borderwidth=1,
                relief="solid",
                anchor="center",
                bg=row_color,
                padx=5,
                pady=5,
            ).grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

    for col in range(len(headers)):
        frame.columnconfigure(col, weight=1)

# Add this below other refresh functions

def refresh_long_query_section():
    """
    Refresh the Long Query section to display data for all clients dynamically,
    including log file attachments with persistent behavior.
    Adds both vertical and horizontal scrollbars with mouse scrolling support.
    """
    global long_query_clients_data

    # Clear the frame content
    for widget in long_query_frame.winfo_children():
        widget.destroy()

    # Create a canvas and a scrollable frame
    canvas = tk.Canvas(long_query_frame)
    v_scrollbar = tk.Scrollbar(long_query_frame, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(long_query_frame, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Create a window inside the canvas for the scrollable frame
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Place canvas and scrollbars in the main frame
    canvas.pack(side="left", fill="both", expand=True)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")

    # Enable mouse scroll on canvas
    def _on_mouse_wheel(event):
        if event.state & 1:  # If the Shift key is pressed, scroll horizontally
            canvas.xview_scroll(-1 * (event.delta // 120), "units")
        else:  # Default vertical scrolling
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Bind mouse scroll events
    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)  # For Windows/MacOS
    canvas.bind_all("<Shift-MouseWheel>", _on_mouse_wheel)  # For horizontal scrolling with Shift key
    canvas.bind_all("<Button-4>", _on_mouse_wheel)  # For Linux scroll up
    canvas.bind_all("<Button-5>", _on_mouse_wheel)  # For Linux scroll down

    # Dynamically add sections for each client
    current_row = 0
    for client_data in long_query_clients_data:
        client_name = client_data["name"]
        log_path = client_data.get("log_path")
        log_link_color = client_data.get("log_link_color", "grey")  # Default to grey if not set

        # Debug MV Refresh Data
        print(f"DEBUG: MV Refresh Data for {client_name}: {client_data.get('mv_refresh_data', [])}")

        # Add client heading with log file attachment
        heading_frame = tk.Frame(scrollable_frame)
        heading_frame.grid(row=current_row, column=0, columnspan=3, pady=(10, 5), sticky="nsew")

        heading_label = tk.Label(heading_frame, text=client_name, font=("Helvetica", 14, "bold"))
        heading_label.pack(side="left", padx=5)

        log_label = tk.Label(
            heading_frame,
            text="Long Query Log" if log_path else "Long Query Log",
            font=("Arial", 10),
            fg=log_link_color,
            cursor="hand2" if log_path else "arrow",
        )
        if log_path:
            log_label.bind("<Button-1>", lambda e, path=log_path: os.startfile(path))
        log_label.pack(side="left", padx=5)

        # Update the color of the log file link after sync
        def update_log_color_after_sync():
            log_label.configure(fg="blue")
            print(f"DEBUG: Updated log link color for {client_name} to blue.")

        # Simulate updating the link color after sync (call this where sync completes)
        update_log_color_after_sync()

        current_row += 1

        # Create frames for grouped sections
        top_frame = tk.Frame(scrollable_frame)
        top_frame.grid(row=current_row, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        # Group Long Sessions and Blocking Sessions in a single frame, one below the other
        long_and_blocking_frame = tk.Frame(top_frame, width=200)
        long_sessions_frame = tk.Frame(long_and_blocking_frame, width=200)
        blocking_sessions_frame = tk.Frame(long_and_blocking_frame, width=200)
        long_sessions_frame.pack(fill="x", pady=(0, 5))
        blocking_sessions_frame.pack(fill="x", pady=(5, 0))

        # Separate frames for other sections
        mv_refresh_frame = tk.Frame(top_frame, width=100)
        archive_generated_frame = tk.Frame(top_frame, width=100)

        # Group Temp and Undo Usage in a single frame, one below the other
        temp_and_undo_frame = tk.Frame(top_frame, width=100)
        temp_tablespace_frame = tk.Frame(temp_and_undo_frame, width=100)
        undo_tablespace_frame = tk.Frame(temp_and_undo_frame, width=100)
        temp_tablespace_frame.pack(fill="x", pady=(0, 5))
        undo_tablespace_frame.pack(fill="x", pady=(5, 0))

        # Grid placements
        long_and_blocking_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        mv_refresh_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        archive_generated_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        temp_and_undo_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        # Add tables for each section
        add_table_to_section(
            long_sessions_frame, "Long Sessions", ["OWNER", "SID", "SERIAL#", "MINS_RUNNING"], client_data.get("long_query_data", [])
        )
        add_table_to_section(
            blocking_sessions_frame, "Blocking Sessions", ["SID", "ISBLOCKING", "SID"], client_data.get("blocking_session_data", [])
        )
        add_table_to_section(
            mv_refresh_frame, "Last MV Refresh", ["OWNER", "MV_NAME", "LAST_REFRESH"], client_data.get("mv_session_data", [])
        )
        add_table_to_section(
            archive_generated_frame, "Current Archive Generated", ["DAY", "ARCHIVE_SIZE(GB)"], client_data.get("current_archive_data", [])
        )
        add_table_to_section(
            temp_tablespace_frame, "Temp Usage", ["TOTAL_MB", "USED_MB", "FREE_MB"], client_data.get("temp_tablespace_data", [])
        )
        add_table_to_section(
            undo_tablespace_frame, "Undo Usage", ["STATUS", "SUM_MB", "COUNTS"], client_data.get("undo_segment_data", [])
        )

        # Move to the next row for the next client
        current_row += 1


  
def add_table_to_section(frame, title, headers, data):
    """
    Add a table structure to a specific section with headers and data rows.
    If no rows are selected, display plain text without a table structure.
    """
    def get_theme_color(base_color):
        theme_colors = {
            "white": "#ffffff",
            "red": "#dc3545",
            "black": "#000000",
        }
        return theme_colors.get(base_color, base_color)

    tk.Label(frame, text=title, font=("Helvetica", 10, "bold")).grid(
        row=0, column=0, columnspan=len(headers), pady=(0, 5), sticky="w"
    )

    if not data or (len(data) == 1 and "no rows selected" in data[0][0].lower()):
        tk.Label(
            frame,
            text="No rows selected",
            font=("Helvetica", 8),
            anchor="w"
        ).grid(row=1, column=0, columnspan=len(headers), sticky="w")
    else:
        # Add headers
        for col, header in enumerate(headers):
            tk.Label(
                frame,
                text=header,
                font=("Helvetica", 10, "bold"),
                borderwidth=1,
                relief="solid",
                anchor="center",
                padx=5,
                pady=5
            ).grid(row=1, column=col, sticky="nsew")

        # Add data rows
        for row_idx, row_data in enumerate(data, start=2):
            if isinstance(row_data, tuple):
                row_text, is_red = row_data
                bg_color = get_theme_color("red") if is_red else get_theme_color("white")
                text_color = "white" if bg_color == get_theme_color("red") else "black"
                print(f"DEBUG: Row {row_idx}, Data: {row_text}, Is Red: {is_red}, BG Color: {bg_color}, Text Color: {text_color}")
            else:
                row_text = row_data
                bg_color = get_theme_color("white")
                text_color = "black"
                print(f"DEBUG: Row {row_idx}, Data: {row_text}, Default BG Color: {bg_color}, Default Text Color: {text_color}")

            for col_idx, cell_data in enumerate(row_text.split()):
                print(f"DEBUG: Adding cell: Row {row_idx}, Column {col_idx}, Text: {cell_data}, BG Color: {bg_color}, Text Color: {text_color}")
                label = tk.Label(
                    frame,
                    text=cell_data,
                    font=("Helvetica", 9),
                    fg=text_color,
                    borderwidth=1,
                    relief="solid",
                    anchor="center",
                    padx=5,
                    pady=5
                )
                # Explicitly set the background color
                label.configure(bg=bg_color)
                label.grid(row=row_idx, column=col_idx, sticky="nsew")







def parse_long_sessions_log(log_dir):
    """
    Parse Long Sessions data from the log files.
    - After `###LONG RUNNING QUERY FOR MORE THAN ONE MINUTE###`, skip the first occurrence of `***************`.
    - Skip a blank line after it.
    - Collect content until encountering another blank line or another `***************`.
    - Exclude lines containing only dashes (e.g., '---------').
    """
    long_sessions_data = []
    try:
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the Long Sessions section
                    if "LONG RUNNING QUERY FOR MORE THAN ONE MINUTE" in stripped_line:
                        start_collecting = True
                        skip_stars_line = True  # Skip the first stars line
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                continue  # Skip the stars line
                            if not stripped_line:  # Skip the blank line after the stars
                                skip_stars_line = False
                                continue

                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            break

                        # Skip dashed lines (e.g., `----------`) exactly
                        if all(char == "-" for char in stripped_line):
                            continue

                        # Check for `no rows selected` and add it to the data
                        if "no rows selected" in stripped_line.lower():
                            long_sessions_data.append("no rows selected")
                            break  # Stop further processing

                        # Collect valid long sessions lines
                        long_sessions_data.append(stripped_line)

        # If no rows were selected and no other data was found
        if not long_sessions_data:
            long_sessions_data.append("no rows selected")

        return long_sessions_data

    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return ["Log directory not found."]
    except Exception as e:
        print(f"Error parsing Long Sessions: {e}")
        return [f"Error: {e}"]

def parse_long_query_log(log_dir):
    """
    Parse Long Sessions data from the log files.
    - After `###LONG RUNNING QUERY FOR MORE THAN ONE MINUTE###`, skip the first occurrence of `***************`.
    - Skip a blank line after it.
    - Collect content until encountering another blank line or another `***************`.
    - Skip lines containing `USERNAME SID SERIAL# MINS_RUNNING`.
    - Skip lines that start with dashes (`---`), even if they contain leading whitespace.
    - Stop parsing after the first blank line following valid content.
    """
    long_session_data = []
    try:
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False
                content_found = False  # Flag to detect if valid content was found

                for line in lines:
                    stripped_line = line.strip()

                    # Debugging: Print the line being processed
                    print(f"DEBUG: Processing line: '{stripped_line}'")

                    # Detect the start of the Long Sessions section
                    if "###LONG RUNNING QUERY FOR MORE THAN ONE MINUTE###" in stripped_line:
                        print("DEBUG: Found LONG RUNNING QUERY header.")
                        start_collecting = True
                        skip_stars_line = True  # Skip the first stars line
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                print("DEBUG: Skipping stars line.")
                                continue  # Skip the stars line
                            if not stripped_line:  # Skip the blank line after the stars
                                print("DEBUG: Skipping blank line after stars.")
                                skip_stars_line = False
                                continue

                        # Skip dashed lines (e.g., `---`)
                        if stripped_line.lstrip().startswith("-"):
                            print("DEBUG: Skipping dashed line.")
                            continue

                        # Skip the header line `USERNAME SID SERIAL# MINS_RUNNING`
                        if "USERNAME" in stripped_line and "SID" in stripped_line and "MINS_RUNNING" in stripped_line:
                            print("DEBUG: Skipping header line.")
                            continue

                        # Stop parsing after the first blank line if valid content was already found
                        if not stripped_line and content_found:
                            print("DEBUG: Stopping parsing after first blank line following content.")
                            break

                        # Check for valid content and flag rows with `MINS_RUNNING >= 60`
                        if stripped_line:  # Ensure the line is not blank
                            try:
                                parts = stripped_line.split()
                                mins_running = float(parts[-1])  # Assume MINS_RUNNING is the last column
                                is_red = mins_running >= 30  # Flag for red color if >= 30
                                print(f"DEBUG: Adding line with MINS_RUNNING = {mins_running}.")
                                long_session_data.append((stripped_line, is_red))
                                content_found = True  # Mark that valid content was found
                            except (ValueError, IndexError):
                                # If parsing fails, add the line without the red flag
                                print("DEBUG: Adding line with parsing error (default no red flag).")
                                long_session_data.append((stripped_line, False))
                                content_found = True  # Mark that valid content was found

        return long_session_data

    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"Error parsing Long Sessions: {e}")
        return [(f"Error: {e}", False)]





def sync_long_query():
    """
    Sync long query data and refresh the UI, including Blocking Sessions.
    """
    status_label.config(text="Syncing Long Query data...", fg="blue")
    root.update_idletasks()

    log_dir = os.path.join(base_directory, "attachments", "ARISU", "longquery")

    print("Log Directory:", log_dir)

    try:
        # Process long query logs for Long Sessions
        long_query_data = parse_long_query_log(log_dir)

        # Process long query logs for Blocking Sessions
        blocking_session_data = parse_blocking_sessions_log(log_dir)

        # Update the UI with both Long Sessions and Blocking Sessions data
        update_long_query_ui(long_query_data, blocking_session_data)

        print("Long Query and Blocking Sessions data successfully synced.")
        status_label.config(text="Long Query Sync completed!", fg="green")

    except Exception as e:
        print(f"Error syncing long query data: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def sync_long_query_data():
    """
    Sync long query data for all clients and dynamically update the log link color based on file availability.
    """
    global long_query_clients_data
    status_label.config(text="Syncing Long Query data...", fg="blue")
    root.update_idletasks()

    script_path = os.path.join(base_directory, "pydash_longquery.py")
    script_path1 = os.path.join(base_directory, "pydash_utf8.py")

    print("Script Path:", script_path)
    print("Script Path 1:", script_path1)

    try:
        # Run the external script to download logs
        subprocess.run(["python", script_path], check=True)
        subprocess.run(["python", script_path1], check=True)

        # Process logs for each client dynamically
        for client_data in long_query_clients_data:
            client_name = client_data["name"]
            log_dir = os.path.join(base_directory, "attachments", client_name, "longquery")

            print("Log Directory:", log_dir)

            # Update log path and link color for the client
            log_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.lower().endswith((".log", ".txt"))
            ]
            if log_files:
                latest_log_file = max(log_files, key=os.path.getmtime)
                client_data["log_path"] = latest_log_file
                client_data["log_link_color"] = "blue"  # Log file available
                print(f"{client_name}: Log file path updated to {latest_log_file}")
            else:
                client_data["log_path"] = None
                client_data["log_link_color"] = "grey"  # No log file available
                print(f"{client_name}: No log files found.")

            # Parse and update client data
            client_data["long_query_data"] = parse_long_query_log(log_dir)
            client_data["blocking_session_data"] = parse_blocking_sessions_log(log_dir)
            client_data["mv_session_data"] = parse_mv_not_refreshed_log(log_dir)
            client_data["temp_tablespace_data"] = parse_temp_tablespace_usage(log_dir)
            client_data["current_archive_data"] = parse_current_archive_generated(log_dir)

            # Parse undo segment status and preserve log path
            client_data["undo_segment_data"] = parse_undo_segment_status(log_dir)

            # Ensure log_path remains consistent
            if not client_data.get("log_path"):
                client_data["log_path"] = log_dir
            client_data["log_link_color"] = "blue" if client_data["log_path"] else "grey"

        # Refresh the UI
        refresh_long_query_section()

        status_label.config(text="Long Query Sync completed!", fg="green")
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")
        status_label.config(text=f"Error: {e}", fg="red")
    except Exception as e:
        print(f"Error syncing data: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def update_long_query_ui(long_query_data, blocking_session_data=None):
    """
    Update the UI for Long Sessions and Blocking Sessions horizontally with a fixed width.
    """
    
    # Clear the frame content
    for widget in long_query_frame.winfo_children():
        widget.destroy()

    # Add the "ARISU" heading
    heading_label = tk.Label(long_query_frame, text="ARISU", font=("Helvetica", 14, "bold"))
    heading_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

    # Create two frames for horizontal layout
    left_frame = tk.Frame(long_query_frame, width=450)
    right_frame = tk.Frame(long_query_frame, width=450)

    left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    long_query_frame.columnconfigure(0, weight=1)
    long_query_frame.columnconfigure(1, weight=1)

    # Add the "Long Sessions" section to the left frame
    tk.Label(left_frame, text="Long Sessions", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))

    if long_query_data:
        for line in long_query_data:
            try:
                # Check if MINS_RUNNING > 60
                if "MINS_RUNNING" not in line and float(line.split()[-1]) > 60:
                    text_color = "red"  # Set text color to red
                else:
                    text_color = "black"

                tk.Label(
                    left_frame,
                    text=line,
                    anchor="w",
                    font=("Courier", 8),
                    fg=text_color
                ).pack(anchor="w", fill="x")
            except ValueError:
                # In case of header or invalid data
                tk.Label(left_frame, text=line, anchor="w", font=("Courier", 8)).pack(anchor="w", fill="x")
    else:
        tk.Label(left_frame, text="No data available.", font=("Helvetica", 8)).pack(anchor="w")

    # Add the "Blocking Sessions" section to the right frame
    tk.Label(right_frame, text="Blocking Sessions", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))

    if blocking_session_data:
        for line in blocking_session_data:
            tk.Label(right_frame, text=line, anchor="w", font=("Courier", 8)).pack(anchor="w", fill="x")
    else:
        tk.Label(right_frame, text="No data available.", font=("Helvetica", 8)).pack(anchor="w")


def parse_blocking_sessions_log(log_dir):
    """
    Parse Blocking Sessions data from the log files.
    - After `###LOCKING SESSION###`, skip the first occurrence of `***************`.
    - Skip a blank line after it.
    - Collect content until encountering another blank line or another `***************`.
    - Skip lines containing `BLOCKER SID 'ISBLOCKING' BLOCKEE SID` and dashed lines.
    - Replace 'is blocking' with 'is_blocking'.
    - Exclude any part of a row that is not numeric or 'is_blocking'.
    """
    blocking_session_data = []
    try:
        print(f"DEBUG: Starting parsing in directory: {log_dir}")
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            print(f"DEBUG: Processing file: {file_name}")

            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the Blocking Sessions section
                    if "LOCKING SESSION" in stripped_line:
                        print(f"DEBUG: Found 'LOCKING SESSION' section in file: {file_name}")
                        start_collecting = True
                        skip_stars_line = True  # Skip the first stars line
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                print("DEBUG: Skipping stars line.")
                                continue  # Skip the stars line
                            if not stripped_line:  # Skip the blank line after the stars
                                print("DEBUG: Skipping blank line after stars.")
                                skip_stars_line = False
                                continue

                        # Skip the header line `BLOCKER SID 'ISBLOCKING' BLOCKEE SID`
                        if "BLOCKER" in stripped_line and "BLOCKEE" in stripped_line:
                            print("DEBUG: Skipping header line.")
                            continue

                        # Skip dashed lines (e.g., `---`)
                        if stripped_line.startswith("-"):
                            print("DEBUG: Skipping dashed line.")
                            continue

                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            print("DEBUG: Stopping parsing after blank or stars line.")
                            break

                        # Handle "no rows selected" case
                        if "no rows selected" in stripped_line.lower():
                            print("DEBUG: No rows selected found.")
                            return [("No rows selected.", False)]  # Return this as plain text

                        # Replace 'is blocking' with 'is_blocking'
                        if "is blocking" in stripped_line:
                            print("DEBUG: Found 'is blocking', converting to 'is_blocking'.")
                            stripped_line = stripped_line.replace("is blocking", "is_blocking")

                        # Filter the row to keep only numeric values and "is_blocking"
                        columns = stripped_line.split()
                        filtered_columns = [col for col in columns if col.isdigit() or col == "is_blocking"]

                        if filtered_columns:
                            filtered_line = "\t".join(filtered_columns)
                            print(f"DEBUG: Adding filtered line: {filtered_line}")
                            blocking_session_data.append(filtered_line)
                        else:
                            print(f"DEBUG: Skipping line with no valid data: {stripped_line}")

        # If no data is collected, explicitly return "No rows selected"
        if not blocking_session_data:
            print("DEBUG: No blocking session data found.")
            return [("No rows selected.", False)]

        print(f"DEBUG: Completed parsing. Total entries collected: {len(blocking_session_data)}")
        return blocking_session_data

    except FileNotFoundError:
        print(f"ERROR: Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"ERROR: Unexpected error occurred while parsing: {e}")
        return [f"Error: {e}"]

def parse_mv_not_refreshed_log(log_dir):
    """
    Parse MV Not Refreshed data from the log files.
    Extract and process LAST_REFRESH_DATE column values, replacing whitespace with underscores.
    Skip lines containing specific headers or starting with dashes.
    """
    mv_not_refreshed_data = []
    try:
        # Get today's date for comparison
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(f"Current Date (SYSDATE): {current_date}")

        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            print(f"Processing file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the MV Not Refreshed section
                    if "MV LAST REFRESH TIME" in stripped_line:
                        start_collecting = True
                        skip_stars_line = True
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                continue
                            if not stripped_line:
                                skip_stars_line = False
                                continue

                        # Skip header lines and dashed lines
                        if re.search(r"\bMVIEW_NAME.*LAST_REFRESH_DATE\b", stripped_line) or stripped_line.startswith("-"):
                            print("DEBUG: Skipping header or dashed line.")
                            continue

                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            print("DEBUG: Stopping log processing.")
                            break

                        # Handle rows without a valid date
                        parts = stripped_line.split()
                        if len(parts) >= 3:
                            owner = parts[0]
                            mview_name = " ".join(parts[1:-2])  # Handle names with spaces
                            last_refresh_timestamp = parts[-2] + "_" + parts[-1]  # Replace space with _
                            try:
                                last_refresh_date = last_refresh_timestamp.split("_")[0]
                                if "-" in last_refresh_date and len(last_refresh_date) == 10:
                                    is_red = last_refresh_date != current_date
                                else:
                                    is_red = False
                            except Exception as e:
                                print(f"Error processing date: {last_refresh_timestamp} - {e}")
                                is_red = False
                            mv_not_refreshed_data.append((f"{owner} {mview_name} {last_refresh_timestamp}", is_red))
                        else:
                            mv_not_refreshed_data.append((stripped_line, False))
        return mv_not_refreshed_data
    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"Error parsing MV Not Refreshed: {e}")
        return [(f"Error: {e}", False)]

def parse_current_archive_generated(log_dir):
    """
    Parse CURRENT ARCHIVE GENERATED data from the log files.
    - Highlight rows where `DAY` matches the system date using the `is_red` flag.
    """
    import datetime

    current_archive_data = []
    sysdate = datetime.datetime.now().strftime("%Y-%m-%d")  # Get current system date

    try:
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the Current archive generated section
                    if "CURRENT ARCHIVE GENERATED" in stripped_line:
                        start_collecting = True
                        skip_stars_line = True  # Skip the first stars line
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                continue  # Skip the stars line
                            if not stripped_line:  # Skip the blank line after the stars
                                skip_stars_line = False
                                continue

                        # Skip lines starting with `DAY`
                        if stripped_line.startswith("DAY"):
                            continue
                        # Skip lines starting with dashes
                        if stripped_line.startswith("-"):
                            continue

                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            break

                        # Exclude the second column (NUM_ARCHIVES_GENERATED) from the output
                        columns = stripped_line.split()
                        if len(columns) >= 3:  # Ensure at least 3 columns are present
                            # Combine the first and last columns
                            day, archive_size = columns[0], columns[2]
                            row_text = f"{day}\t{archive_size}"
                            is_red = day == sysdate  # Highlight if DAY matches sysdate
                            current_archive_data.append((row_text, is_red))

        return current_archive_data

    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"Error parsing Current archive generated: {e}")
        return [(f"Error: {e}", False)]


def parse_temp_tablespace_usage(log_dir):
    """
    Parse TEMP USAGE data from the log files.
    - Look for the section after `###TEMP TABLESPACE ###`.
    - Skip the first stars (`***************`) line and a blank line after it.
    - Exclude the first column (TABLESPACE) and combine the remaining columns as output.
    - Highlight the `USED_MB` cell if it is 50% or greater of `TOTAL_MB`.
    """
    temp_tablespace_data = []
    try:
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                skip_stars_line = False

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the Temp tablespace section
                    if "TEMP TABLESPACE" in stripped_line:
                        start_collecting = True
                        skip_stars_line = True  # Skip the first stars line
                        continue

                    if start_collecting:
                        # Skip the first stars line and the following blank line
                        if skip_stars_line:
                            if stripped_line.startswith("*"):
                                continue  # Skip the stars line
                            if not stripped_line:  # Skip the blank line after the stars
                                skip_stars_line = False
                                continue

                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            break
                        # Skip header and separator lines
                        if stripped_line.startswith("TABLESPACE") or stripped_line.startswith("-"):
                            continue

                        # Process and exclude the first column
                        columns = stripped_line.split()
                        if len(columns) >= 4:  # Ensure at least 4 columns are present
                            try:
                                total_mb = float(columns[1])
                                used_mb = float(columns[2])
                                is_red = used_mb >= (0.5 * total_mb)  # Check if USED_MB is 50% or greater of TOTAL_MB
                                filtered_line = f"{columns[1]}\t{columns[2]}\t{columns[3]}"
                                temp_tablespace_data.append((filtered_line, is_red))
                            except ValueError:
                                # If parsing fails, add the line without the red flag
                                temp_tablespace_data.append((f"{columns[1]}\t{columns[2]}\t{columns[3]}", False))

        return temp_tablespace_data

    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"Error parsing Temp Tablespace Usage: {e}")
        return [(f"Error: {e}", False)]


import re

def parse_undo_segment_status(log_dir):
    """
    Parse UNDO SEGMENT STATUS data from the log files.
    - Look for the section after `###UNDO SEGMENT STATUS###`.
    - Start collecting data after encountering headers `TABLESPACE STATUS SUM_MB COUNTS` 
      or `TABLESPACE STATUS SUM_IN_MB COUNTS`.
    - Handles extra whitespaces before, after, or between the columns.
    - Excludes the first column from the collected data.
    - Flags rows with `STATUS = ACTIVE` and `SUM_MB >= 20000`.

    Args:
        log_dir (str): The directory containing the log files.

    Returns:
        list: A list of tuples, where each tuple contains:
              - row data as a string
              - a boolean indicating if the row should be highlighted (True for red).
    """
    undo_segment_data = []
    try:
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                start_collecting = False
                section_found = False  # Indicates `UNDO SEGMENT STATUS` section was found
                blank_line_count = 0  # Track blank lines

                for line in lines:
                    stripped_line = line.strip()

                    # Detect the start of the UNDO SEGMENT STATUS section
                    if not section_found and "UNDO SEGMENT STATUS" in stripped_line:
                        section_found = True
                        continue

                    # Check for specific headers
                    if section_found and re.match(
                        r"^\s*TABLESPACE\s+STATUS\s+(SUM_MB|SUM_IN_MB)\s+COUNTS\s*$", stripped_line
                    ):
                        start_collecting = True
                        continue

                    if start_collecting:
                        # Stop parsing if another blank line or stars line is found
                        if not stripped_line or stripped_line.startswith("*"):
                            break

                        # Skip separator lines
                        if stripped_line.startswith("-"):
                            continue

                        # Increment blank line count and stop parsing on the second blank line
                        if not stripped_line:
                            blank_line_count += 1
                            if blank_line_count == 3:
                                break
                            continue

                        # Exclude the first column
                        columns = stripped_line.split()
                        if len(columns) > 1:  # Ensure there is more than one column
                            try:
                                status = columns[1]  # STATUS column
                                sum_mb = float(columns[2])  # SUM_MB or SUM_IN_MB column

                                # Check if the row meets the red flag condition
                                is_red = status.upper() == "ACTIVE" and sum_mb >= 20000

                                # Append the row data and red flag
                                stripped_line = " ".join(columns[1:])  # Exclude the first column
                                undo_segment_data.append((stripped_line, is_red))
                            except (ValueError, IndexError):
                                # If parsing fails, add the line without the red flag
                                undo_segment_data.append((stripped_line, False))

        # If no data was collected, indicate no rows were found
        if not undo_segment_data:
            undo_segment_data.append(("No data available.", False))

        return undo_segment_data

    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return [("Log directory not found.", False)]
    except Exception as e:
        print(f"Error parsing UNDO Segment Status: {e}")
        return [(f"Error: {e}", False)]



def extract_between_markers(content, start_markers, end_markers):
    """
    Extract data between start and end markers, excluding unwanted paths and skipping the 'Filesystem' column.
    """
    lines = content.splitlines()
    start_idx = next(
        (idx for idx, line in enumerate(lines) if any(marker in line for marker in start_markers)),
        None,
    )
    end_idx = next(
        (idx for idx, line in enumerate(lines) if any(marker in line for marker in end_markers)),
        None,
    )

    # Exclude unwanted paths
    exclude_paths = [
        "/run/media/oracle/RHEL-8-2-0-BaseOS-x86_64",
        "/run/media/oracle/RHEL-7.9 Server.x86_64"
    ]

    def is_valid_line(line):
        return not any(excluded in line for excluded in exclude_paths) and line.strip()

    def remove_filesystem_column(line):
        columns = line.split()
        if columns and columns[0].lower() == "filesystem":
            return None  # Skip header row
        return " ".join(columns[1:])  # Skip the first column

    if start_idx is not None:
        data_lines = lines[start_idx + 1:end_idx] if end_idx else lines[start_idx + 1:]
        filtered_lines = filter(is_valid_line, data_lines)
        cleaned_lines = [remove_filesystem_column(line) for line in filtered_lines if line]
        extracted_data = "\n".join(line for line in cleaned_lines if line)

        # Log the extracted data
        logging.debug(f"Extracted Data between markers ({start_markers}, {end_markers}): {extracted_data}")
        return extracted_data

    logging.debug(f"No data found between markers ({start_markers}, {end_markers})")
    return None


def show_disk_utilization_section():
    print("Switching to Disk Utilization Section")  # Debugging
    hide_all_sections()
    disk_utilization_frame.pack(fill="both", expand=True)
    refresh_disk_utilization_section()

def setup_scrollable_frame(parent):
    """
    Sets up a scrollable frame within the given parent widget.
    Returns a frame that can be populated with widgets.
    """
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure canvas and scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Add scrollable frame to the canvas
    scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind events to update the canvas scrolling region
    scrollable_frame.bind("<Configure>", on_frame_configure)

    def on_mouse_scroll(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Bind mouse scrolling
    canvas.bind_all("<MouseWheel>", on_mouse_scroll)

    return scrollable_frame


def refresh_disk_utilization_section():
    """
    Refreshes the Disk Utilization section and dynamically creates log links for each client.
    """
    global client_disk_utilization_data

    # Clear existing widgets in the Disk Utilization Frame
    for widget in disk_utilization_frame.winfo_children():
        widget.destroy()

    # Add a scrollable frame
    scrollable_frame = setup_scrollable_frame(disk_utilization_frame)

    current_row = 1
    for client_data in client_disk_utilization_data:
        client = client_data["name"]

        # Add client heading
        client_heading_label = tk.Label(
            scrollable_frame,
            text=f"   {client}",
            font=("Arial", 14, "bold"),
            fg="black"
        )
        client_heading_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Handle log link
        log_file = client_data.get("log_path")
        log_text = "View Log (Sync Required)" if not log_file else f"Long Query Log ({os.path.basename(log_file)})"
        log_link = tk.Label(
            scrollable_frame,
            text=log_text,
            font=("Arial", 10),
            fg="grey" if not log_file else "blue",
            cursor="arrow" if not log_file else "hand2"
        )

        if log_file:
            log_link.bind("<Button-1>", lambda e, path=log_file: open_log_file(path))
            log_link.configure(fg="blue")
        log_link.grid(row=current_row, column=3, sticky="e", padx=10)
        current_row += 1

        # Add Production Server Section
        prod_heading = tk.Label(
            scrollable_frame,
            text="Production Server",
            font=("Arial", 11),
            fg="black"
        )
        prod_heading.grid(row=current_row, column=0, sticky="w", padx=10, pady=(5, 0))

        prod_frame = tk.Frame(scrollable_frame)
        prod_frame.grid(row=current_row + 1, column=0, padx=10, pady=10, sticky="nsew")
        if client_data.get("production"):
            create_table(prod_frame, client_data["production"])
        else:
            tk.Label(prod_frame, text="No Data Available", font=("Arial", 10, "italic"), fg="gray").grid(row=1, column=0)

        # Add Backup Server Section
        backup_heading = tk.Label(
            scrollable_frame,
            text="Backup Server",
            font=("Arial", 11),
            fg="black"
        )
        backup_heading.grid(row=current_row, column=1, sticky="w", padx=10, pady=(5, 0))

        backup_frame = tk.Frame(scrollable_frame)
        backup_frame.grid(row=current_row + 1, column=1, padx=10, pady=10, sticky="nsew")
        if client_data.get("backup"):
            create_table(backup_frame, client_data["backup"])
        else:
            tk.Label(backup_frame, text="No Data Available", font=("Arial", 10, "italic"), fg="gray").grid(row=1, column=0)

        # Add Load Average Section
        load_avg_heading = tk.Label(
            scrollable_frame,
            text="Load Average",
            font=("Arial", 11),
            fg="black"
        )
        load_avg_heading.grid(row=current_row, column=2, sticky="w", padx=10, pady=(5, 0))

        load_avg_frame = tk.Frame(scrollable_frame)
        load_avg_frame.grid(row=current_row + 1, column=2, padx=10, pady=10, sticky="nsew")

        if client_data.get("load_average"):
            try:
                # Extract and convert the load average value to float
                load_average_value = float(client_data["load_average"])
        
                # Set colors based on the value
                bg_color = "red" if load_average_value >= 1 else None
                fg_color = "white" if load_average_value >= 1 else "black"
            except ValueError:
                # Handle cases where load average is not a valid float
                load_average_value = client_data["load_average"]
                bg_color = None
                fg_color = "black"

            tk.Label(
                load_avg_frame,
                text=str(client_data["load_average"]),  # Always display as string
                font=("Courier", 10),
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=2,
                bg=bg_color,  # Apply background color for high load average
                fg=fg_color   # Apply foreground color
            ).grid(row=1, column=0, sticky="nsew")
        else:
            tk.Label(
                load_avg_frame,
                text="No Data Available",
                font=("Arial", 10, "italic"),
                fg="gray",
                borderwidth=0,
                relief="flat",
                padx=5,
                pady=2
            ).grid(row=1, column=0, sticky="nsew")


        current_row += 2






# Ensure `enable_log_links()` is called after sync completion.

 

def create_table(parent_frame, content):
    """
    Creates a table from the provided content within the specified frame,
    excluding the 'Filesystem' column.
    """
    try:
        lines = content.splitlines()
        for row_idx, line in enumerate(lines):
            # Normalize spacing and split columns
            columns = line.replace("Mounted on", "Mounted_on").split()
            if "Filesystem" in columns:  # Skip header row
                continue
            elif row_idx == 0:  # Ensure first row is not parsed as data
                continue

            row_highlight = False  # Flag to determine if the row needs highlighting

            # Check if the row contains `Use%` >= 90%
            if len(columns) > 3:  # Ensure there are enough columns
                try:
                    # Extract `Use%` value, handling cases with unexpected formats
                    use_percent_str = columns[3].strip('%')
                    if use_percent_str.isdigit():
                        use_percent = int(use_percent_str)
                        if use_percent >= 90:
                            row_highlight = True  # Mark row for highlighting
                except (ValueError, IndexError):
                    logging.warning(f"Unable to parse Use% value in row: {line}")

            # Create cells for each column
            for col_idx, col_value in enumerate(columns):
                display_value = col_value.replace("Mounted_on", "Mounted on")  # Restore "Mounted on"
                cell = tk.Label(
                    parent_frame,
                    text=display_value,
                    font=("Courier", 10),
                    borderwidth=1,
                    relief="solid",
                    padx=5,
                    pady=2
                )
                # Apply row highlighting if necessary
                if row_highlight:
                    cell.config(bg="red", fg="white")
                cell.grid(row=row_idx, column=col_idx, sticky="nsew")  # Start from row=1 for data
    except Exception as e:
        logging.error(f"Error creating table: {e}")

def fetch_client_load_average(client_directory):
    """
    Fetches load average for a client from the latest log file and grants necessary permissions.
    """
    try:
        # List all log files in the directory
        log_files = [
            os.path.join(client_directory, f)
            for f in os.listdir(client_directory)
            if f.endswith(".log") or f.endswith(".txt")
        ]

        # If no log files found, return a default message
        if not log_files:
            return "No Load Average Data"

        # Find the latest log file
        latest_log = max(log_files, key=os.path.getmtime)

        # Grant full permissions to the latest log file
        try:
            os.chmod(latest_log, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # Full permissions
            logging.info(f"Granted full permissions to: {latest_log}")
        except Exception as e:
            logging.error(f"Failed to grant permissions for {latest_log}: {e}")

        # Read the latest log file to extract load average
        with open(latest_log, "r", encoding="utf-8") as file:
            for line in file:
                if "load average" in line.lower():
                    return line.split("load average:")[-1].strip()

        return "No Load Average Data"

    except Exception as e:
        logging.error(f"Error fetching load average: {e}")
        return "No Load Average Data"

def extract_first_load_average(content, start_marker):
    """
    Extract the first load average value from the content.
    """
    for line in content.splitlines():
        if start_marker in line:
            load_avg_values = line.split("load average:")[-1].strip().split(",")
            return load_avg_values[0].strip() if load_avg_values else "No Data Found"
    return "No Data Found"




def sync_disk_utilization_data():
    """
    Syncs Disk Utilization data for Production, Backup, and Load Average sections dynamically for all clients.
    Handles permission issues, missing directories, and processes directory contents dynamically.
    """
    global client_disk_utilization_data

    logging.info("Starting Disk Utilization data sync...")

    # Run the external script to download the longquery logs
    try:
        print("Running pydash_disk_utilization.py...")
        script_path = os.path.join(base_directory, "pydash_disk_utilization.py")
        print("Script Path:", script_path)

        subprocess.run(["python", script_path], check=True)  # Execute the script
        print("Disk utilization log file downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        status_label.config(text="Error running script.", fg="red")
        return

    # Iterate over the list of client data
    for client_data in client_disk_utilization_data:
        client = client_data["name"]
        client_dir = os.path.join(base_directory, "attachments", client, "longquery")
        logging.info(f"Processing client: {client}, Directory: {client_dir}")

        # Ensure the directory exists
        if not os.path.exists(client_dir):
            logging.warning(f"Client directory not found: {client_dir}")
            client_data.update({
                "production": "Directory Not Found",
                "backup": "Directory Not Found",
                "load_average": "Directory Not Found",
                "log_path": None,  # Ensure log_path is reset
            })
            continue

        try:
            # Grant permissions to the client directory and its contents
            os.chmod(client_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            logging.info(f"Granted permissions to directory: {client_dir}")

            for root, dirs, files in os.walk(client_dir):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                for f in files:
                    file_path = os.path.join(root, f)
                    os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        except Exception as e:
            logging.error(f"Error granting permissions for {client_dir}: {e}")
            client_data.update({
                "production": "Permission Error",
                "backup": "Permission Error",
                "load_average": "Permission Error",
                "log_path": None,  # Reset log_path on error
            })
            continue

        try:
            # Process files inside the longquery folder
            files_in_dir = [
                os.path.join(client_dir, f)
                for f in os.listdir(client_dir)
                if os.path.isfile(os.path.join(client_dir, f))
            ]
            if not files_in_dir:
                logging.warning(f"No files found in directory: {client_dir}")
                client_data.update({
                    "production": "No Files Found",
                    "backup": "No Files Found",
                    "load_average": "No Files Found",
                    "log_path": None,  # Reset log_path
                })
                continue

            # Read the first valid file
            with open(files_in_dir[0], "r") as file:
                file_content = file.read()

            # Extract data
            production_data = extract_between_markers(file_content, ["PRODUCTION SERVER DISK SPACE START"], ["PRODUCTION SERVER DISK SPACE END"])
            backup_data = extract_between_markers(file_content, ["BACKUP SERVER DISK SPACE START"], ["BACKUP SERVER DISK SPACE END"])
            load_average = extract_first_load_average(file_content, "load average:")

            # Update client data
            client_data.update({
                "production": production_data if production_data else "No Data Found",
                "backup": backup_data if backup_data else "No Data Found",
                "load_average": load_average if load_average else "No Data Found",
                "log_path": files_in_dir[0],  # Update log_path to the first file found
            })

            logging.info(f"Updated client data: {client_data}")

        except Exception as e:
            logging.error(f"Unexpected error syncing data for client {client}: {e}")
            client_data.update({
                "production": "Error",
                "backup": "Error",
                "load_average": "Error",
                "log_path": None,  # Reset log_path on error
            })

    logging.info("Disk Utilization Sync completed successfully.")
    refresh_disk_utilization_section()

import threading

def sync_action():
    """
    Sync action determines which section is visible and syncs data accordingly.
    Updates the `status_label` with appropriate messages during and after syncing.
    Each message is exclusive to the section currently being synced.
    """
    def sync_task():
        try:
            # Sync Tablespaces section
            if tablespace_frame.winfo_ismapped():
                root.after(0, lambda: status_label.config(text="Syncing Tablespaces...", fg="blue"))
                sync_tablespace_data()
                root.after(0, lambda: status_label.config(text="Tablespaces data synced successfully.", fg="green"))

            # Sync RMAN Backup section
            elif rman_backup_frame.winfo_ismapped():
                root.after(0, lambda: status_label.config(text="Syncing RMAN Backup data...", fg="blue"))
                sync_rman_backup()
                root.after(0, lambda: status_label.config(text="RMAN Backup data synced successfully.", fg="green"))

            # Sync ARC Gap section
            elif arc_gap_frame.winfo_ismapped():
                root.after(0, lambda: status_label.config(text="Syncing ARC Gap and Apply data...", fg="blue"))
                sync_arc_gap()
                sync_biba_log()
                update_gap_field_for_clients(["VMART"])
                root.after(0, lambda: status_label.config(text="ARC Gap data synced successfully.", fg="green"))

            # Sync Long Query section
            elif long_query_frame.winfo_ismapped():
                root.after(0, lambda: status_label.config(text="Syncing Long Query data...", fg="blue"))
                sync_long_query_data()
                root.after(0, lambda: status_label.config(text="Long Query data synced successfully.", fg="green"))

            # Sync Disk Utilization section
            elif disk_utilization_frame.winfo_ismapped():
                root.after(0, lambda: status_label.config(text="Syncing Disk Utilization data...", fg="blue"))
                sync_disk_utilization_data()
                root.after(0, lambda: status_label.config(text="Disk Utilization data synced successfully.", fg="green"))

            else:
                root.after(0, lambda: status_label.config(text="No active section for syncing.", fg="red"))

        except Exception as e:
            root.after(0, lambda: status_label.config(text=f"Error during syncing: {e}", fg="red"))
            print(f"Error: {e}")

    # Start sync operation in a separate thread
    sync_thread = threading.Thread(target=sync_task)
    sync_thread.daemon = True  # Ensure thread exits when the main program ends
    sync_thread.start()






# Ensure fields are visible initially
refresh_arc_gap_section()

# Start the Tkinter main loop
root.mainloop()
if __name__ == "__main__":
    root.mainloop()



