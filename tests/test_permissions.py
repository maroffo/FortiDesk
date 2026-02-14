# ABOUTME: RBAC permission tests verifying admin-only routes and coach restrictions
# ABOUTME: Tests unauthenticated redirects, coach read-only on delete, admin-only sections

import pytest


class TestUnauthenticatedAccess:
    """Unauthenticated users must be redirected to login for all protected routes."""

    @pytest.mark.parametrize('url', [
        '/dashboard',
        '/athletes/',
        '/staff/',
        '/teams/',
        '/attendance/',
        '/equipment/',
        '/admin/users',
        '/seasons/',
        '/training/',
        '/matches/',
        '/documents/',
        '/communications/',
        '/reports/',
        '/calendar/',
    ])
    def test_redirect_to_login(self, client, url):
        response = client.get(url)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestCoachPermissions:
    """Coach users can access list/create pages but cannot perform delete operations."""

    def test_coach_can_view_athletes(self, logged_in_coach):
        response = logged_in_coach.get('/athletes/')
        assert response.status_code == 200

    def test_coach_can_view_staff(self, logged_in_coach):
        response = logged_in_coach.get('/staff/')
        assert response.status_code == 200

    def test_coach_can_create_athlete_page(self, logged_in_coach):
        response = logged_in_coach.get('/athletes/new')
        assert response.status_code == 200

    def test_coach_can_create_staff_page(self, logged_in_coach):
        response = logged_in_coach.get('/staff/new')
        assert response.status_code == 200

    def test_coach_cannot_delete_athlete(self, logged_in_coach, sample_athlete):
        response = logged_in_coach.post(f'/athletes/{sample_athlete.id}/delete')
        # Should redirect (302) with permission denied flash, or return 403
        assert response.status_code in (302, 403)
        # Verify athlete still active
        from app.models import Athlete
        athlete = Athlete.query.get(sample_athlete.id)
        assert athlete.is_active is True

    def test_coach_cannot_delete_staff(self, logged_in_coach, sample_staff):
        response = logged_in_coach.post(f'/staff/{sample_staff.id}/delete')
        assert response.status_code in (302, 403)
        from app.models import Staff
        staff = Staff.query.get(sample_staff.id)
        assert staff.is_active is True

    def test_coach_cannot_delete_team(self, logged_in_coach, sample_team):
        response = logged_in_coach.post(f'/teams/{sample_team.id}/delete')
        assert response.status_code in (302, 403)
        from app.models import Team
        team = Team.query.get(sample_team.id)
        assert team.is_active is True


class TestAdminOnlyRoutes:
    """Admin-only routes (e.g. user management) are blocked for coach users."""

    def test_admin_can_access_user_list(self, logged_in_admin):
        response = logged_in_admin.get('/admin/users')
        assert response.status_code == 200

    def test_admin_can_access_user_create(self, logged_in_admin):
        response = logged_in_admin.get('/admin/users/new')
        assert response.status_code == 200

    def test_coach_cannot_access_user_list(self, logged_in_coach):
        response = logged_in_coach.get('/admin/users')
        # Should redirect with permission denied or return 403
        assert response.status_code in (302, 403)

    def test_coach_cannot_access_user_create(self, logged_in_coach):
        response = logged_in_coach.get('/admin/users/new')
        assert response.status_code in (302, 403)


class TestAdminCanDelete:
    """Admin users can perform soft-delete operations."""

    def test_admin_can_delete_athlete(self, logged_in_admin, sample_athlete):
        response = logged_in_admin.post(f'/athletes/{sample_athlete.id}/delete')
        assert response.status_code == 302  # redirect after successful delete
        from app.models import Athlete
        athlete = Athlete.query.get(sample_athlete.id)
        assert athlete.is_active is False

    def test_admin_can_delete_staff(self, logged_in_admin, sample_staff):
        response = logged_in_admin.post(f'/staff/{sample_staff.id}/delete')
        assert response.status_code == 302
        from app.models import Staff
        staff = Staff.query.get(sample_staff.id)
        assert staff.is_active is False

    def test_admin_can_delete_team(self, logged_in_admin, sample_team):
        response = logged_in_admin.post(f'/teams/{sample_team.id}/delete')
        assert response.status_code == 302
        from app.models import Team
        team = Team.query.get(sample_team.id)
        assert team.is_active is False
