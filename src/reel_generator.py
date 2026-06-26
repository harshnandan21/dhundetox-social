"""Create a 20-second Ken Burns reel from a still image using ffmpeg."""
import os
import random
import subprocess
import cloudinary
import cloudinary.uploader
import imageio_ffmpeg

FFMPEG       = imageio_ffmpeg.get_ffmpeg_exe()
REEL_DURATION = 20
MUSIC_DIR    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music")
OUTPUT_DIR   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def _zoom_filter(duration=REEL_DURATION, size="1080x1920", fps=25, max_zoom=1.12):
    frames = int(duration * fps)
    half   = frames // 2
    step   = (max_zoom - 1.0) / half
    z_expr = f"if(lte(on,{half}),1+{step:.7f}*on,{max_zoom:.4f}-{step:.7f}*(on-{half}))"
    return (
        f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s={size}:fps={fps}"
    )


def create_reel(image_path, output_name=None):
    """Render a 20s Ken Burns reel from image_path. Returns output video path."""
    music_files = [
        f for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))
    ] if os.path.exists(MUSIC_DIR) else []

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base        = output_name or os.path.basename(image_path).replace(".jpg", "_reel.mp4")
    output_path = os.path.join(OUTPUT_DIR, base)
    fade_out    = REEL_DURATION - 2.5

    if music_files:
        music_path = os.path.join(MUSIC_DIR, random.choice(music_files))
        vf = (
            f"[0:v]{_zoom_filter()}[v];"
            f"[1:a]afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out}:d=2.5[a]"
        )
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-r", "25", "-i", image_path,
            "-i", music_path,
            "-filter_complex", vf,
            "-map", "[v]", "-map", "[a]",
        ]
    else:
        vf = f"[0:v]{_zoom_filter()}[v]"
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-r", "25", "-i", image_path,
            "-filter_complex", vf,
            "-map", "[v]",
        ]

    cmd += [
        "-t", str(REEL_DURATION),
        "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p", "-b:v", "2M",
        output_path,
    ]

    print(f"Rendering reel from {os.path.basename(image_path)}...")
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Reel saved: {output_path}")
    return output_path


def upload_to_cloudinary(file_path, folder="dhundetox", resource_type="video"):
    """Upload a file to Cloudinary and return the permanent public URL."""
    print(f"Uploading {os.path.basename(file_path)} to Cloudinary...")
    result = cloudinary.uploader.upload(
        file_path,
        folder=folder,
        resource_type=resource_type,
        quality="auto",
    )
    url = result["secure_url"]
    print(f"Cloudinary URL: {url}")
    return url
