from PyQt5.QtWidgets import QMessageBox


def _get_tr(parent):
    if hasattr(parent, 'main_window') and hasattr(parent.main_window, 'tr'):
        return parent.main_window.tr
    if hasattr(parent, 'tr'):
        return parent.tr
    return lambda x: x


def _show_msg(parent, title, text, icon, buttons):
    tr = _get_tr(parent)
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStandardButtons(buttons)
    if buttons & QMessageBox.StandardButton.Ok:
        msg.button(QMessageBox.StandardButton.Ok).setText(tr("common.ok"))
    if buttons & QMessageBox.StandardButton.Yes:
        msg.button(QMessageBox.StandardButton.Yes).setText(tr("common.yes"))
    if buttons & QMessageBox.StandardButton.No:
        msg.button(QMessageBox.StandardButton.No).setText(tr("common.no"))
    return msg.exec()


def show_info(parent, title, text):
    """Information dialog with translated OK button"""
    return _show_msg(parent, title, text, QMessageBox.Icon.Information,
                     QMessageBox.StandardButton.Ok)


def show_warning(parent, title, text):
    """Warning dialog with translated OK button"""
    return _show_msg(parent, title, text, QMessageBox.Icon.Warning,
                     QMessageBox.StandardButton.Ok)


def show_critical(parent, title, text):
    """Error dialog with translated OK button"""
    return _show_msg(parent, title, text, QMessageBox.Icon.Critical,
                     QMessageBox.StandardButton.Ok)


def show_question(parent, title, text, default_btn=QMessageBox.StandardButton.No):
    """Question dialog with translated Yes/No buttons"""
    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setStandardButtons(buttons)
    tr = _get_tr(parent)
    msg.button(QMessageBox.StandardButton.Yes).setText(tr("common.yes"))
    msg.button(QMessageBox.StandardButton.No).setText(tr("common.no"))
    msg.setDefaultButton(default_btn)
    reply = msg.exec()
    return reply == QMessageBox.StandardButton.Yes
