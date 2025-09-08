from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Bambino, Genitore
from app.forms.anagrafica_forms import BambinoForm

anagrafica_bp = Blueprint('anagrafica', __name__, url_prefix='/anagrafica')

@anagrafica_bp.route('/')
@login_required
def index():
    """Lista di tutti i bambini nell'anagrafica"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Bambino.query.filter_by(is_active=True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Bambino.nome.ilike(search_filter)) |
            (Bambino.cognome.ilike(search_filter)) |
            (Bambino.codice_fiscale.ilike(search_filter))
        )
    
    bambini = query.order_by(Bambino.cognome, Bambino.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('anagrafica/index.html', bambini=bambini, search=search)

@anagrafica_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo():
    """Inserimento nuovo bambino"""
    if not (current_user.is_admin() or current_user.is_allenatore()):
        flash('Non hai i permessi per inserire nuovi bambini', 'danger')
        return redirect(url_for('anagrafica.index'))
    
    form = BambinoForm()
    
    if form.validate_on_submit():
        try:
            # Verifica che il codice fiscale non esista già
            existing_bambino = Bambino.query.filter_by(
                codice_fiscale=form.codice_fiscale.data.upper()
            ).first()
            
            if existing_bambino:
                flash('Un bambino con questo codice fiscale è già presente', 'danger')
                return render_template('anagrafica/form.html', form=form, title='Nuovo Bambino')
            
            # Crea il nuovo bambino
            bambino = Bambino(
                nome=form.nome.data.strip().title(),
                cognome=form.cognome.data.strip().title(),
                data_nascita=form.data_nascita.data,
                luogo_nascita=form.luogo_nascita.data.strip().title(),
                codice_fiscale=form.codice_fiscale.data.upper(),
                indirizzo_via=form.indirizzo_via.data.strip(),
                indirizzo_civico=form.indirizzo_civico.data.strip(),
                indirizzo_cap=form.indirizzo_cap.data.strip(),
                indirizzo_comune=form.indirizzo_comune.data.strip().title(),
                indirizzo_provincia=form.indirizzo_provincia.data.upper(),
                numero_documento=form.numero_documento.data.strip(),
                ente_emettitore=form.ente_emettitore.data.strip(),
                scadenza_documento=form.scadenza_documento.data,
                ha_certificato_medico=form.ha_certificato_medico.data,
                tipo_certificato=form.tipo_certificato.data if form.ha_certificato_medico.data else None,
                scadenza_certificato=form.scadenza_certificato.data if form.ha_certificato_medico.data else None,
                inserito_da=current_user.id
            )
            
            db.session.add(bambino)
            db.session.flush()  # Per ottenere l'ID del bambino
            
            # Crea i due genitori
            genitore1 = Genitore(
                nome=form.genitore1_nome.data.strip().title(),
                cognome=form.genitore1_cognome.data.strip().title(),
                telefono=form.genitore1_telefono.data.strip(),
                email=form.genitore1_email.data.strip().lower(),
                tipo_genitore=form.genitore1_tipo.data,
                bambino_id=bambino.id
            )
            
            genitore2 = Genitore(
                nome=form.genitore2_nome.data.strip().title(),
                cognome=form.genitore2_cognome.data.strip().title(),
                telefono=form.genitore2_telefono.data.strip(),
                email=form.genitore2_email.data.strip().lower(),
                tipo_genitore=form.genitore2_tipo.data,
                bambino_id=bambino.id
            )
            
            db.session.add(genitore1)
            db.session.add(genitore2)
            
            db.session.commit()
            
            flash(f'Anagrafica di {bambino.get_nome_completo()} inserita correttamente!', 'success')
            return redirect(url_for('anagrafica.dettaglio', id=bambino.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Errore durante il salvataggio. Riprova.', 'danger')
            print(f"Errore: {e}")
    
    return render_template('anagrafica/form.html', form=form, title='Nuovo Bambino')

@anagrafica_bp.route('/<int:id>')
@login_required
def dettaglio(id):
    """Visualizza i dettagli di un bambino"""
    bambino = Bambino.query.get_or_404(id)
    if not bambino.is_active:
        abort(404)
    
    return render_template('anagrafica/dettaglio.html', bambino=bambino)

@anagrafica_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica(id):
    """Modifica anagrafica bambino"""
    if not (current_user.is_admin() or current_user.is_allenatore()):
        flash('Non hai i permessi per modificare le anagrafiche', 'danger')
        return redirect(url_for('anagrafica.dettaglio', id=id))
    
    bambino = Bambino.query.get_or_404(id)
    if not bambino.is_active:
        abort(404)
    
    form = BambinoForm(obj=bambino)
    
    # Popola i dati dei genitori nel form
    genitori = bambino.genitori
    if len(genitori) >= 1:
        form.genitore1_nome.data = genitori[0].nome
        form.genitore1_cognome.data = genitori[0].cognome
        form.genitore1_telefono.data = genitori[0].telefono
        form.genitore1_email.data = genitori[0].email
        form.genitore1_tipo.data = genitori[0].tipo_genitore
        
    if len(genitori) >= 2:
        form.genitore2_nome.data = genitori[1].nome
        form.genitore2_cognome.data = genitori[1].cognome
        form.genitore2_telefono.data = genitori[1].telefono
        form.genitore2_email.data = genitori[1].email
        form.genitore2_tipo.data = genitori[1].tipo_genitore
    
    if form.validate_on_submit():
        try:
            # Verifica che il codice fiscale non sia duplicato (escludendo il bambino corrente)
            existing_bambino = Bambino.query.filter(
                Bambino.codice_fiscale == form.codice_fiscale.data.upper(),
                Bambino.id != bambino.id
            ).first()
            
            if existing_bambino:
                flash('Un altro bambino con questo codice fiscale è già presente', 'danger')
                return render_template('anagrafica/form.html', form=form, title='Modifica Bambino', bambino=bambino)
            
            # Aggiorna i dati del bambino
            bambino.nome = form.nome.data.strip().title()
            bambino.cognome = form.cognome.data.strip().title()
            bambino.data_nascita = form.data_nascita.data
            bambino.luogo_nascita = form.luogo_nascita.data.strip().title()
            bambino.codice_fiscale = form.codice_fiscale.data.upper()
            bambino.indirizzo_via = form.indirizzo_via.data.strip()
            bambino.indirizzo_civico = form.indirizzo_civico.data.strip()
            bambino.indirizzo_cap = form.indirizzo_cap.data.strip()
            bambino.indirizzo_comune = form.indirizzo_comune.data.strip().title()
            bambino.indirizzo_provincia = form.indirizzo_provincia.data.upper()
            bambino.numero_documento = form.numero_documento.data.strip()
            bambino.ente_emettitore = form.ente_emettitore.data.strip()
            bambino.scadenza_documento = form.scadenza_documento.data
            bambino.ha_certificato_medico = form.ha_certificato_medico.data
            bambino.tipo_certificato = form.tipo_certificato.data if form.ha_certificato_medico.data else None
            bambino.scadenza_certificato = form.scadenza_certificato.data if form.ha_certificato_medico.data else None
            bambino.data_modifica = datetime.utcnow()
            
            # Aggiorna i genitori esistenti o ne crea di nuovi
            genitori = bambino.genitori
            
            # Aggiorna primo genitore
            if len(genitori) >= 1:
                genitori[0].nome = form.genitore1_nome.data.strip().title()
                genitori[0].cognome = form.genitore1_cognome.data.strip().title()
                genitori[0].telefono = form.genitore1_telefono.data.strip()
                genitori[0].email = form.genitore1_email.data.strip().lower()
                genitori[0].tipo_genitore = form.genitore1_tipo.data
                genitori[0].data_modifica = datetime.utcnow()
            else:
                nuovo_genitore1 = Genitore(
                    nome=form.genitore1_nome.data.strip().title(),
                    cognome=form.genitore1_cognome.data.strip().title(),
                    telefono=form.genitore1_telefono.data.strip(),
                    email=form.genitore1_email.data.strip().lower(),
                    tipo_genitore=form.genitore1_tipo.data,
                    bambino_id=bambino.id
                )
                db.session.add(nuovo_genitore1)
            
            # Aggiorna secondo genitore
            if len(genitori) >= 2:
                genitori[1].nome = form.genitore2_nome.data.strip().title()
                genitori[1].cognome = form.genitore2_cognome.data.strip().title()
                genitori[1].telefono = form.genitore2_telefono.data.strip()
                genitori[1].email = form.genitore2_email.data.strip().lower()
                genitori[1].tipo_genitore = form.genitore2_tipo.data
                genitori[1].data_modifica = datetime.utcnow()
            else:
                nuovo_genitore2 = Genitore(
                    nome=form.genitore2_nome.data.strip().title(),
                    cognome=form.genitore2_cognome.data.strip().title(),
                    telefono=form.genitore2_telefono.data.strip(),
                    email=form.genitore2_email.data.strip().lower(),
                    tipo_genitore=form.genitore2_tipo.data,
                    bambino_id=bambino.id
                )
                db.session.add(nuovo_genitore2)
            
            db.session.commit()
            
            flash(f'Anagrafica di {bambino.get_nome_completo()} aggiornata correttamente!', 'success')
            return redirect(url_for('anagrafica.dettaglio', id=bambino.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Errore durante il salvataggio. Riprova.', 'danger')
            print(f"Errore: {e}")
    
    return render_template('anagrafica/form.html', form=form, title='Modifica Bambino', bambino=bambino)

@anagrafica_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
def elimina(id):
    """Elimina (disattiva) un bambino"""
    if not current_user.is_admin():
        flash('Non hai i permessi per eliminare le anagrafiche', 'danger')
        return redirect(url_for('anagrafica.dettaglio', id=id))
    
    bambino = Bambino.query.get_or_404(id)
    
    try:
        bambino.is_active = False
        bambino.data_modifica = datetime.utcnow()
        
        # Disattiva anche i genitori
        for genitore in bambino.genitori:
            genitore.is_active = False
            genitore.data_modifica = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Anagrafica di {bambino.get_nome_completo()} eliminata correttamente', 'success')
        return redirect(url_for('anagrafica.index'))
        
    except Exception as e:
        db.session.rollback()
        flash('Errore durante l\'eliminazione. Riprova.', 'danger')
        print(f"Errore: {e}")
        return redirect(url_for('anagrafica.dettaglio', id=id))