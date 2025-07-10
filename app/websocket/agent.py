from fastapi import WebSocket, WebSocketDisconnect
from app.services.agents import get_llm_response

clients = []

async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  clients.append(websocket)
  try:
    while True:
      data = await websocket.receive_json()
      message = data.get("message")
      user = data.get("user")
      response, emotion = get_llm_response(message)
      await websocket.send_json({
        "emotion": emotion,
        "summary": response,
        "user": user
      })
  except WebSocketDisconnect:
    clients.remove(websocket)