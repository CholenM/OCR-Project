import os


TEXT_DIRECT_UPLOAD_TYPES = {"md", "txt", "csv"}


def dedupe_filename(filename: str, used_names: set) -> str:
    stem, ext = os.path.splitext(filename or "document")
    candidate = filename or "document"
    counter = 2
    while candidate.lower() in used_names:
        candidate = f"{stem} ({counter}){ext}"
        counter += 1
    used_names.add(candidate.lower())
    return candidate


def unique_upload_names(filenames):
    used = set()
    return [dedupe_filename(name, used) for name in filenames]


def is_text_direct_upload(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower().lstrip(".") in TEXT_DIRECT_UPLOAD_TYPES


def decode_text_upload(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")
