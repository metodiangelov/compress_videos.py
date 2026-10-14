
from pathlib import Path
import shutil
import subprocess

# ===== SETTINGS =====
INPUT_DIR = Path(r"D:\Videos")  # Change this to your video folder
OUTPUT_DIR = INPUT_DIR / "compressed"

# Quality settings:
CRF = "26"          # Lower = better quality/larger files
PRESET = "medium"   # Slower presets can compress more efficiently

VIDEO_EXTENSIONS = {".mp4"}
# ====================


def main():
    # Check that the input folder exists
    if not INPUT_DIR.is_dir():
        print(f"ERROR: Folder not found: {INPUT_DIR}")
        return

    # Check that FFmpeg is installed and available in PATH
    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg is None:
        print("ERROR: FFmpeg was not found.")
        print("Install FFmpeg or add its bin folder to your Windows PATH.")
        return

    # Find MP4 files directly inside the input folder
    videos = sorted(
        file for file in INPUT_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in VIDEO_EXTENSIONS
    )

    if not videos:
        print(f"No MP4 files found in: {INPUT_DIR}")
        return

    # Create the destination folder
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(videos)} MP4 video(s).")
    print(f"Output folder: {OUTPUT_DIR}")
    print("Starting compression...\n")

    successful = 0
    failed = 0
    skipped = 0

    for index, video in enumerate(videos, start=1):
        output_file = OUTPUT_DIR / f"{video.stem}.mp4"

        print("=" * 60)
        print(f"[{index}/{len(videos)}] {video.name}")

        # Do not overwrite an existing compressed file
        if output_file.exists():
            print("SKIPPED: Output file already exists.")
            skipped += 1
            continue

        command = [
            ffmpeg,
            "-hide_banner",
            "-n",
            "-i", str(video),

            # Select the primary video and any audio streams.
            # Subtitles and other extra streams are not copied.
            "-map", "0:v:0",
            "-map", "0:a?",

            # H.265 / HEVC video for efficient compression
            "-c:v", "libx265",
            "-preset", PRESET,
            "-crf", CRF,
            "-tag:v", "hvc1",
            "-pix_fmt", "yuv420p",

            # AAC audio for broad device compatibility
            "-c:a", "aac",
            "-b:a", "160k",

            # Help the MP4 start playing before fully downloaded
            "-movflags", "+faststart",

            str(output_file)
        ]

        try:
            # FFmpeg will display its progress in the terminal
            subprocess.run(command, check=True)

            if output_file.exists() and output_file.stat().st_size > 0:
                original_mb = video.stat().st_size / (1024 * 1024)
                compressed_mb = output_file.stat().st_size / (1024 * 1024)
                reduction = (1 - compressed_mb / original_mb) * 100

                print(f"\nSUCCESS: {output_file.name}")
                print(f"Original size:   {original_mb:.1f} MB")
                print(f"Compressed size: {compressed_mb:.1f} MB")
                print(f"Size reduction:  {reduction:.1f}%")
                successful += 1
            else:
                print("ERROR: Output file was not created correctly.")
                failed += 1

        except subprocess.CalledProcessError:
            print(f"ERROR: Failed to compress {video.name}")
            failed += 1

    print("\n" + "=" * 60)
    print("COMPRESSION FINISHED")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Skipped:    {skipped}")
    print(f"Output:     {OUTPUT_DIR}")
    print("Original videos have not been deleted.")


if __name__ == "__main__":
    main()
