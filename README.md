# Transcriptor M4 Pro (macOS Nativo) 🚀

Herramienta de transcripción ultra-rápida y eficiente diseñada específicamente para equipos Apple Silicon (M1 a M4). Utiliza el framework MLX de Apple para obtener el máximo rendimiento del hardware local sin depender de la nube.

## ✨ Características Principales
- **Arquitectura de 2 Fases**: Extracción de audio vía FFmpeg + Transcripción MLX para evitar cuelgues de memoria.
- **Selector de Modelos**: Elige entre 5 niveles de precisión (desde Tiny hasta Turbo Q4) según tu necesidad de RAM y exactitud.
- **Interfaz Web Premium**: Diseño minimalista estilo macOS con efecto Glassmorphism.
- **Selección Nativa**: Integración con el Finder de macOS para elegir archivos desde cualquier directorio.
- **Privacidad Total**: Todo el procesamiento es 100% local. No se envían datos a internet.
- **Gestión de Temporales**: Botón de limpieza para eliminar archivos generados y mantener tu Mac impecable.

## 🛠️ Requisitos previos

Necesitas **FFmpeg** instalado para la extracción de audio.
```bash
brew install ffmpeg
```

## 🚀 Instalación y Uso

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/diegoeguz90/herramienta-transcripciones.git
   cd herramienta-transcripciones
   ```

2. **Configura el entorno**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. **Inicia la aplicación**:
   ```bash
   python3 web_app.py
   ```

4. **Accede**: Abre [http://localhost:8000](http://localhost:8000) en tu navegador.

## 📁 Estructura del Proyecto
- `web_app.py`: Servidor principal FastAPI.
- `cli_engine.py`: Motor de transcripción aislado en subproceso.
- `temp_results/`: Carpeta para archivos temporales (.md y .wav).
- `templates/`: Interfaz de usuario.

---
Desarrollado para la comunidad de usuarios de Apple Silicon. 🍎⚙️
