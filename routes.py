from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from forms import RegistrationForm, LoginForm, FlaskForm, AlbumForm, PhotoUploadForm, ShareLinkForm
from models import User, Album, Photo
from flask_login import login_user, current_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Contul tau a fost creat! Te poti autentifica acum.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='inregistrare', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Te-ai autentificat cu succes!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Autentificare esuata. Verifica email-ul si parola.', 'danger')
    return render_template('login.html', title='Autentificare', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    albums = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='Dashboard', albums=albums)

@app.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
    form = AlbumForm()
    if form.validate_on_submit():
        album = Album(name=form.name.data, is_private=form.is_private.data, owner=current_user)
        db.session.add(album)
        db.session.commit()
        flash('Albumul a fost creat cu succes!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_album.html', title='Creeaza Album', form=form)

@app.route('/album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def view_album(album_id):
    album = Album.query.get_or_404(album_id)
    if album.owner != current_user:
        abort(403)
    photos = Photo.query.filter_by(album_id=album.id).all()
    share_link = request.args.get('share_link', None)
    form = PhotoUploadForm()
    if form.validate_on_submit():
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename == '':
                flash('Nu ai selectat niciun fisier.', 'danger')
                return redirect(request.url)
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                photo = Photo(image_file=filename, album=album)
                db.session.add(photo)
                db.session.commit()
                flash('Fotografia a fost incarcata!', 'success')
                return redirect(url_for('view_album', album_id=album.id))
            else:
                flash('Tip de fisier nepermis.', 'danger')
    return render_template('album.html', title=album.name, album=album, photos=photos, form=form, share_link=share_link)

@app.route('/share/<token>')
def shared_album(token):
    album = Album.verify_share_token(token)
    if album is None:
        flash('Link invalid sau expirat.', 'warning')
        return redirect(url_for('home'))
    photos = Photo.query.filter_by(album_id=album.id).all()
    return render_template('shared_album.html', album=album, photos=photos)

@app.route('/album/<int:album_id>/share', methods=['POST'])
@login_required
def generate_share_link(album_id):
    album = Album.query.get_or_404(album_id)
    if album.owner != current_user:
        abort(403)
    form = ShareLinkForm()
    if form.validate_on_submit():  # Verifică token-ul CSRF
        token = album.get_share_token()
        share_link = url_for('shared_album', token=token, _external=True)
        flash('Linkul de partajare a fost generat.', 'info')
        return redirect(url_for('view_album', album_id=album.id, share_link=share_link))
    return render_template('album.html', album=album, share_link=None, form=form)
