# ABOUTME: Unit tests for SQLAlchemy model methods (display, expiry, validation helpers)
# ABOUTME: Tests Athlete, Staff, Equipment, Insurance, Season, Match, Document, Attendance, Announcement models

from datetime import date, timedelta
from app.models import (
    Athlete, Staff, Equipment, Insurance, Season, Match,
    Document, Attendance, Announcement,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_athlete(db_session, admin_user, **overrides):
    """Create a minimal Athlete with sensible defaults."""
    defaults = dict(
        first_name='Test', last_name='Athlete',
        birth_date=date(2015, 1, 1), birth_place='Bologna',
        fiscal_code='TSTATH15A01A944X',
        street_address='Via Test', street_number='1',
        postal_code='40100', city='Bologna', province='BO',
        document_number='XX000', issuing_authority='Test',
        document_expiry=date(2030, 12, 31),
        created_by=admin_user.id,
    )
    defaults.update(overrides)
    a = Athlete(**defaults)
    db_session.add(a)
    db_session.commit()
    return a


def _make_staff(db_session, admin_user, **overrides):
    """Create a minimal Staff member with sensible defaults."""
    defaults = dict(
        first_name='Test', last_name='Staff',
        birth_date=date(1985, 6, 15), birth_place='Roma',
        fiscal_code='TSTSTF85H15H501Z',
        phone='+393330000000', email='teststaff@test.com',
        street_address='Via Staff', street_number='2',
        postal_code='00100', city='Roma', province='RM',
        document_number='YY111', issuing_authority='Test',
        document_expiry=date(2030, 12, 31),
        role='coach',
        created_by=admin_user.id,
    )
    defaults.update(overrides)
    s = Staff(**defaults)
    db_session.add(s)
    db_session.commit()
    return s


def _make_equipment(db_session, admin_user, **overrides):
    """Create a minimal Equipment item with sensible defaults."""
    defaults = dict(
        name='Test Ball',
        category='ball',
        condition='new',
        status='available',
        created_by=admin_user.id,
    )
    defaults.update(overrides)
    e = Equipment(**defaults)
    db_session.add(e)
    db_session.commit()
    return e


# ---------------------------------------------------------------------------
# TestAthleteModel
# ---------------------------------------------------------------------------

class TestAthleteModel:

    def test_get_full_name(self, sample_athlete):
        assert sample_athlete.get_full_name() == 'Marco Bianchi'

    def test_get_age(self, sample_athlete):
        today = date.today()
        birth = date(2015, 3, 20)
        expected_age = today.year - birth.year - (
            (today.month, today.day) < (birth.month, birth.day)
        )
        assert sample_athlete.get_age() == expected_age

    def test_get_full_address(self, sample_athlete):
        assert sample_athlete.get_full_address() == 'Via Garibaldi 5, 40100 Bologna (BO)'

    def test_is_certificate_expired_when_no_certificate(self, db_session, admin_user):
        athlete = _make_athlete(
            db_session, admin_user,
            has_medical_certificate=False,
            fiscal_code='NOCRT15A01A944A',
        )
        assert athlete.is_certificate_expired() is True

    def test_is_certificate_expired_when_future(self, db_session, admin_user):
        athlete = _make_athlete(
            db_session, admin_user,
            has_medical_certificate=True,
            certificate_expiry=date.today() + timedelta(days=30),
            fiscal_code='FUTCR15A01A944B',
        )
        assert athlete.is_certificate_expired() is False

    def test_is_certificate_expired_when_past(self, db_session, admin_user):
        athlete = _make_athlete(
            db_session, admin_user,
            has_medical_certificate=True,
            certificate_expiry=date.today() - timedelta(days=1),
            fiscal_code='PSTCR15A01A944C',
        )
        assert athlete.is_certificate_expired() is True

    def test_is_document_expired_future(self, sample_athlete):
        # document_expiry is 2030-06-30
        assert sample_athlete.is_document_expired() is False

    def test_days_until_certificate_expiry_none(self, db_session, admin_user):
        athlete = _make_athlete(
            db_session, admin_user,
            has_medical_certificate=False,
            certificate_expiry=None,
            fiscal_code='NONCE15A01A944D',
        )
        assert athlete.days_until_certificate_expiry() is None

    def test_days_until_document_expiry(self, sample_athlete):
        # document_expiry is 2030-06-30, should be a positive number
        days = sample_athlete.days_until_document_expiry()
        assert isinstance(days, int)
        assert days > 0


# ---------------------------------------------------------------------------
# TestStaffModel
# ---------------------------------------------------------------------------

class TestStaffModel:

    def test_get_role_display(self, app, sample_staff):
        with app.app_context():
            display = sample_staff.get_role_display()
            assert isinstance(display, str)
            assert len(display) > 0

    def test_requires_medical_certificate_coach(self, sample_staff):
        assert sample_staff.requires_medical_certificate() is True

    def test_requires_medical_certificate_manager(self, db_session, admin_user):
        staff = _make_staff(
            db_session, admin_user,
            role='manager',
            fiscal_code='MNGSTF85H15H501A',
            email='manager@test.com',
        )
        assert staff.requires_medical_certificate() is False

    def test_requires_background_check_coach(self, sample_staff):
        assert sample_staff.requires_background_check() is True

    def test_requires_background_check_secretary(self, db_session, admin_user):
        staff = _make_staff(
            db_session, admin_user,
            role='secretary',
            fiscal_code='SECSTF85H15H501B',
            email='secretary@test.com',
        )
        assert staff.requires_background_check() is False

    def test_is_document_expired_future(self, sample_staff):
        # document_expiry is 2030-12-31
        assert sample_staff.is_document_expired() is False

    def test_is_certificate_expired_no_cert(self, sample_staff):
        # has_medical_certificate defaults to False in the fixture
        assert sample_staff.is_certificate_expired() is True


# ---------------------------------------------------------------------------
# TestEquipmentModel
# ---------------------------------------------------------------------------

class TestEquipmentModel:

    def test_get_category_display(self, app, db_session, admin_user):
        eq = _make_equipment(db_session, admin_user, category='ball')
        with app.app_context():
            display = eq.get_category_display()
            assert isinstance(display, str)
            assert len(display) > 0

    def test_is_available_when_available(self, db_session, admin_user):
        eq = _make_equipment(db_session, admin_user, status='available')
        assert eq.is_available() is True

    def test_is_available_when_assigned(self, db_session, admin_user):
        eq = _make_equipment(
            db_session, admin_user,
            status='assigned',
            name='Assigned Ball',
        )
        assert eq.is_available() is False

    def test_needs_maintenance_future(self, db_session, admin_user):
        eq = _make_equipment(
            db_session, admin_user,
            next_maintenance_date=date.today() + timedelta(days=30),
            name='Future Maint Ball',
        )
        assert eq.needs_maintenance() is False

    def test_needs_maintenance_past(self, db_session, admin_user):
        eq = _make_equipment(
            db_session, admin_user,
            next_maintenance_date=date.today() - timedelta(days=1),
            name='Overdue Maint Ball',
        )
        assert eq.needs_maintenance() is True

    def test_needs_maintenance_none(self, db_session, admin_user):
        eq = _make_equipment(
            db_session, admin_user,
            next_maintenance_date=None,
            name='No Maint Ball',
        )
        assert eq.needs_maintenance() is False


# ---------------------------------------------------------------------------
# TestInsuranceModel
# ---------------------------------------------------------------------------

class TestInsuranceModel:

    def test_is_expired_future(self, db_session, admin_user, sample_athlete):
        ins = Insurance(
            policy_number='POL-001',
            provider='Assicurazioni Test',
            insurance_type='sports',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
        )
        db_session.add(ins)
        db_session.commit()
        assert ins.is_expired() is False

    def test_is_expired_past(self, db_session, admin_user, sample_athlete):
        ins = Insurance(
            policy_number='POL-002',
            provider='Assicurazioni Test',
            insurance_type='sports',
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=1),
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
        )
        db_session.add(ins)
        db_session.commit()
        assert ins.is_expired() is True

    def test_days_until_expiry(self, db_session, admin_user, sample_athlete):
        ins = Insurance(
            policy_number='POL-003',
            provider='Assicurazioni Test',
            insurance_type='accident',
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=30),
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
        )
        db_session.add(ins)
        db_session.commit()
        assert ins.days_until_expiry() == 30

    def test_get_insurance_type_display(self, app, db_session, admin_user, sample_athlete):
        ins = Insurance(
            policy_number='POL-004',
            provider='Assicurazioni Test',
            insurance_type='sports',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
        )
        db_session.add(ins)
        db_session.commit()
        with app.app_context():
            display = ins.get_insurance_type_display()
            assert isinstance(display, str)
            assert len(display) > 0


# ---------------------------------------------------------------------------
# TestSeasonModel
# ---------------------------------------------------------------------------

class TestSeasonModel:

    def test_is_ongoing_current(self, db_session, admin_user):
        # Create a season that definitely spans today
        season = Season(
            name='Current Test',
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=10),
            created_by=admin_user.id,
        )
        db_session.add(season)
        db_session.commit()
        assert season.is_ongoing() is True

    def test_days_remaining(self, db_session, admin_user):
        season = Season(
            name='Remaining Test',
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            created_by=admin_user.id,
        )
        db_session.add(season)
        db_session.commit()
        assert season.days_remaining() == 10


# ---------------------------------------------------------------------------
# TestMatchModel
# ---------------------------------------------------------------------------

class TestMatchModel:

    def _make_match(self, db_session, admin_user, sample_team, **overrides):
        defaults = dict(
            date=date.today(),
            opponent='Avversari RFC',
            match_type='league',
            team_id=sample_team.id,
            created_by=admin_user.id,
        )
        defaults.update(overrides)
        m = Match(**defaults)
        db_session.add(m)
        db_session.commit()
        return m

    def test_get_match_type_display(self, app, db_session, admin_user, sample_team):
        match = self._make_match(db_session, admin_user, sample_team, match_type='league')
        with app.app_context():
            display = match.get_match_type_display()
            assert isinstance(display, str)
            assert len(display) > 0

    def test_get_result_display_none(self, db_session, admin_user, sample_team):
        match = self._make_match(
            db_session, admin_user, sample_team,
            result=None,
            opponent='No Result FC',
        )
        assert match.get_result_display() == '-'

    def test_get_result_display_win(self, app, db_session, admin_user, sample_team):
        match = self._make_match(
            db_session, admin_user, sample_team,
            result='win',
            opponent='Losers RFC',
        )
        with app.app_context():
            display = match.get_result_display()
            assert isinstance(display, str)
            assert len(display) > 0
            assert display != '-'

    def test_get_score_display(self, db_session, admin_user, sample_team):
        match = self._make_match(
            db_session, admin_user, sample_team,
            score_home=3, score_away=1,
            opponent='Scored FC',
        )
        assert match.get_score_display() == '3 - 1'

    def test_get_score_display_no_score(self, db_session, admin_user, sample_team):
        match = self._make_match(
            db_session, admin_user, sample_team,
            opponent='TBD FC',
        )
        assert match.get_score_display() == '-'


# ---------------------------------------------------------------------------
# TestDocumentModel
# ---------------------------------------------------------------------------

class TestDocumentModel:

    def _make_document(self, db_session, admin_user, **overrides):
        defaults = dict(
            title='Test Doc',
            document_type='medical_certificate',
            file_path='/uploads/test.pdf',
            file_name='test.pdf',
            entity_type='athlete',
            entity_id=1,
            created_by=admin_user.id,
        )
        defaults.update(overrides)
        d = Document(**defaults)
        db_session.add(d)
        db_session.commit()
        return d

    def test_get_document_type_display(self, app, db_session, admin_user):
        doc = self._make_document(
            db_session, admin_user,
            document_type='medical_certificate',
        )
        with app.app_context():
            display = doc.get_document_type_display()
            assert isinstance(display, str)
            assert len(display) > 0

    def test_is_expired_future(self, db_session, admin_user):
        doc = self._make_document(
            db_session, admin_user,
            expiry_date=date.today() + timedelta(days=30),
            title='Future Doc',
        )
        assert doc.is_expired() is False

    def test_is_expired_no_date(self, db_session, admin_user):
        doc = self._make_document(
            db_session, admin_user,
            expiry_date=None,
            title='No Expiry Doc',
        )
        assert doc.is_expired() is False

    def test_days_until_expiry(self, db_session, admin_user):
        doc = self._make_document(
            db_session, admin_user,
            expiry_date=date.today() + timedelta(days=15),
            title='15 Days Doc',
        )
        assert doc.days_until_expiry() == 15


# ---------------------------------------------------------------------------
# TestAttendanceModel
# ---------------------------------------------------------------------------

class TestAttendanceModel:

    def test_get_status_display(self, app, db_session, admin_user, sample_athlete):
        att = Attendance(
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
            date=date.today(),
            session_type='training',
            status='present',
        )
        db_session.add(att)
        db_session.commit()
        with app.app_context():
            display = att.get_status_display()
            assert isinstance(display, str)
            assert len(display) > 0

    def test_get_session_type_display(self, app, db_session, admin_user, sample_athlete):
        att = Attendance(
            athlete_id=sample_athlete.id,
            created_by=admin_user.id,
            date=date.today(),
            session_type='training',
            status='present',
        )
        db_session.add(att)
        db_session.commit()
        with app.app_context():
            display = att.get_session_type_display()
            assert isinstance(display, str)
            assert len(display) > 0


# ---------------------------------------------------------------------------
# TestAnnouncementModel
# ---------------------------------------------------------------------------

class TestAnnouncementModel:

    def test_get_announcement_type_display(self, app, db_session, admin_user):
        ann = Announcement(
            subject='Test Announcement',
            body='This is a test announcement body.',
            announcement_type='general',
            created_by=admin_user.id,
        )
        db_session.add(ann)
        db_session.commit()
        with app.app_context():
            display = ann.get_announcement_type_display()
            assert isinstance(display, str)
            assert len(display) > 0
