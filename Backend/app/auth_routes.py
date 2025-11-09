"""
Rutas de Autenticación
Endpoints: login, logout, refresh token, cambio de contraseña, reset de contraseña
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import (
    LoginRequest, 
    LoginResponse, 
    MessageResponse, 
    UserResponse,
    UserChangePassword,
    PasswordResetRequest,
    PasswordResetValidate,
    PasswordResetConfirm
)
from app.dependencies import get_db, get_current_active_user, get_client_ip, get_user_agent
from app.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User, ActionType, PasswordResetToken
from app.schemas import LoginResponse, UserResponse
from app.email_service import EmailService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login de usuario"""
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        AuthService.create_audit_log(
            db=db,
            user_id=None,
            action_type=ActionType.LOGIN,
            description=f"Failed login attempt for username: {login_data.username}",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    AuthService.create_user_session(
        db=db,
        user_id=user.id,
        token=access_token,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    AuthService.update_last_login(db, user.id)
    
    AuthService.create_audit_log(
        db=db,
        user_id=user.id,
        action_type=ActionType.LOGIN,
        description=f"Successful login for user: {user.username}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout de usuario"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    AuthService.invalidate_session(db, token)
    
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.LOGOUT,
        description=f"User {current_user.username} logged out",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(
        message="Logout successful",
        detail=f"User {current_user.username} has been logged out"
    )

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Obtener información del usuario actual"""
    return UserResponse.from_orm(current_user)

@router.post("/change-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserChangePassword,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    if not AuthService.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if AuthService.verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    current_user.password_hash = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.UPDATE_USER,
        description="Password changed successfully",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(
        message="Password changed successfully",
        detail="Your password has been updated"
    )

@router.post("/validate-token", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def validate_token(
    current_user: User = Depends(get_current_active_user)
):
    """Validar si el token actual es válido"""
    return MessageResponse(
        message="Token is valid",
        detail=f"User {current_user.username} is authenticated"
    )

# ============ ENDPOINTS DE RESET DE CONTRASEÑA ============

@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Solicitar restablecimiento de contraseña"""
    try:
        print(f"📧 Password reset requested for: {reset_request.email}")
        
        user = AuthService.get_user_by_email(db, reset_request.email)
        
        if user and user.is_active:
            print(f"✅ User found: {user.username}")
            
            reset_token = AuthService.create_password_reset_token(db, user.id)
            print(f"🔑 Token created: {reset_token.token[:20]}...")
            
            email_sent = EmailService.send_password_reset_email(
                to_email=user.email,
                username=user.username,
                reset_token=reset_token.token
            )
            
            AuthService.create_audit_log(
                db=db,
                user_id=user.id,
                action_type=ActionType.PASSWORD_RESET_REQUEST,
                description=f"Password reset requested for user: {user.username}",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            if not email_sent:
                print(f"⚠️ Email service not configured")
                print(f"🔗 Reset URL: https://financial-analysis-system-two.vercel.app/reset-password?token={reset_token.token}")
        else:
            print(f"⚠️ User not found or inactive: {reset_request.email}")
        
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            detail="Please check your email for instructions to reset your password"
        )
        
    except Exception as e:
        print(f"❌ ERROR in forgot-password: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing password reset: {str(e)}"
        )

@router.post("/validate-reset-token", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def validate_reset_token(
    token_data: PasswordResetValidate,
    db: Session = Depends(get_db)
):
    """Validar si un token de reset es válido"""
    reset_token = AuthService.verify_reset_token(db, token_data.token)
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    
    return MessageResponse(
        message="Token is valid",
        detail=f"Token valid for user: {user.username}"
    )

@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Restablecer contraseña usando token válido"""
    success = AuthService.reset_password_with_token(
        db, 
        reset_data.token, 
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token
    ).first()
    
    if reset_token:
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        
        if user:
            AuthService.create_audit_log(
                db=db,
                user_id=user.id,
                action_type=ActionType.PASSWORD_RESET_COMPLETE,
                description=f"Password reset completed for user: {user.username}",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            EmailService.send_password_changed_notification(
                to_email=user.email,
                username=user.username
            )
    
    return MessageResponse(
        message="Password reset successful",
        detail="Your password has been updated. You can now login with your new password"
    )