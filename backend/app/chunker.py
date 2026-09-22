def chunk_code(path, language, content, max_lines=80, overlap=12):
    lines = content.splitlines()
    chunks = []
    step = max_lines - overlap
    for start in range(0, len(lines), step):
        end = min(start + max_lines, len(lines))
        text = "\n".join(lines[start:end]).strip()
        if text:
            chunks.append({
                "path": path, "language": language,
                "start_line": start + 1, "end_line": end, "content": text
            })
        if end == len(lines):
            break
    return chunks
