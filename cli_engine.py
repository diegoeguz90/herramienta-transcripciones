import sys
import os
import mlx_whisper

def main():
    if len(sys.argv) < 3:
        return

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "mlx-community/whisper-tiny-mlx"

    try:
        # Transcripción directa
        result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=model)
        full_text = result.get("text", "").strip()

        # Ajuste de texto para evitar líneas infinitas (tokenization errors)
        import textwrap
        wrapped_text = textwrap.fill(full_text, width=100)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Transcripción\n\n{wrapped_text}")
            
    except Exception as e:
        with open(output_path + ".error", "w") as f:
            f.write(str(e))

if __name__ == "__main__":
    main()
