import re
import json
import os

# Standard message header: [6/23/26, 9:25:16 AM] Sender: Message content
WHATSAPP_MSG_REGEX = r'^\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M)\]\s([^:]+?):\s(.*)$'

# System event header: [6/23/26, 9:25:16 AM] System message without sender
WHATSAPP_SYSTEM_REGEX = r'^\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]\s.*$'

# Case-insensitive media placeholder regex
MEDIA_PLACEHOLDER_REGEX = re.compile(
    r'<?(?:image|video|audio|sticker|gif|document)\s+omitted>?',
    re.IGNORECASE
)

def parse_whatsapp_chat(file_path, relationship, contact_name):
    """
    Parses a WhatsApp export .txt file into retrieval/history memory pairs (incoming -> reply).
    Uses only Python standard library.
    """
    messages = []
    current_timestamp = None
    current_sender = None
    current_text_lines = []

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Chat file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            msg_match = re.match(WHATSAPP_MSG_REGEX, line_stripped)
            if msg_match:
                # Flush previous message
                if current_sender is not None:
                    text_block = "\n".join(current_text_lines).strip()
                    if text_block:
                        messages.append({
                            "timestamp": current_timestamp,
                            "sender": current_sender,
                            "text": text_block
                        })

                current_timestamp, current_sender, text = msg_match.groups()
                current_text_lines = [text]
            elif re.match(WHATSAPP_SYSTEM_REGEX, line_stripped):
                # System event line: flush previous message and discard this line without appending as multiline
                if current_sender is not None:
                    text_block = "\n".join(current_text_lines).strip()
                    if text_block:
                        messages.append({
                            "timestamp": current_timestamp,
                            "sender": current_sender,
                            "text": text_block
                        })
                current_sender = None
                current_timestamp = None
                current_text_lines = []
            else:
                # Genuine multiline continuation of current message
                if current_sender is not None:
                    current_text_lines.append(line_stripped)

    # Flush last message in file
    if current_sender is not None:
        text_block = "\n".join(current_text_lines).strip()
        if text_block:
            messages.append({
                "timestamp": current_timestamp,
                "sender": current_sender,
                "text": text_block
            })

    # Clean media placeholders and filter out empty messages
    valid_messages = []
    for msg in messages:
        cleaned_text = MEDIA_PLACEHOLDER_REGEX.sub("", msg["text"]).strip()
        if cleaned_text:
            msg["text"] = cleaned_text
            valid_messages.append(msg)

    # Group consecutive messages by sender and form Incoming -> You pairs
    pairs = []
    i = 0
    while i < len(valid_messages):
        # Ignore stray replies or messages starting with "You" without preceding incoming block
        if valid_messages[i]["sender"] == "You":
            i += 1
            continue

        incoming_block_msgs = []
        incoming_timestamp = valid_messages[i]["timestamp"]

        # Gather all consecutive incoming messages from contact
        while i < len(valid_messages) and valid_messages[i]["sender"] != "You":
            incoming_block_msgs.append(valid_messages[i]["text"])
            incoming_timestamp = valid_messages[i]["timestamp"]
            i += 1

        # Gather immediately following reply messages from "You"
        reply_block_msgs = []
        while i < len(valid_messages) and valid_messages[i]["sender"] == "You":
            reply_block_msgs.append(valid_messages[i]["text"])
            i += 1

        # If there is a matching reply from You, form a retrieval memory example
        if reply_block_msgs:
            pairs.append({
                "timestamp": incoming_timestamp,
                "relationship": relationship,
                "contact_name": contact_name,
                "incoming": "\n".join(incoming_block_msgs),
                "reply": "\n".join(reply_block_msgs)
            })

    return pairs

if __name__ == "__main__":
    raw_path = "data/raw/sample_chat.txt"
    processed_path = "data/processed/sample_pairs.json"

    print(f"Parsing {raw_path}...")
    pairs = parse_whatsapp_chat(raw_path, relationship="friend", contact_name="Prateek")

    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    with open(processed_path, 'w', encoding='utf-8') as out_f:
        json.dump(pairs, out_f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(pairs)} retrieval pairs at {processed_path}")
