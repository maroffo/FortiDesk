# ABOUTME: Tests for the responsive navbar structure (hamburger, dropdowns, no duplicates)
# ABOUTME: Verifies Bootstrap 5 collapse, grouped navigation, and clean user menu

import pytest


class TestNavbarStructure:
    """Verify the navbar has proper Bootstrap 5 responsive markup."""

    def test_has_navbar_toggler(self, logged_in_admin):
        """Hamburger button must exist for mobile collapse."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert 'navbar-toggler' in html
        assert 'navbar-toggler-icon' in html
        assert 'data-bs-target="#mainNav"' in html

    def test_has_collapse_wrapper(self, logged_in_admin):
        """Nav items must be inside a collapse div."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert 'class="collapse navbar-collapse"' in html
        assert 'id="mainNav"' in html

    def test_grouped_dropdowns_present(self, logged_in_admin):
        """The 3 dropdown groups (People, Activities, Management) must exist."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert 'People' in html or 'Persone' in html
        assert 'Activities' in html or 'Attività' in html
        assert 'Management' in html or 'Gestione' in html

    def test_dropdown_people_contains_athletes_teams_staff(self, logged_in_admin):
        """People dropdown must contain Athletes, Teams, Staff links."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/athletes/' in html
        assert '/teams/' in html
        assert '/staff/' in html

    def test_dropdown_activities_contains_links(self, logged_in_admin):
        """Activities dropdown must contain Attendance, Training, Matches, Calendar."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/attendance/' in html
        assert '/training/' in html
        assert '/matches/' in html
        assert '/calendar/' in html

    def test_dropdown_management_contains_links(self, logged_in_admin):
        """Management dropdown must contain Equipment, Seasons, Documents, Communications."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/equipment/' in html
        assert '/seasons/' in html
        assert '/documents/' in html
        assert '/communications/' in html

    def test_standalone_links(self, logged_in_admin):
        """Dashboard and Reports must be standalone nav items (not in dropdowns)."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/dashboard' in html
        assert '/reports/' in html

    def test_user_dropdown_no_duplicates(self, logged_in_admin):
        """User dropdown must NOT contain navigation links (only language + logout)."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        # Extract the user dropdown (dropdown-menu-end) specifically
        user_menu_start = html.find('dropdown-menu-end')
        assert user_menu_start != -1, "User dropdown (dropdown-menu-end) not found"
        # Find the closing </ul> after that point
        user_menu_end = html.find('</ul>', user_menu_start)
        user_menu = html[user_menu_start:user_menu_end]
        # User menu should NOT contain nav section links
        assert '/athletes/' not in user_menu
        assert '/teams/' not in user_menu
        assert '/staff/' not in user_menu
        assert '/attendance/' not in user_menu
        assert '/training/' not in user_menu
        assert '/reports/' not in user_menu

    def test_user_dropdown_has_logout(self, logged_in_admin):
        """User dropdown must contain the logout link."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/auth/logout' in html

    def test_user_dropdown_has_language_links(self, logged_in_admin):
        """User dropdown must contain language switching links."""
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/set_language/en' in html
        assert '/set_language/it' in html


class TestNavbarAdminConditional:
    """Admin link should only appear for admin users."""

    def test_admin_link_visible_for_admin(self, logged_in_admin):
        resp = logged_in_admin.get('/dashboard')
        html = resp.data.decode()
        assert '/admin/users' in html

    def test_admin_link_hidden_for_coach(self, logged_in_coach):
        resp = logged_in_coach.get('/dashboard')
        html = resp.data.decode()
        assert '/admin/users' not in html
