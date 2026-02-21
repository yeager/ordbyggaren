"""Ordbyggaren - Phonological training app."""
import sys
import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from ordbyggaren import __version__
from ordbyggaren.window import OrdbyggarenWindow
from ordbyggaren.accessibility import apply_large_text

TEXTDOMAIN = "ordbyggaren"
gettext.textdomain(TEXTDOMAIN)
_ = gettext.gettext


class OrdbyggarenApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="se.yeager.ordbyggaren",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        apply_large_text()
        win = self.props.active_window or OrdbyggarenWindow(application=self)
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._setup_actions()

    def _setup_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self._on_shortcuts)
        self.add_action(shortcuts_action)
        self.set_accels_for_action("app.shortcuts", ["<Control>slash"])

    def _on_about(self, *_):
        about = Adw.AboutDialog(
            application_name=_("Word Builder"),
            application_icon="ordbyggaren",
            version=__version__,
            developer_name="Daniel Nylander",
            website="https://github.com/yeager/ordbyggaren",
            issue_url="https://github.com/yeager/ordbyggaren/issues",
            translate_url="https://app.transifex.com/danielnylander/ordbyggaren",
            license_type=Gtk.License.GPL_3_0,
            developers=["Daniel Nylander"],
            copyright="© 2026 Daniel Nylander",
        )
        about.present(self.props.active_window)

    def _on_shortcuts(self, *_):
        builder = Gtk.Builder()
        builder.add_from_string('''
        <interface>
          <object class="GtkShortcutsWindow" id="shortcuts">
            <property name="modal">true</property>
            <child><object class="GtkShortcutsSection"><child><object class="GtkShortcutsGroup">
              <property name="title" translatable="yes">General</property>
              <child><object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Quit</property>
                <property name="accelerator">&lt;Control&gt;q</property>
              </object></child>
              <child><object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Keyboard Shortcuts</property>
                <property name="accelerator">&lt;Control&gt;slash</property>
              </object></child>
            </object></child></object></child>
          </object>
        </interface>''')
        win = builder.get_object("shortcuts")
        win.set_transient_for(self.props.active_window)
        win.present()


def main():
    app = OrdbyggarenApp()
    app.run(sys.argv)
