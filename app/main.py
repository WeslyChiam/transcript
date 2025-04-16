from fastapi import FastAPI, HTTPException, Depends, Query 
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from moviepy import VideoFileClip
from openai import OpenAI, OpenAIError
from typing import Annotated, Optional

import base64
import httpx
import json
import os
import requests
import subprocess
import sys
import tempfile
import uuid

import functions
import models
import prompt

app = FastAPI() 

bearer_scheme = HTTPBearer()

@app.post("/extract-audio-via-url")
async def extract_audio_via_url(url: str):
    """Extrac audio from url"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), timeout=30)
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
async def transcription_via_url_with_gpt(
    url: str, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    user_id: str = Query(default="dev-12980912"),
):
    """Transcript audio from url using gptbot"""
    token = credentials.credentials 
    async with httpx.AsyncClient() as client:
        response = await client.get(str(url))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail={"error": str(response.text)})
    file_bytes = response.content
    if not functions.fileCheckup(file_byte=file_bytes):
        raise HTTPException(status_code=400, detail="Invalid url video format")
    audio_path = functions.convert_bytes_2_audio(file_bytes=file_bytes)

    # with open(audio_path, "rb") as audio_file: 
    #     audio_bytes = audio_file.read()
    #     audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    # os.remove(audio_path)

    # if user_id is None:
    #     user_id = "dev-12980912"
    data = {"user_id": user_id}

    response = requests.post(
        "https://api.gptbots.ai/v1/conversation", 
        headers = {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json",
        },
        data = json.dumps(data), 
    )

    # new_audio_b64 = base64.b64encode(file_bytes).decode('utf-8')

    # Get conversation id
    json_response = response.json()
    id = json_response.get("conversation_id")
    # Setup conversation 
    payload = {
        "conversation_id": id, 
        "response_mode": "blocking",
        "messages": [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": "Translate to Malay",
                    }, 
                    {
                        "type": "audio", 
                        "audio": {
                            "url": audio_path,
                            "name": "output", 
                            "format": "mp3"
                        }
                    }
                    # {
                    #     "type": "audio", 
                    #     "audio": {
                    #         "base64_content": audio_b64, 
                    #         "name": "output.mp3", 
                    #         "format": "mp3"
                    #     }
                    # }
                ], 
            }, 
        ],
    }
    response = requests.post(
        "https://api.gptbots.ai/v2/conversation/message", 
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {token}"
        }, 
        data = json.dumps(payload),
    )
    json_response = response.json()

    return JSONResponse(
        status_code = 200, 
        content = {
            "msg": json_response["output"][0]["content"]["text"]
        },
    )



if __name__ == "__main__":
    import uvicorn 
    port = 8000 
    uvicorn.run(app, host="0.0.0.0", port=port)


