from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import nmap3
import ipaddress
import json

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    user_id = session.get('user_id')
    scans = db.execute(
        'SELECT s.id, ip_address, description, created, scan_data, scan_id, username'
        ' FROM scan s JOIN user u ON s.scan_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC',
        (user_id,)
    ).fetchall()

    return render_template('blog/index.html', scans=scans)


@bp.route('/<int:id>/index', methods=('POST',))
@login_required
def scanning(id):
    db = get_db()
    ip_addr = db.execute(
        'SELECT ip_address FROM scan WHERE id = ?', (id,)).fetchone()
    ip = ip_addr['ip_address']

    ipaddress.ip_address(ip)
    nmap = nmap3.Nmap()
    data = nmap.nmap_version_detection(
        ip, args="--script vulners --script-args mincvss+5.0")
    results = json.dumps(data[ip]["ports"])

    db.execute("UPDATE scan SET scan_data = ? WHERE id = ?",
               (results, id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        ip_addr = request.form['ip_addr']
        description = request.form['description']
        error = None

        if not ip_addr:
            error = 'IP Address is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO scan (ip_address, description, scan_id)'
                ' VALUES (?, ?, ?)',
                (ip_addr, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/index.html')


def get_scan(id, check_scan=True):
    scan = get_db().execute(
        'SELECT s.id, ip_address, description, created, scan_id, username'
        ' FROM scan s JOIN user u ON s.scan_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if scan is None:
        abort(404, f"Scan id {id} doesn't exist.")

    if check_scan and scan['scan_id'] != g.user['id']:
        abort(403)

    return scan


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    scan = get_scan(id)

    if request.method == 'POST':
        ip_addr = request.form['ip_addr']
        description = request.form['description']
        error = None

        if not ip_addr:
            error = 'IP Address is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE scan SET ip_address = ?, description = ?'
                ' WHERE id = ?',
                (ip_addr, description, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', scan=scan)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_scan(id)
    db = get_db()
    db.execute('DELETE FROM scan WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
