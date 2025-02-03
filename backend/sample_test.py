import subprocess
def home():
    try:
        result = subprocess.run(
            ["python", "videoTranslation.py", "--player", "Ohtani", "--play", "homeruns", '--language', 'English'],
            capture_output=True,
            text=True,
            check=True  # Raises an exception if the command fails
        )
        output_lines = result.stdout.strip().split("\n")  # Split into lines
        video_url = output_lines[-1]  # Get the last printed line
        print("Captured Video URL:", video_url)
        return video_url  # Return the URL if needed
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)  # Print the actual error message from the script

if __name__ == '__main__':
    home()