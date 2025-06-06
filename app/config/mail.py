from fastapi_mail import ConnectionConfig
from pathlib import Path
import os

conf = ConnectionConfig(
  MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
  MAIL_FROM=os.getenv("MAIL_FROM"),
  MAIL_PORT=587,
  MAIL_SERVER="smtp.gmail.com",
  MAIL_TLS=True,
  MAIL_SSL=False,
  USE_CREDENTIALS=False,  # 使用 OAuth2 就不需要密碼
  TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent.parent / "templates"
)