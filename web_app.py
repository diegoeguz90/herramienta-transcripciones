import os
import asyncio
import sys
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Transcripción Ultra-Simple")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_results")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Estado
app.state.transcription_status = "idle"
app.state.current_file = ""
app.state.progress_log = []
app.state.last_result_file = "" # Guardamos la ruta del último archivo generado

async def run_transcription_task(video_path: str, model: str):
    app.state.transcription_status = "processing"
    app.state.progress_log = [f"1. Usando modelo: {model.split('/')[-1]}", "2. Extrayendo audio..."]
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_temp = os.path.join(TEMP_DIR, "temp_audio.wav")
    output_filename = f"{base_name}_resultado.md"
    output_md = os.path.join(TEMP_DIR, output_filename)

    try:
        # Fase 1: Audio
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', '-i', video_path,
            '-ar', '16000', '-ac', '1', audio_temp,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()
        app.state.progress_log.append("3. Audio listo. Transcribiendo...")

        # Fase 2: Transcripción
        process_ml = await asyncio.create_subprocess_exec(
            sys.executable, os.path.join(BASE_DIR, "cli_engine.py"),
            audio_temp, output_md, model
        )
        await process_ml.wait()

        if os.path.exists(output_md):
            app.state.last_result_file = output_filename
            app.state.transcription_status = "completed"
            app.state.progress_log.append("✅ Finalizado con éxito.")
        else:
            app.state.transcription_status = "error"
            app.state.progress_log.append("❌ Error en el proceso.")

    except Exception as e:
        app.state.transcription_status = "error"
        app.state.progress_log.append(f"❌ Fallo: {str(e)}")
    finally:
        if os.path.exists(audio_temp):
            os.remove(audio_temp)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pick-file")
async def pick_file():
    """Lanza el diálogo de archivos usando AppleScript nativo (más estable que Tkinter)."""
    try:
        # Script para pedir un archivo y devolver su ruta POSIX
        script = 'set theFile to (choose file with prompt "Selecciona un video o audio")\nreturn POSIX path of theFile'
        process = await asyncio.create_subprocess_exec(
            'osascript', '-e', script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        file_path = stdout.decode().strip()
        
        if file_path:
            app.state.current_file = file_path
            return {"status": "success", "file_path": file_path}
    except Exception as e:
        print(f"Error en seleccionador: {e}")
        
    return {"status": "cancelled"}

@app.post("/start")
async def start_transcription(background_tasks: BackgroundTasks, request: Request):
    data = await request.json()
    model = data.get("model", "mlx-community/whisper-tiny-mlx")
    
    if not app.state.current_file or app.state.transcription_status == "processing":
        return JSONResponse({"status": "error"}, 400)
    background_tasks.add_task(run_transcription_task, app.state.current_file, model)
    return {"status": "started"}

@app.get("/status")
async def get_status():
    return {
        "status": app.state.transcription_status,
        "log": app.state.progress_log,
        "filename": app.state.last_result_file
    }

@app.get("/download")
async def download():
    if not app.state.last_result_file:
        return JSONResponse({"error": "No hay archivo"}, 404)
    file_path = os.path.join(TEMP_DIR, app.state.last_result_file)
    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=app.state.last_result_file)

@app.post("/clear")
async def clear():
    if app.state.last_result_file:
        file_path = os.path.join(TEMP_DIR, app.state.last_result_file)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    app.state.transcription_status = "idle"
    app.state.current_file = ""
    app.state.progress_log = []
    app.state.last_result_file = ""
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
