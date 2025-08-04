from flask import flash, render_template


def get_form_errors(form):
    """
    Récupère les erreurs du formulaire et les affiche à l'utilisateur.
    """
    for _, errors in form.errors.items():
        for error in errors:
            flash(error, "danger")


def page_not_found(e):
    """
    Gère les erreurs 404.
    """
    ctx = {
        "title": "Page introuvable",
        e.description: "La page que vous recherchez n'existe pas.",
        "status": 404,
    }
    return render_template("errors/404.html", **ctx)


def internal_server_error(e):
    """
    Gère les erreurs 500.
    """
    ctx = {
        "title": "Erreur serveur",
        e.description: "Une erreur interne s'est produite sur le serveur.",
        "status": 500,
    }
    return render_template("errors/500.html", **ctx)