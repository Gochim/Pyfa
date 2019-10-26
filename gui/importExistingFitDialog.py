# =============================================================================
# Copyright (C) 2010 Lucas Thode
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


from collections import OrderedDict

# noinspection PyPackageRequirements
import wx

from eos.db import getFit
from gui.utils.clipboard import toClipboard
from service.port import Port
from service.settings import SettingsProvider


class ImportExistingFitDialog(wx.Dialog):
    actionOverwrite = 0
    actionAddPostfix = 1
    actionSkip = 2

    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, title="Fit collision", size=(-1, -1), style=wx.DEFAULT_DIALOG_STYLE)

        self.importActionsDict = {
            ImportExistingFitDialog.actionOverwrite     : self.doActionOverwrite,
            ImportExistingFitDialog.actionAddPostfix    : self.doActionAddPostfix,
            ImportExistingFitDialog.actionSkip          : self.doActionSkip
        }

        shipName = "Retribution"
        fitName = "Beam PVP"
        fitsNumber = 1

        self.mainFrame = parent
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.fitActions = OrderedDict((
            ("Overwrite", (ImportExistingFitDialog.actionOverwrite, None)),
            ("Add postfix", (ImportExistingFitDialog.actionAddPostfix, None)),
            ("Skip", (ImportExistingFitDialog.actionSkip, None)),
        ))

        self.settings = SettingsProvider.getInstance().getSettings("pyfaImportAction", {"format": 0})

        mainText = "Fit for the '{}' with the name '{}'\n already exists".format(shipName, fitName)
        if fitsNumber > 1:
            mainText = "There are {} for '{}' with the name '{}'".format(fitsNumber, shipName, fitName)

        label = wx.StaticText(self, wx.ID_ANY, mainText, style=wx.ALIGN_CENTER)
        mainSizer.Add(label, 0, wx.EXPAND | wx.ALL, 5)

        initialized = False
        for formatName, formatData in self.fitActions.items():
            formatId, formatOptions = formatData
            if not initialized:
                rdo = wx.RadioButton(self, wx.ID_ANY, formatName, style=wx.RB_GROUP)
                initialized = True
            else:
                rdo = wx.RadioButton(self, wx.ID_ANY, formatName)

            rdo.Bind(wx.EVT_RADIOBUTTON, self.selected)
            if self.settings['format'] == formatId:
                rdo.SetValue(True)
                self.fitAction = formatId
            mainSizer.Add(rdo, 0, wx.EXPAND | wx.ALL, 5)

        buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttonSizer:
            mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.Fit()
        self.Center()

    def Validate(self):
        # Since this dialog is shown through as ShowModal(),
        # we hook into the Validate function to veto the closing of the dialog until we're ready.
        # This always returns False, and when we're ready will EndModal()
        selectedItem = self.getSelected()

        settings = SettingsProvider.getInstance().getSettings("pyfaImportAction")
        settings["format"] = selectedItem

        def cb(text):
            toClipboard(text)
            self.EndModal(wx.ID_OK)

        self.importActionsDict[selectedItem](callback=cb)

        return False

    def selected(self, event):
        obj = event.GetEventObject()
        formatName = obj.GetLabel()
        self.fitAction = self.fitActions[formatName][0]
        self.Fit()

    def getSelected(self):
        return self.fitActions

    def doActionOverwrite(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportEft(fit, None, callback)

    def doActionSkip(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportDna(fit, None, callback)

    def doActionAddPostfix(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportESI(fit, callback)