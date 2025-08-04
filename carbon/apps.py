from flask import Blueprint

carbon = Blueprint("carbon", __name__)

from .views import (
    IndexView,
    AddActivityView,
    HistoryView,
    DeleteActivityView
)

carbon.add_url_rule(
    "/",
    view_func=IndexView.as_view("index")
)
carbon.add_url_rule(
    "/add_activity/",
    view_func=AddActivityView.as_view("add_activity")
)
carbon.add_url_rule(
    "/history/",
    view_func=HistoryView.as_view("history")
)
carbon.add_url_rule(
    "/activity/delete/<int:activity_id>/",
    view_func=DeleteActivityView.as_view("delete_activity")
)