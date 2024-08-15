from ExitDialogWindow import exitDialog


def test_exit_dialog(qWindow, window_type):
    do_exit = exitDialog(qWindow, window_type)

    assert do_exit == True or do_exit == False
