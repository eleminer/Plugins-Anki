import aqt
import anki
from anki.hooks import addHook


def flipCard():
    if aqt.mw.reviewer.state == "question":
        if aqt.mw.reviewer.typedAnswer is None:
            aqt.mw.reviewer.typedAnswer = ""
        aqt.mw.reviewer._showAnswer()
    elif aqt.mw.reviewer.state == "answer":
        aqt.mw.reviewer._showQuestion()


def keyHandler(shortcuts):
    additions = (("0", flipCard),("Ctrl+;", flipCard))
    shortcuts += additions


addHook("reviewStateShortcuts", keyHandler)
