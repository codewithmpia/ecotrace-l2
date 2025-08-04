from auth.models import User
from carbon.models import Activity

def inject_total_users():
    return {"total_users": User.get_total_users()}


def inject_total_activities():
    return {"total_activities": Activity.get_total_activities()}

def inject_get_total_emissions():
    return {"total_emissions": User.get_all_users_total_emissions()}