from flask import Blueprint

auth = Blueprint("auth", __name__)

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    DashboardView,
)

auth.add_url_rule(
    "/register/",
    view_func=RegisterView.as_view("register"),
)
auth.add_url_rule(
    "/login/",
    view_func=LoginView.as_view("login"),
)
auth.add_url_rule(
    "/logout/",
    view_func=LogoutView.as_view("logout"),
)
auth.add_url_rule(
    "/dashboard/",
    view_func=DashboardView.as_view("dashboard"),
)