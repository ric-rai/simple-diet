from flask_login import current_user

from application import app, db
from flask import render_template, request, Response, abort


def render_table(**kwargs):
    return render_template("components/table.html", **kwargs)


def delete_row(db_model, form_class):
    form = form_class(request.form)
    if not form.validate_id_fields():
        abort(400)
    row = db_model.cache.pop(form.id.data)
    if hasattr(row, "before_delete"):
        row.before_delete()
    db.session().delete(row)
    db.session().commit()
    return Response("", status=200, mimetype='text/plain')


def edit_row(db_model, form_class, **kwargs):
    if request.method == "GET":
        form = form_class(request.args)
        if not form.validate_id_fields():
            abort(400)
        row = db_model.from_cache(form.id.data)
        return render_template("components/input-row.html", form=form_class(obj=row))
    form = form_class(request.form)
    if not form.validate():
        return render_template("components/input-row.html", form=form), 422
    app.logger.info("fetching row for saving")
    row = db_model.from_cache(form.id.data)
    form.populate_obj(row)
    db.session().add(row)
    db.session().commit()
    app.logger.info("committed")
    return render_template("components/row.html", row=row, form=form_class(), **kwargs)


def new_row(db_model, form_class, **kwargs):
    if request.method == "GET":
        form = form_class(request.args)
        if not form.validate_id_fields():
            abort(400)
        return render_template("components/input-row.html", form=form)
    form = form_class(request.form)
    del form.id
    if not form.validate():
        return render_template("components/input-row.html", form=form), 422
    row = db_model()
    form.populate_obj(row)
    if hasattr(db_model, 'account_id'):
            row.account_id = current_user.id
    db_model.to_cache(row)
    db.session().add(row)
    db.session().commit()
    app.logger.info("committed")
    return render_template("components/row.html", row=row, form=form_class(), **kwargs)

