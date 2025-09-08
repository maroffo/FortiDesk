from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional
from datetime import date

class GenitoreForm(FlaskForm):
    nome = StringField('Nome', 
                      validators=[DataRequired(), Length(min=2, max=100)])
    cognome = StringField('Cognome', 
                         validators=[DataRequired(), Length(min=2, max=100)])
    telefono = StringField('Numero di Telefono', 
                          validators=[DataRequired(), Length(min=10, max=20), 
                                    Regexp(r'^[\d\s\+\-\(\)]+$', message='Inserire un numero di telefono valido')])
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)])
    tipo_genitore = SelectField('Tipo', 
                               choices=[('padre', 'Padre'), ('madre', 'Madre'), ('tutore', 'Tutore/Tutrice')],
                               validators=[DataRequired()])

class BambinoForm(FlaskForm):
    # Dati anagrafici
    nome = StringField('Nome', 
                      validators=[DataRequired(), Length(min=2, max=100)])
    cognome = StringField('Cognome', 
                         validators=[DataRequired(), Length(min=2, max=100)])
    data_nascita = DateField('Data di Nascita', 
                            validators=[DataRequired()],
                            format='%Y-%m-%d')
    luogo_nascita = StringField('Luogo di Nascita', 
                               validators=[DataRequired(), Length(max=100)])
    codice_fiscale = StringField('Codice Fiscale', 
                                validators=[DataRequired(), Length(min=16, max=16),
                                          Regexp(r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$', 
                                                message='Inserire un codice fiscale valido')])
    
    # Indirizzo
    indirizzo_via = StringField('Via/Piazza', 
                               validators=[DataRequired(), Length(max=200)])
    indirizzo_civico = StringField('Numero Civico', 
                                  validators=[DataRequired(), Length(max=10)])
    indirizzo_cap = StringField('CAP', 
                               validators=[DataRequired(), Length(min=5, max=5),
                                         Regexp(r'^\d{5}$', message='Inserire un CAP valido')])
    indirizzo_comune = StringField('Comune', 
                                  validators=[DataRequired(), Length(max=100)])
    indirizzo_provincia = StringField('Provincia', 
                                     validators=[DataRequired(), Length(min=2, max=2),
                                               Regexp(r'^[A-Z]{2}$', message='Inserire una sigla provincia valida (es: BO)')])
    
    # Documento
    numero_documento = StringField('Numero Documento', 
                                  validators=[DataRequired(), Length(max=50)])
    ente_emettitore = StringField('Ente Emettitore', 
                                 validators=[DataRequired(), Length(max=100)])
    scadenza_documento = DateField('Scadenza Documento', 
                                  validators=[DataRequired()],
                                  format='%Y-%m-%d')
    
    # Certificato medico
    ha_certificato_medico = BooleanField('Ha Certificato Medico/Libretto Sportivo')
    tipo_certificato = SelectField('Tipo Certificato', 
                                  choices=[('', 'Seleziona...'), 
                                          ('medico', 'Certificato Medico'), 
                                          ('libretto_sportivo', 'Libretto dello Sportivo')],
                                  validators=[Optional()])
    scadenza_certificato = DateField('Scadenza Certificato', 
                                    validators=[Optional()],
                                    format='%Y-%m-%d')
    
    # Genitori - usando FieldList per gestire i due genitori
    genitore1_nome = StringField('Nome Genitore 1', 
                                validators=[DataRequired(), Length(min=2, max=100)])
    genitore1_cognome = StringField('Cognome Genitore 1', 
                                   validators=[DataRequired(), Length(min=2, max=100)])
    genitore1_telefono = StringField('Telefono Genitore 1', 
                                    validators=[DataRequired(), Length(min=10, max=20)])
    genitore1_email = StringField('Email Genitore 1', 
                                 validators=[DataRequired(), Email(), Length(max=120)])
    genitore1_tipo = SelectField('Tipo Genitore 1', 
                                choices=[('padre', 'Padre'), ('madre', 'Madre'), ('tutore', 'Tutore/Tutrice')],
                                validators=[DataRequired()])
    
    genitore2_nome = StringField('Nome Genitore 2', 
                                validators=[DataRequired(), Length(min=2, max=100)])
    genitore2_cognome = StringField('Cognome Genitore 2', 
                                   validators=[DataRequired(), Length(min=2, max=100)])
    genitore2_telefono = StringField('Telefono Genitore 2', 
                                    validators=[DataRequired(), Length(min=10, max=20)])
    genitore2_email = StringField('Email Genitore 2', 
                                 validators=[DataRequired(), Email(), Length(max=120)])
    genitore2_tipo = SelectField('Tipo Genitore 2', 
                                choices=[('padre', 'Padre'), ('madre', 'Madre'), ('tutore', 'Tutore/Tutrice')],
                                validators=[DataRequired()])
    
    submit = SubmitField('Salva Anagrafica')
    
    def validate_data_nascita(self, field):
        """Valida che la data di nascita sia realistica"""
        if field.data:
            today = date.today()
            if field.data > today:
                raise ValueError('La data di nascita non può essere futura')
            age = today.year - field.data.year
            if age > 18:
                raise ValueError('Il bambino deve avere meno di 18 anni')
            if age < 3:
                raise ValueError('Il bambino deve avere almeno 3 anni')
    
    def validate_scadenza_documento(self, field):
        """Valida che il documento non sia già scaduto"""
        if field.data and field.data < date.today():
            raise ValueError('Il documento risulta già scaduto')
    
    def validate_scadenza_certificato(self, field):
        """Valida la scadenza del certificato se presente"""
        if self.ha_certificato_medico.data:
            if not self.tipo_certificato.data:
                raise ValueError('Specificare il tipo di certificato')
            if not field.data:
                raise ValueError('Specificare la scadenza del certificato')
    
    def validate_genitore1_tipo(self, field):
        """Valida che i due genitori abbiano tipi diversi se sono padre/madre"""
        if field.data in ['padre', 'madre'] and self.genitore2_tipo.data == field.data:
            raise ValueError('Non è possibile avere due genitori dello stesso tipo')
    
    def validate_genitore2_tipo(self, field):
        """Valida che i due genitori abbiano tipi diversi se sono padre/madre"""
        if field.data in ['padre', 'madre'] and self.genitore1_tipo.data == field.data:
            raise ValueError('Non è possibile avere due genitori dello stesso tipo')