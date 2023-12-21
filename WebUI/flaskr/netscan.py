from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import nmap3
import ipaddress
import json
from io import StringIO
import sys


# Defined Functions needed in the code!
# Fetches the scan information by their
# id and return the value of existed
# scan information as scan to the program

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


# The Blueprints are used in the place
# route and is placed in the code in
# order where we can access the function
# Which are needed!

# Declaration of the netscan Application
# Blueprint so we can acces this from
# our __init__.py

bp = Blueprint('netscan', __name__)


# Cotain function to fetch all the Desired Logs
# Information Associated with the Logged-In user
# in a Logged-In Session Dashboard which is the
# Index page.

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

    return render_template('netscan/index.html', scans=scans)


# Scanning Function which uses nmap3 library for
# Ip Scanning with vulners and mincvss+5.0 script
# in the arguments and it dumps all the results
# in json format with print standard output and get
# stored in the database

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
        ip, args="--script vulners --script-args mincvss+5.0 -p- ")
    results = json.dumps(data[ip]["ports"], indent=2)

    buffer = StringIO()
    sys.stdout = buffer

    print(results)
    final_data = buffer.getvalue()

    sys.stdout = sys.__stdout__
    db.execute("UPDATE scan SET scan_data = ? WHERE id = ?",
               (final_data, id,))
    db.commit()
    return redirect(url_for('netscan.index'))


# Create Function used to add the IP with their
# Description and Store their Information in the
# Database

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
            return redirect(url_for('netscan.index'))

    return render_template('netscan/index.html')


# Function to Update IP and their Description
# Information and Store the Modified Data in
# the Database

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
            return redirect(url_for('netscan.index'))

    return render_template('netscan/update.html', scan=scan)


# Function to Delete the Information of
# IP and their Description from the Database

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_scan(id)
    db = get_db()
    db.execute('DELETE FROM scan WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('netscan.index'))
