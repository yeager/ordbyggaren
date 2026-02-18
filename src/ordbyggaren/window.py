"""Main window for Ordbyggaren - Phonological training."""
import random
import subprocess
import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

_ = gettext.gettext

# Word lists by difficulty
WORDS = {
    _("Easy"): [
        ("sol", "☀️"), ("bil", "🚗"), ("hus", "🏠"), ("bok", "📖"),
        ("mat", "🍽️"), ("ko", "🐄"), ("is", "🍦"), ("uv", "🦉"),
    ],
    _("Medium"): [
        ("katt", "🐱"), ("hund", "🐕"), ("fisk", "🐟"), ("skog", "🌲"),
        ("boll", "⚽"), ("lamm", "🐑"), ("ring", "💍"), ("sand", "🏖️"),
    ],
    _("Hard"): [
        ("skola", "🏫"), ("blomma", "🌸"), ("vatten", "💧"), ("stjärna", "⭐"),
        ("groda", "🐸"), ("morot", "🥕"), ("cykel", "🚲"), ("papper", "📄"),
    ],
}


class OrdbyggarenWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, default_width=500, default_height=650,
                         title=_("Ordbyggaren"))
        self.difficulty = list(WORDS.keys())[0]
        self.current_word = ""
        self.current_emoji = ""
        self.score = 0
        self.attempts = 0
        self._build_ui()
        self._new_word()
        self._start_clock()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        theme_btn = Gtk.Button(icon_name="weather-clear-night-symbolic",
                               tooltip_text=_("Toggle dark/light theme"))
        theme_btn.connect("clicked", self._toggle_theme)
        header.pack_end(theme_btn)

        menu = Gio.Menu()
        menu.append(_("Keyboard Shortcuts"), "app.shortcuts")
        menu.append(_("About Ordbyggaren"), "app.about")
        menu.append(_("Quit"), "app.quit")
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        header.pack_end(menu_btn)

        # Score
        self.score_label = Gtk.Label(label="⭐ 0")
        self.score_label.add_css_class("title-2")
        header.pack_start(self.score_label)

        # Difficulty selector
        diff_box = Gtk.Box(spacing=0, halign=Gtk.Align.CENTER)
        diff_box.add_css_class("linked")
        diff_box.set_margin_top(8)
        first = None
        for d in WORDS:
            btn = Gtk.ToggleButton(label=d)
            if first is None:
                first = btn
                btn.set_active(True)
            else:
                btn.set_group(first)
            btn.connect("toggled", self._on_diff_changed, d)
            diff_box.append(btn)
        main_box.append(diff_box)

        # Word display area
        self.emoji_label = Gtk.Label()
        self.emoji_label.add_css_class("title-1")
        self.emoji_label.set_margin_top(24)
        main_box.append(self.emoji_label)

        # Hint: shows blanks
        self.hint_label = Gtk.Label()
        self.hint_label.add_css_class("title-2")
        self.hint_label.set_margin_top(12)
        main_box.append(self.hint_label)

        # Letter slots (where answer goes)
        self.answer_box = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
        self.answer_box.set_margin_top(16)
        main_box.append(self.answer_box)

        # Scrambled letter buttons
        self.letters_box = Gtk.FlowBox()
        self.letters_box.set_max_children_per_line(8)
        self.letters_box.set_min_children_per_line(4)
        self.letters_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.letters_box.set_homogeneous(True)
        self.letters_box.set_margin_start(24)
        self.letters_box.set_margin_end(24)
        self.letters_box.set_margin_top(16)
        main_box.append(self.letters_box)

        # Speak button
        speak_btn = Gtk.Button(label="🔊 " + _("Listen"))
        speak_btn.add_css_class("pill")
        speak_btn.set_margin_top(12)
        speak_btn.set_halign(Gtk.Align.CENTER)
        speak_btn.connect("clicked", self._on_speak)
        main_box.append(speak_btn)

        # Feedback
        self.feedback_label = Gtk.Label(label="")
        self.feedback_label.add_css_class("title-2")
        self.feedback_label.set_margin_top(12)
        main_box.append(self.feedback_label)

        # Controls
        ctrl_box = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER)
        ctrl_box.set_margin_top(12)
        ctrl_box.set_margin_bottom(8)

        clear_btn = Gtk.Button(label=_("Clear"))
        clear_btn.add_css_class("pill")
        clear_btn.connect("clicked", self._on_clear)
        ctrl_box.append(clear_btn)

        skip_btn = Gtk.Button(label=_("Skip"))
        skip_btn.add_css_class("pill")
        skip_btn.connect("clicked", lambda *_: self._new_word())
        ctrl_box.append(skip_btn)

        main_box.append(ctrl_box)

        # Spacer
        spacer = Gtk.Box(vexpand=True)
        main_box.append(spacer)

        # Status
        self.status_label = Gtk.Label(label="", xalign=0)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_bottom(4)
        main_box.append(self.status_label)

        self.typed_letters = []

    def _new_word(self):
        words = WORDS.get(self.difficulty, [])
        if not words:
            return
        word, emoji = random.choice(words)
        self.current_word = word
        self.current_emoji = emoji
        self.typed_letters = []
        self.feedback_label.set_label("")

        self.emoji_label.set_label(emoji)
        self.hint_label.set_label("_ " * len(word))
        self._update_answer()
        self._populate_letters()

    def _populate_letters(self):
        child = self.letters_box.get_first_child()
        while child:
            nc = child.get_next_sibling()
            self.letters_box.remove(child)
            child = nc

        letters = list(self.current_word.upper())
        # Add some random distractors
        extras = random.sample("ABCDEFGHIJKLMNOPRSTUVÅÄÖ", min(3, 24))
        letters.extend(extras[:3])
        random.shuffle(letters)

        for ch in letters:
            btn = Gtk.Button(label=ch)
            btn.add_css_class("title-3")
            btn.set_size_request(50, 50)
            btn.connect("clicked", self._on_letter_clicked, ch)
            self.letters_box.insert(btn, -1)

    def _on_letter_clicked(self, btn, letter):
        if len(self.typed_letters) < len(self.current_word):
            self.typed_letters.append(letter)
            btn.set_sensitive(False)
            self._update_answer()
            self._check_word()

    def _update_answer(self):
        child = self.answer_box.get_first_child()
        while child:
            nc = child.get_next_sibling()
            self.answer_box.remove(child)
            child = nc

        for i in range(len(self.current_word)):
            lbl = Gtk.Label()
            lbl.add_css_class("title-2")
            lbl.set_size_request(40, 40)
            if i < len(self.typed_letters):
                lbl.set_label(self.typed_letters[i])
            else:
                lbl.set_label("_")
            self.answer_box.append(lbl)

    def _check_word(self):
        if len(self.typed_letters) == len(self.current_word):
            attempt = "".join(self.typed_letters).lower()
            self.attempts += 1
            if attempt == self.current_word:
                self.score += 1
                self.score_label.set_label(f"⭐ {self.score}")
                self.feedback_label.set_label("🎉 " + _("Correct!") + " 🎉")
                GLib.timeout_add(1500, self._new_word)
            else:
                self.feedback_label.set_label("❌ " + _("Try again!"))
                GLib.timeout_add(1000, self._on_clear)

    def _on_clear(self, *_):
        self.typed_letters = []
        self.feedback_label.set_label("")
        self._update_answer()
        self._populate_letters()
        return False

    def _on_speak(self, btn):
        try:
            subprocess.Popen(["espeak-ng", "-v", "sv", self.current_word],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            pass

    def _on_diff_changed(self, btn, diff):
        if btn.get_active():
            self.difficulty = diff
            self._new_word()

    def _toggle_theme(self, btn):
        mgr = Adw.StyleManager.get_default()
        if mgr.get_dark():
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def _start_clock(self):
        GLib.timeout_add_seconds(1, self._update_clock)
        self._update_clock()

    def _update_clock(self):
        now = GLib.DateTime.new_now_local()
        self.status_label.set_label(now.format("%Y-%m-%d %H:%M:%S"))
        return True
