from .auth import auth_bp
from .students import students_bp
from .parents import parents_bp
from .classes import classes_bp
from .attendance import attendance_bp
from .payments import payments_bp
from .forms import forms_bp
from .videos import videos_bp
from .announcements import announcements_bp
from .settings import settings_bp
from .backup import backup_bp

__all__ = [
    'auth_bp',
    'students_bp',
    'parents_bp',
    'classes_bp',
    'attendance_bp',
    'payments_bp',
    'forms_bp',
    'videos_bp',
    'announcements_bp',
    'settings_bp',
    'backup_bp',
]
