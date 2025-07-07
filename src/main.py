import sys
import os
import cups
import time
import json
import mimetypes
from prompt_toolkit.shortcuts.dialogs import input_dialog, button_dialog, message_dialog
from prompt_toolkit.styles import Style

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def get_printer():
    conn = cups.Connection()
    printers = conn.getPrinters()

    for name, info in printers.items():
        device_uri = info.get("device-uri", "")
        if device_uri.startswith("usb://"):
            return conn, name, printers

    if printers:
        first_name = next(iter(printers))
        return conn, first_name, printers

    return None, None, printers

style = Style.from_dict({
    'dialog':             'bg:#007AB9',
    'dialog frame.label': 'bg:#ffffff #000000',
    'dialog.body':        'bg:#ffffff #000000',
    'dialog shadow':      'bg:#333333',
})

def FILE_INPUT():
    path = input_dialog(
        title="ᕕ( ᐛ )ᕗ  ~  P R I N T E R G E I S T  ~  ᕕ( ᐛ )ᕗ",
        text="* FILE PATH FOR PRINTING",
        style=style
    ).run()
    if path == None:
        sys.exit(0)
    return path

def MENU():
    application_menu = button_dialog(
        title="ᕕ( ᐛ )ᕗ  ~  P R I N T E R G E I S T  ~  ᕕ( ᐛ )ᕗ",
        text="""
            ----------------------------------------------------------------------
            Copyright (c) 2025 mvghasty - https://github.com/mvghasty/printergeist
            LICENSE: GNU General Public License, 2.0
            ----------------------------------------------------------------------
            """,
        buttons=[
            ('INIT', 1),
            ('EXIT', 2),
        ],
        style=style
    ).run()

    match application_menu:
        case 1:
            return FILE_INPUT()
        case 2:
            sys.exit(0)

def main():
    file_path = MENU()

    if not file_path or not os.path.isfile(file_path):
        message_dialog(
            title="Error",
            text="Invalid file path provided.",
            style=style
        ).run()
        sys.exit(1)

    conn, printer_name, printers_info = get_printer()
    if not printer_name:
        message_dialog(
            title="Error",
            text="No printer found.",
            style=style
        ).run()
        sys.exit(1)

    mime_type, _ = mimetypes.guess_type(file_path)
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    is_color = not ("gray" in printer_name.lower() or "bw" in printer_name.lower())

    message_dialog(
        title="PRINT REQUEST", 
        text= f""" 
            Archive: {file_name}
            MIME type: {mime_type}
            Size: {format_bytes(file_size)}
            Colorful: {"Yes" if is_color else "No"}
            ----------------------------------------------------------------------
            """,
        style=style
    ).run()

    print(f"[ * ] Sending request: {printer_name}...")

    try:
        job_id = conn.printFile(
            printer_name,
            file_path,
            f"PRINTERGEIST REQUEST - {file_name}",
            {"document-format": mime_type or "application/octet-stream"}
        )
        time.sleep(2)
    except cups.IPPError as e:
        message_dialog(
            title="ERROR",
            text=f"Request error for: {e}",
            style=style
        ).run()
        sys.exit(1)

    message_dialog(
        title="PRINT REQUEST",
        text=f"""
            [ ✓ ] Printing made successfully! Job ID: {job_id}")
            ----------------------------------------------------------------------
            CUPS DEBUG-LOG
            (JSON FORMAT)
            ----------------------------------------------------------------------
            {json.dumps(printers_info, indent=4, separators=(", ", " = "))}
            """,
        style=style
    ).run()
    
    print(json.dumps(printers_info, indent=4, separators=(", ", " = ")))

if __name__ == "__main__":
    main()
