# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from aqt.deckbrowser import DeckBrowser
from anki.find import *
from anki.utils import fmtTimeSpan, intTime, ids2str

from anki.hooks import addHook

def cram():
    # get all cards of the current deck
    idsCurrentDeck = mw.col.findCards('"deck:current"')
    #############################
    # remove cards that were answered in the last session
    count = 0
    listOfAnsweredCards = []
    for cid in idsCurrentDeck:
        # get last results for each card
        sqlstring = "select ease from revlog where cid = %s" % str(cid)
        out = mw.col.db.all(sqlstring)
        nested = list(reversed(out))
        flat = [i for sublist in nested for i in sublist]
        # remove card from current deck if the last two answers were correct
        try:
            if ((flat[0]==2) and (flat[1]==2)):
                listOfAnsweredCards.append(cid)
                count += 1
        except:
            pass

    mw.col.sched.remFromDyn(listOfAnsweredCards)
    # show a message box
    showInfo(str(count) + " cards removed")
    mw.reset()

# create a new menu item
action = QAction("Cram - Rebuild without known cards of last session", mw)
# set it to call cram() when it's clicked and the right window is open
action.triggered.connect(cram)
# add it to the tools menu
menu = mw.form.menubar.addMenu('&Cram')
menu.addAction(action)