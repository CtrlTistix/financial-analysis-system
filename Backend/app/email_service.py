"""
Servicio de envío de emails
Maneja el envío de correos para reset de contraseña
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuración de email desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://financial-analysis-system-two.vercel.app")

class EmailService:
    """Servicio para enviar emails"""

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Enviar email usando SMTP
        """
        # Verificar si el servicio de email está configurado
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            print(f"⚠️ Email no configurado. Token para {to_email}:")
            print(f"🔗 Link de reset: {html_content}")
            return False

        try:
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = FROM_EMAIL
            message["To"] = to_email

            # Agregar contenido
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Conectar y enviar
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, to_email, message.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            print(f"✅ Email enviado a: {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            print(f"❌ Error enviando email: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        username: str,
        reset_token: str
    ) -> bool:
        """
        Enviar email de restablecimiento de contraseña
        """
        reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"

        subject = "Restablecimiento de Contraseña - Sistema de Análisis Financiero"

        # Contenido HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Restablecimiento de Contraseña</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en el Sistema de Análisis Financiero.</p>
                    
                    <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                    </div>
                    
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                        {reset_url}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Este enlace expira en <strong>1 hora</strong></li>
                            <li>Si no solicitaste este cambio, ignora este email</li>
                            <li>Tu contraseña actual no cambiará hasta que completes el proceso</li>
                        </ul>
                    </div>
                    
                    <p>Si tienes algún problema, contacta al administrador del sistema.</p>
                    
                    <p>Saludos,<br><strong>Equipo de Análisis Financiero</strong></p>
                </div>
                <div class="footer">
                    <p>Este es un mensaje automático, por favor no respondas a este email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Contenido texto plano
        text_content = f"""
        Hola {username},

        Recibimos una solicitud para restablecer la contraseña de tu cuenta.

        Usa el siguiente enlace para crear una nueva contraseña:
        {reset_url}

        Este enlace expira en 1 hora.

        Si no solicitaste este cambio, ignora este email.

        Saludos,
        Equipo de Análisis Financiero
        """

        return EmailService.send_email(to_email, subject, html_content, text_content)

    @staticmethod
    def send_password_changed_notification(to_email: str, username: str) -> bool:
        """
        Enviar notificación de que la contraseña fue cambiada exitosamente
        """
        subject = "Contraseña Actualizada - Sistema de Análisis Financiero"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .success {{
                    background-color: #d4edda;
                    border: 1px solid #28a745;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Contraseña Actualizada</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <div class="success">
                        <p><strong>Tu contraseña ha sido actualizada exitosamente.</strong></p>
                    </div>
                    
                    <p>Si no realizaste este cambio, contacta inmediatamente al administrador del sistema.</p>
                    
                    <p>Saludos,<br><strong>Equipo de Análisis Financiero</strong></p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Hola {username},

        Tu contraseña ha sido actualizada exitosamente.

        Si no realizaste este cambio, contacta inmediatamente al administrador.

        Saludos,
        Equipo de Análisis Financiero
        """

        return EmailService.send_email(to_email, subject, html_content, text_content)