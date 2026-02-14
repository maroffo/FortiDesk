# ABOUTME: Smoke tests verifying all GET routes return 200/302 (no 500 errors)
# ABOUTME: Parametrized tests for unauthenticated and authenticated access

import pytest


# ---------------------------------------------------------------------------
# 1. Public routes (no login required) should return 200
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('url', [
    '/auth/login',
    '/auth/register',
])
def test_public_routes_return_200(client, url):
    response = client.get(url)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 2. Protected routes should redirect to login when unauthenticated
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('url', [
    '/dashboard',
    '/athletes/',
    '/athletes/new',
    '/staff/',
    '/staff/new',
    '/teams/',
    '/teams/new',
    '/attendance/',
    '/attendance/check-in',
    '/attendance/report',
    '/equipment/',
    '/equipment/new',
    '/equipment/assign',
    '/equipment/assignments',
    '/admin/users',
    '/admin/users/new',
    '/seasons/',
    '/seasons/new',
    '/training/',
    '/training/new',
    '/training/generate-recurring',
    '/matches/',
    '/matches/new',
    '/documents/',
    '/documents/upload',
    '/documents/expiring',
    '/communications/',
    '/communications/new',
    '/reports/',
    '/reports/team-roster',
    '/reports/attendance-summary',
    '/reports/equipment-inventory',
    '/reports/document-status',
    '/reports/insurance-status',
    '/calendar/',
])
def test_protected_routes_redirect_when_unauthenticated(client, url):
    response = client.get(url)
    assert response.status_code == 302
    assert '/auth/login' in response.headers.get('Location', '')


# ---------------------------------------------------------------------------
# 3. Authenticated admin access: list / index pages should return 200
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('url', [
    '/dashboard',
    '/athletes/',
    '/athletes/new',
    '/staff/',
    '/staff/new',
    '/teams/',
    '/teams/new',
    '/attendance/',
    '/attendance/check-in',
    '/attendance/report',
    '/equipment/',
    '/equipment/new',
    '/equipment/assign',
    '/equipment/assignments',
    '/admin/users',
    '/admin/users/new',
    '/seasons/',
    '/seasons/new',
    '/training/',
    '/training/new',
    '/training/generate-recurring',
    '/matches/',
    '/matches/new',
    '/documents/',
    '/documents/upload',
    '/documents/expiring',
    '/communications/',
    '/communications/new',
    '/reports/',
    '/reports/team-roster',
    '/reports/attendance-summary',
    '/reports/equipment-inventory',
    '/reports/document-status',
    '/reports/insurance-status',
    '/calendar/',
])
def test_authenticated_routes_return_200(logged_in_admin, url):
    response = logged_in_admin.get(url)
    assert response.status_code == 200, f'{url} returned {response.status_code}'


# ---------------------------------------------------------------------------
# 4. Detail / edit pages that require a persisted entity
# ---------------------------------------------------------------------------

def test_athlete_detail_page(logged_in_admin, sample_athlete):
    response = logged_in_admin.get(f'/athletes/{sample_athlete.id}')
    assert response.status_code == 200


def test_athlete_edit_page(logged_in_admin, sample_athlete):
    response = logged_in_admin.get(f'/athletes/{sample_athlete.id}/edit')
    assert response.status_code == 200


def test_staff_detail_page(logged_in_admin, sample_staff):
    response = logged_in_admin.get(f'/staff/{sample_staff.id}')
    assert response.status_code == 200


def test_staff_edit_page(logged_in_admin, sample_staff):
    response = logged_in_admin.get(f'/staff/{sample_staff.id}/edit')
    assert response.status_code == 200


def test_team_detail_page(logged_in_admin, sample_team):
    response = logged_in_admin.get(f'/teams/{sample_team.id}')
    assert response.status_code == 200


def test_team_edit_page(logged_in_admin, sample_team):
    response = logged_in_admin.get(f'/teams/{sample_team.id}/edit')
    assert response.status_code == 200


def test_team_assign_staff_page(logged_in_admin, sample_team):
    response = logged_in_admin.get(f'/teams/{sample_team.id}/assign-staff')
    assert response.status_code == 200


def test_season_detail_page(logged_in_admin, sample_season):
    response = logged_in_admin.get(f'/seasons/{sample_season.id}')
    assert response.status_code == 200


def test_season_edit_page(logged_in_admin, sample_season):
    response = logged_in_admin.get(f'/seasons/{sample_season.id}/edit')
    assert response.status_code == 200


def test_admin_user_detail_page(logged_in_admin, admin_user):
    response = logged_in_admin.get(f'/admin/users/{admin_user.id}')
    assert response.status_code == 200


def test_admin_user_edit_page(logged_in_admin, admin_user):
    response = logged_in_admin.get(f'/admin/users/{admin_user.id}/edit')
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 5. Auth logout
# ---------------------------------------------------------------------------

def test_logout_redirects(logged_in_admin):
    response = logged_in_admin.get('/auth/logout')
    assert response.status_code == 302


# ---------------------------------------------------------------------------
# 6. Language switcher
# ---------------------------------------------------------------------------

def test_set_language(client):
    response = client.get('/set_language/it')
    assert response.status_code == 302


# ---------------------------------------------------------------------------
# 7. Index redirect
# ---------------------------------------------------------------------------

def test_index_redirects(client):
    response = client.get('/')
    assert response.status_code == 302
