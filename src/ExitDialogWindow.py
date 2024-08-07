from PyQt6.QtWidgets import QMessageBox


def exitDialog(parent, window_type: str | None = None):
    if window_type:
        text = f"Are you sure you want to close the {window_type} window?"
    else:
        text = "Are you sure you want to close the window?"
    confirmation = QMessageBox.question(
        parent,
        "Warning",
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )

    if confirmation == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False
