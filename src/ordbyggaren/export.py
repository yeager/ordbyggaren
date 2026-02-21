"""Export functionality for Ordbyggaren training results."""

import csv
import io
import json
from datetime import datetime

import gettext
_ = gettext.gettext

from ordbyggaren import __version__

APP_LABEL = _("Word Builder")
AUTHOR = "Daniel Nylander"
WEBSITE = "www.autismappar.se"

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib


def results_to_csv(results, score):
    """Export training results as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([_("Word"), _("Difficulty"), _("Correct"), _("Attempts"), _("Date")])
    for r in results:
        writer.writerow([
            r.get("word", ""),
            r.get("difficulty", ""),
            _("Yes") if r.get("correct") else _("No"),
            r.get("attempts", 1),
            r.get("date", ""),
        ])
    writer.writerow([])
    writer.writerow([_("Total score: %d") % score])
    writer.writerow([f"{APP_LABEL} v{__version__} — {WEBSITE}"])
    return output.getvalue()


def results_to_json(results, score):
    """Export training results as JSON."""
    data = {
        "results": results,
        "score": score,
        "_exported_by": f"{APP_LABEL} v{__version__}",
        "_author": AUTHOR,
        "_website": WEBSITE,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_results_pdf(results, score, output_path):
    """Export training results as PDF."""
    try:
        import cairo
    except ImportError:
        try:
            import cairocffi as cairo
        except ImportError:
            return False

    width, height = 595, 842
    surface = cairo.PDFSurface(output_path, width, height)
    ctx = cairo.Context(surface)

    ctx.set_font_size(24)
    ctx.move_to(40, 50)
    ctx.show_text(_("Training Results"))

    ctx.set_font_size(16)
    ctx.move_to(40, 80)
    ctx.show_text(_("Score: %d ⭐") % score)

    ctx.set_font_size(12)
    ctx.move_to(40, 100)
    ctx.show_text(datetime.now().strftime("%Y-%m-%d"))

    # Table header
    y = 130
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.3, 0.3, 0.3)
    ctx.move_to(40, y)
    ctx.show_text(_("Word"))
    ctx.move_to(200, y)
    ctx.show_text(_("Difficulty"))
    ctx.move_to(340, y)
    ctx.show_text(_("Correct"))
    ctx.move_to(440, y)
    ctx.show_text(_("Attempts"))

    y += 10
    ctx.set_line_width(0.5)
    ctx.move_to(40, y)
    ctx.line_to(width - 40, y)
    ctx.stroke()

    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(12)

    for r in results:
        y += 24
        if y > height - 40:
            surface.show_page()
            y = 40
        ctx.move_to(40, y)
        ctx.show_text(r.get("word", ""))
        ctx.move_to(200, y)
        ctx.show_text(r.get("difficulty", ""))
        ctx.move_to(340, y)
        if r.get("correct"):
            ctx.set_source_rgb(0.18, 0.76, 0.49)
            ctx.show_text("✓")
        else:
            ctx.set_source_rgb(0.88, 0.11, 0.14)
            ctx.show_text("✗")
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(440, y)
        ctx.show_text(str(r.get("attempts", 1)))

    # Footer
    ctx.set_font_size(9)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    footer = f"{APP_LABEL} v{__version__} — {WEBSITE} — {datetime.now().strftime('%Y-%m-%d')}"
    ctx.move_to(40, height - 20)
    ctx.show_text(footer)

    surface.finish()
    return True


def show_export_dialog(window, results, score, status_callback=None):
    """Show export dialog."""
    dialog = Adw.AlertDialog.new(
        _("Export Training Results"),
        _("Choose export format:")
    )

    dialog.add_response("cancel", _("Cancel"))
    dialog.add_response("csv", _("CSV"))
    dialog.add_response("json", _("JSON"))
    dialog.add_response("pdf", _("PDF"))
    dialog.set_default_response("csv")
    dialog.set_close_response("cancel")

    dialog.connect("response", _on_export_response, window, results, score, status_callback)
    dialog.present(window)


def _on_export_response(dialog, response, window, results, score, status_callback):
    if response == "cancel":
        return
    if response == "csv":
        _save_text(window, results, score, "csv", results_to_csv, status_callback)
    elif response == "json":
        _save_text(window, results, score, "json", results_to_json, status_callback)
    elif response == "pdf":
        _save_pdf(window, results, score, status_callback)


def _save_text(window, results, score, ext, converter, status_callback):
    dialog = Gtk.FileDialog.new()
    dialog.set_title(_("Save Export"))
    dialog.set_initial_name(f"ordbyggaren_{datetime.now().strftime('%Y-%m-%d')}.{ext}")
    dialog.save(window, None, _on_text_done, results, score, converter, ext, status_callback)


def _on_text_done(dialog, result, results, score, converter, ext, status_callback):
    try:
        gfile = dialog.save_finish(result)
    except GLib.Error:
        return
    try:
        with open(gfile.get_path(), "w") as f:
            f.write(converter(results, score))
        if status_callback:
            status_callback(_("Exported %s") % ext.upper())
    except Exception as e:
        if status_callback:
            status_callback(_("Export error: %s") % str(e))


def _save_pdf(window, results, score, status_callback):
    dialog = Gtk.FileDialog.new()
    dialog.set_title(_("Save PDF"))
    dialog.set_initial_name(f"ordbyggaren_{datetime.now().strftime('%Y-%m-%d')}.pdf")
    dialog.save(window, None, _on_pdf_done, results, score, status_callback)


def _on_pdf_done(dialog, result, results, score, status_callback):
    try:
        gfile = dialog.save_finish(result)
    except GLib.Error:
        return
    try:
        success = export_results_pdf(results, score, gfile.get_path())
        if success and status_callback:
            status_callback(_("PDF exported"))
        elif not success and status_callback:
            status_callback(_("PDF export requires cairo."))
    except Exception as e:
        if status_callback:
            status_callback(_("Export error: %s") % str(e))
