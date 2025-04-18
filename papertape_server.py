from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import io
import requests
import matplotlib.font_manager as fm
import datetime

app = Flask(__name__)

def generate_paper_tape(text, bell_enabled=False):    
    # Define paper tape format
    
    # Font selection logic
    # Try setting a font that supports control pictures
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    #print(f"Available fonts: {available_fonts}")

    # Try to find a suitable monospace font
    for font in ["FreeMono", "Courier New"]:
        if any(f == font for f in available_fonts):
            plt.rcParams['font.family'] = font
            print(f"Using font: {font}")
            break
    else:
        print("Warning: No suitable font found. Using default.")
    
    header = "#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#00,#00,#00,#00,#00,#00,#00,#00,#00,#00"
    footer = "#00,#00,#00,#00,#00,#00,#00,#00,#00,#00,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff,#ff"

    # Function to convert hex codes (e.g., "#FF" → "11111111")
    def parse_hex_code(hex_str):
        if hex_str.startswith("#"):
            try:
                binary_value = format(int(hex_str[1:], 16), '08b')  # Convert hex to 8-bit binary
                #print(f"Processing HEX '{hex_str}' → {binary_value}")  # Debug statement
                return binary_value
            except ValueError:
                raise ValueError(f"Invalid hex code: {hex_str}")
        return None  # Not a hex code

    # Function to convert ASCII characters to 8-bit binary
    def convert_to_binary(char):
        binary_value = format(ord(char), '08b')  # Standard ASCII to 8-bit binary
        #print(f"Processing ASCII '{char}' → {binary_value}")  # Debug statement
        return binary_value

    def get_visual_char(c):
        if isinstance(c, str) and len(c) == 1:
            code = ord(c)
            # ASCII 0x00–0x1F and 0x7F → Unicode U+2400–U+241F and U+2421
            if 0x00 <= code <= 0x1F:
                return chr(0x2400 + code)
            elif code == 0x7F:
                return chr(0x2421)
            else:
                return c
        return c
    # Process header, message, and footer
    header_binary = [parse_hex_code(x) for x in header.split(",")]
    message_binary = [convert_to_binary(char) for char in text]

    # Optional bell sequence
    bell_sequence = []
    bell_visuals = []
    if bell_enabled:
        for c in [chr(0x00), chr(0x00), chr(0x07)]:
            bell_sequence.append(convert_to_binary(c))
            bell_visuals.append(get_visual_char(c))

    footer_binary = [parse_hex_code(x) for x in footer.split(",")]

    # Combine everything into the final sequence
    full_binary = header_binary + message_binary + bell_sequence + footer_binary
    full_char_sources = header.split(",") + list(text) + bell_visuals + footer.split(",")

    # Create a display-friendly char list
    visual_chars = []
    for char, code in zip(full_char_sources, full_binary):
        if len(char) == 1:
            # Normal ASCII char
            visual_chars.append(get_visual_char(char))
        elif char.startswith("#"):
            try:
                val = int(char[1:], 16)
                if 0x00 <= val <= 0x1F:
                    visual_chars.append(chr(0x2400 + val))  # control pictures
                elif val == 0x7F:
                    visual_chars.append(chr(0x2421))  # DEL
                elif val == 0xFF:
                    #visual_chars.append("█")  # full block for 0xFF
                    visual_chars.append("░")  # empty/light block for 0xFF
                else:
                    visual_chars.append("�")  # replacement char or whatever fallback you prefer
            except:
                visual_chars.append("?")

    ascii_punch_codes = [code for code in full_binary if code]    

    # Adjusted parameters for better spacing
    char_width = 0.7  # Reduced spacing between characters
    char_height = 8
    data_hole_radius = 0.25  # Keep holes round
    sprocket_hole_radius = 0.06  # Slightly smaller sprocket hole
    sprocket_y = 4.5
    y_spacing_factor = 0.82  # Reduce Y spacing (values < 1 squich, values > 1 stretch)

    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(len(ascii_punch_codes) * char_width, 2))
    ax.set_xlim(0, len(ascii_punch_codes) * char_width)
    ax.set_ylim(-1, char_height * y_spacing_factor)
    ax.set_aspect(1)  # Keep holes round

    # Draw tape background (yellow color)
    ax.add_patch(plt.Rectangle((0, -1), len(ascii_punch_codes) * char_width, char_height * y_spacing_factor + 1, color="#FFCC66", ec="black"))

    # Plot punched holes
    for i, (char, code) in enumerate(zip(visual_chars, ascii_punch_codes)):    
        x_offset = i * char_width + char_width / 2  # Adjust for closer spacing

        # Data holes (for ASCII bits)
        for j, bit in enumerate(reversed(code)):  # Reverse for correct orientation
            if bit == '1':
                ax.add_patch(plt.Circle((x_offset, j * y_spacing_factor), data_hole_radius, color="black", fill=True))  

        # Sprocket hole (between rows 4 and 5)
        ax.add_patch(plt.Circle((x_offset, sprocket_y * y_spacing_factor), sprocket_hole_radius, color="black", fill=True))

        # Print characters below the paper tape
        ax.text(
        x_offset,
        -1.5,
        char,
        fontsize=14,
        fontname="FreeMono",  # force use of control-picture-capable font
        ha="center",
        va="top",
        color="white",
        rotation=0
        )

    # Hide axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Save image to a BytesIO stream
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight', dpi=150, facecolor='#0f0f0f', transparent=False)
    img_io.seek(0)
    plt.close(fig)

    return img_io, len(ascii_punch_codes)

@app.route('/generate_paper_tape', methods=['POST'])
def generate_tape():

    system_prompt = (
        "You are a Teletype Model 33 ASR from the year 1979, connected to a mainframe via serial cable. "
        "You respond in short bursts of uppercase text as if printed on a paper tape. "
        "Your language is efficient, mechanical, and dry. Limit output to a few words per line, like a real teletype outputting ASCII on paper tape. "
        "Avoid punctuation unless absolutely necessary. Never apologize or explain. "
    )

    data = request.get_json()
    user_prompt = data.get("text", "")
    bell_enabled = data.get("bell", False)
    selected_model = data.get("model", "qwen2.5:0.5b")  # default fallback

    if not user_prompt:
        return "Error: No text provided", 400
    
    # Send request to local Ollama (Qwen)
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": selected_model,
        "prompt": user_prompt,
        "system": system_prompt,
        "options": {"temperature": 0.5},
        "stream": False
    })


    if not response.ok:
        return f"Ollama error: {response.text}", 500
    
    completion = response.json().get("response", "").strip()

    # Only allow 500 chars in the completion, if more, trigger a "JAM" and truncate
    max_chars = 500
    if len(completion) > max_chars:
        completion = completion[:max_chars]
        jam_detected = True
    else:
        jam_detected = False

    # Generate tape image from LLM response
    img_io, punch_count = generate_paper_tape(completion, bell_enabled)


    # This log code is not included in the Github release
    ip_addr = request.remote_addr
    truncated_completion = completion.strip().replace("\n", " ")[:500]
    model_used = selected_model  # pulled from the JSON earlier
    log_line = (
        f"[{datetime.datetime.now()}] "
        f"IP: {ip_addr} | MODEL: {model_used} | "
        f"PROMPT: {user_prompt.strip()} || COMPLETION: {truncated_completion}\n"
    )
    with open("usage.log", "a") as log_file:
        log_file.write(log_line)


    response = send_file(img_io, mimetype='image/png')
    response.headers['X-Punch-Count'] = str(punch_count)
    response.headers["X-Jam"] = "1" if jam_detected else "0"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
