import yt_dlp
import os

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            # Filter formats to include all video formats
            video_formats = []
            for f in formats:
                # Include all video formats including those with separate audio
                if f.get('vcodec') != 'none':
                    format_info = {
                        'format_id': f.get('format_id', 'N/A'),
                        'ext': f.get('ext', 'N/A'),
                        'resolution': f.get('resolution', 'N/A'),
                        'filesize': f.get('filesize', 0),
                        'format_note': f.get('format_note', ''),
                        'fps': f.get('fps', 0),
                        'vcodec': f.get('vcodec', 'N/A'),
                        'acodec': f.get('acodec', 'N/A'),
                        'tbr': f.get('tbr', 0),  # Total bit rate
                    }
                    video_formats.append(format_info)

            # Sort formats by quality (resolution and bitrate)
            video_formats.sort(key=lambda x: (
                int(x['resolution'].split('x')[1]) if 'x' in str(x['resolution']) else 0,
                x['tbr']
            ), reverse=True)

            return {
                'title': info.get('title', 'Video'),
                'duration': info.get('duration', 0),
                'formats': video_formats
            }
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return None

def format_size(bytes):
    if not bytes:
        return 'N/A'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} GB"

def download_video(url, format_id, output_path='downloads'):
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',  # Automatically merge video and audio
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',  # Merge into MP4 format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nDownload completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\rDownloading... {d.get('_percent_str', '0%')}", end='')
    elif d['status'] == 'finished':
        print("\nProcessing completed file...")

def main():
    print("Enhanced YouTube Video Downloader")
    print("--------------------------------")

    while True:
        url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()

        if url.lower() == 'q':
            print("Goodbye!")
            break

        print("Fetching video information...")
        info = get_video_info(url)

        if not info:
            continue

        print(f"\nTitle: {info['title']}")
        print(f"Duration: {info['duration']} seconds")
        print("\nAvailable formats:")
        print("\nID | Resolution | Format | FPS | Size | Codecs | Note")
        print("-" * 80)

        # Display available formats
        for i, fmt in enumerate(info['formats'], 1):
            filesize = format_size(fmt['filesize'])
            fps = str(fmt['fps']) if fmt['fps'] else 'N/A'
            resolution = str(fmt['resolution'])
            codecs = f"V:{fmt['vcodec'][:4]}"
            if fmt['acodec'] != 'none':
                codecs += f"/A:{fmt['acodec'][:4]}"

            print(f"{i:2d} | {resolution:^10} | {fmt['ext']:^6} | {fps:^4} | {filesize:^8} | {codecs:^10} | {fmt['format_note']}")

        print("\nNote: Video will automatically be merged with best audio quality.")

        # Get user choice
        while True:
            try:
                choice = input("\nSelect format number (or 'b' to go back): ").strip()
                if choice.lower() == 'b':
                    break

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(info['formats']):
                    selected_format = info['formats'][choice_idx]
                    print(f"\nSelected: {selected_format['resolution']} - {selected_format['format_note']}")

                    # Create downloads directory if it doesn't exist
                    os.makedirs('downloads', exist_ok=True)

                    # Download video
                    download_video(url, selected_format['format_id'])
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"Error: {str(e)}")
                break

if __name__ == "__main__":
    main()
