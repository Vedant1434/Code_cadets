from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.models import User, UserRole, DoctorStatus, DoctorProfile, PatientProfile
from app.security import create_access_token, pwd_context, audit_log
from app.templates import render_template

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def login_page(): return render_template("login", {})

@router.get("/register", response_class=HTMLResponse)
async def register_page(): return render_template("register", {})

@router.post("/auth/register")
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_db)
):
    if session.exec(select(User).where(User.email == email)).first():
        return HTMLResponse("Email exists", status_code=400)
    
    # 1. Create Base User
    user = User(
        email=email,
        hashed_password=pwd_context.hash(password),
        full_name=full_name,
        role=UserRole.PATIENT
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # 2. Create Patient Profile
    profile = PatientProfile(user_id=user.id)
    session.add(profile)
    session.commit()
    
    audit_log(session, user, "Registered", "Patient Profile", "Onboarding")
    return RedirectResponse("/", status_code=303)

@router.post("/auth/login")
async def login(response: RedirectResponse, username: str = Form(...), password: str = Form(...), session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.email == username)).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return HTMLResponse("Invalid credentials", status_code=400)
    
    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", token)
    return response

@router.get("/logout")
async def logout():
    resp = RedirectResponse("/")
    resp.delete_cookie("access_token")
    return resp

@router.post("/auth/seed")
async def seed_data(session: Session = Depends(get_db)):
    if session.exec(select(User)).first(): return RedirectResponse("/", status_code=303)
    pwd = pwd_context.hash("password")
    
    # Admin
    admin = User(email="admin@test.com", hashed_password=pwd, full_name="Admin", role=UserRole.ADMIN)
    session.add(admin)
    
    # Doctor
    doc_user = User(email="doc@test.com", hashed_password=pwd, full_name="Dr. Smith", role=UserRole.DOCTOR)
    session.add(doc_user)
    session.commit()
    session.refresh(doc_user)
    
    doc_profile = DoctorProfile(user_id=doc_user.id, specialty="Cardiology", status=DoctorStatus.ONLINE)
    session.add(doc_profile)
    
    session.commit()
    return RedirectResponse("/", status_code=303)