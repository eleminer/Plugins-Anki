import random
# import sys
import anki
import aqt
import aqt.qt
import aqt.deckconf

import PyQt5
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
# from PyQt5.QtWidgets import QWidget, QApplication, QPushButton


def my_fillRev(self):
    deckConf = self.col.decks.confForDid(self.col.decks.current()["id"])
    reviewOrder = deckConf.get("reviewOrder", 0)
    # print "reviewOrder", reviewOrder
    if reviewOrder == 1:
        # modified to sort cards
        if self._revQueue:
            return True
        if not self.revCount:
            return False
        while self._revDids:
            did = self._revDids[0]
            lim = min(self.queueLimit, self._deckRevLimit(did))
            if lim:
                # fill the queue with the current did
                self._revQueue = self.col.db.list("""
    select id from cards where
    did = ? and queue = 2 and due <= ? order by id limit ?""",
                                                  did, self.today, lim)
                if self._revQueue:
                    self._revQueue.reverse()
                    # is the current did empty?
                    if len(self._revQueue) < lim:
                        self._revDids.pop(0)
                    return True
            # nothing left in the deck; move to next
            self._revDids.pop(0)
        if self.revCount:
            # if we didn't get a card but the count is non-zero,
            # we need to check again for any cards that were
            # removed from the queue but not buried
            self._resetRev()
            return self._fillRev()
    else:
        # original _fillRev
        if self._revQueue:
            return True
        if not self.revCount:
            return False
        while self._revDids:
            did = self._revDids[0]
            lim = min(self.queueLimit, self._deckRevLimit(did))
            if lim:
                # fill the queue with the current did
                self._revQueue = self.col.db.list("""
select id from cards where
did = ? and queue = 2 and due <= ? limit ?""",
                                                  did, self.today, lim)
                if self._revQueue:
                    # ordering
                    if self.col.decks.get(did)['dyn']:
                        # dynamic decks need due order preserved
                        self._revQueue.reverse()
                    else:
                        # random order for regular reviews
                        r = random.Random()
                        r.seed(self.today)
                        r.shuffle(self._revQueue)
                    # is the current did empty?
                    if len(self._revQueue) < lim:
                        self._revDids.pop(0)
                    return True
            # nothing left in the deck; move to next
            self._revDids.pop(0)
        if self.revCount:
            # if we didn't get a card but the count is non-zero,
            # we need to check again for any cards that were
            # removed from the queue but not buried
            self._resetRev()
            return self._fillRev()


def indexChanged(self, i):
    # 0 = random, 1 = order added
    self.reviewOrder = i


def myOnRestore(self):
    self.form.myComboBox.setCurrentIndex(0)
    self.reviewOrder = 0


def mySaveConf(self):
    self.conf['reviewOrder'] = self.reviewOrder


def myLoadConf(self):
    if "reviewOrder" in self.conf:
        self.reviewOrder = self.conf["reviewOrder"]
    else:
        self.reviewOrder = 0
    self.form.myComboBox.setCurrentIndex(self.reviewOrder)


def mySetupCombos(self):
    self.form.myLabel = PyQt5.QtWidgets.QLabel("Order")
    self.form.myComboBox = PyQt5.QtWidgets.QComboBox()
    self.form.myComboBox.addItems(["Show review cards in random order",
                                   "Show review cards in order added"])

    self.form.myComboBox.currentIndexChanged.connect(self.indexChanged)

    self.form.myLabel.show()
    self.form.gridLayout_3.addWidget(self.form.myLabel, 7, 0, 1, 3)
    self.form.gridLayout_3.addWidget(self.form.myComboBox, 7, 1, 1, 3)


anki.sched.Scheduler._fillRev = my_fillRev
aqt.deckconf.DeckConf.setupCombos = anki.hooks.wrap(
    aqt.deckconf.DeckConf.setupCombos,
    mySetupCombos)
aqt.deckconf.DeckConf.onRestore = anki.hooks.wrap(
    aqt.deckconf.DeckConf.onRestore,
    myOnRestore)
aqt.deckconf.DeckConf.saveConf = anki.hooks.wrap(
    aqt.deckconf.DeckConf.saveConf,
    mySaveConf)
aqt.deckconf.DeckConf.loadConf = anki.hooks.wrap(
    aqt.deckconf.DeckConf.loadConf,
    myLoadConf)
aqt.deckconf.DeckConf.indexChanged = indexChanged


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = my_fillRev("col 1")
#     window.show()
#
#     sys.exit(app.exec_())