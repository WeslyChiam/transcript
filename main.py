from fastapi import FastAPI, HTTPException, Depends 
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer
from moviepy import VideoFileClip
from typing import Annotated

import subprocess
import os
import sys
import httpx
import requests
import base64
import tempfile
import uuid

import models
import functions

app = FastAPI() 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/extract-audio-via-url")
async def extract_audio_via_url(url: str):
    """Extrac audio from url"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(url))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail={"error": str(response.text)})
        file_bytes = response.content
        if not functions.fileCheckup(file_byte=file_bytes):
            raise HTTPException(status_code=400, detail="Invalid url video format")
        audio_path = functions.convert_bytes_2_audio(file_bytes=file_bytes)
        return FileResponse(audio_path, filename=str(audio_path), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/extract-video-no-audio-via-url")
async def extract_video_no_audio_via_url(url: str):
    """Extract video with no audio from url"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(url))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail={"error": str(response.text)})
        file_bytes = response.content 
        if not functions.fileCheckup(file_byte=file_bytes):
            raise HTTPException(status_code=400, detail="Invalid url video format")
        video_path = functions.convert_bytes_2_vid_no_audio(file_bytes=file_bytes)
        return FileResponse(video_path, filename=str(video_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/transcript-via-url")
async def transcription_via_url_with_gpt(url: str):
    """Transcript audio from url using gptbot"""


if __name__ == "__main__":
    import uvicorn 
    port = 8000 
    uvicorn.run(app, host="0.0.0.0", port=port)


