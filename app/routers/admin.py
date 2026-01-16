from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from app.database import get_db
from app.models import User, UserRole, DoctorStatus
from app.security import get_current_user, pwd_context, audit_log, oauth2_scheme

router = APIRouter()

@router.post("/admin/add_doctor")
async def add_doctor(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    specialty: str = Form(...),
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
):
    admin = await get_current_user(token, session)
    if admin.role != UserRole.ADMIN: return HTMLResponse("Unauthorized", status_code=403)
    
    new_doc = User(
        email=email,
        hashed_password=pwd_context.hash(password),
        full_name=full_name,
        role=UserRole.DOCTOR,
        specialty=specialty,
        status=DoctorStatus.OFFLINE
    )
    session.add(new_doc)
    session.commit()
    audit_log(session, admin, "Onboarded New Doctor", f"Staff: {full_name}", "Staff Management")
    return RedirectResponse("/dashboard", status_code=303)