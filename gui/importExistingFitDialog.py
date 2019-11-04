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

    applyToAllFitsText = "Apply to all fits"

    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, title="Fit collision", size=(-1, -1), style=wx.DEFAULT_DIALOG_STYLE)

        # data START
        shipName = "Retribution"
        fitName = "Beam PVP"
        fitsNumber = 1
        #todo generate the value in postfix field to make it unique
        #todo check if the new name is unique
        #todo add tooltips. Explain why overwrite is disabled
        #todo on change the name check if it's a correct one

        self.fitActions = OrderedDict((
            ("Overwrite", (ImportExistingFitDialog.actionOverwrite, {"Hideable": True})),
            ("Add postfix", (ImportExistingFitDialog.actionAddPostfix, {"TextCtrl": True})),
            ("Skip", (ImportExistingFitDialog.actionSkip, None)),
        ))

        self.importActionsDict = {
            ImportExistingFitDialog.actionOverwrite: self.doActionOverwrite,
            ImportExistingFitDialog.actionAddPostfix: self.doActionAddPostfix,
            ImportExistingFitDialog.actionSkip: self.doActionSkip
        }

        mainText = "Fit for the '{}' with the name '{}'\n already exists".format(shipName, fitName)
        if fitsNumber > 1:
            mainText = "There are {} for '{}' with the name '{}'".format(fitsNumber, shipName, fitName)

        # data END


        self.settings = SettingsProvider.getInstance().getSettings("pyfaImportCollisionAction", {"format": 0, "applyToAll": False})

        #todo move sizers to one place
        # Layout creation
        self.mainFrame = parent
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, wx.ID_ANY, mainText, style = wx.ALIGN_CENTER)
        mainSizer.Add(label, 0, wx.EXPAND | wx.ALL, 10)

        initialized = False
        radioSizer = wx.BoxSizer(wx.VERTICAL)
        for formatName, formatData in self.fitActions.items():
            formatId, formatOptions = formatData

            if not initialized:
                rdo = wx.RadioButton(self, wx.ID_ANY, formatName, style=wx.RB_GROUP)
                initialized = True
            else:
                rdo = wx.RadioButton(self, wx.ID_ANY, formatName)

            rdo.Bind(wx.EVT_RADIOBUTTON, self.changeSelected)
            if self.settings['format'] == formatId:
                rdo.SetValue(True)
                self.fitAction = formatId

            radioSizer.Add(rdo, 0, wx.EXPAND | wx.ALL, 5)

            # In case we have more that one fit - we can't use 'Overwrite' option
            if fitsNumber > 1 and formatOptions and formatOptions.get("Hideable"):
                rdo.Hide()

            if formatOptions and formatOptions.get("TextCtrl"):
                textSizer = wx.BoxSizer(wx.VERTICAL)
                edit = wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, (150, -1))
                textSizer.Add(edit, 0, wx.TOP | wx.BOTTOM, 3)
                radioSizer.Add(textSizer, 0, wx.EXPAND | wx.LEFT, 20)

        mainSizer.Add(radioSizer, 0, wx.EXPAND | wx.LEFT, 20)

        buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttonSizer:
            mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 5)

        # Add checkbox for "apply to all fits"
        # csizer = wx.BoxSizer(wx.VERTICAL)
        checkbox = wx.CheckBox(self, -1, self.applyToAllFitsText)
        checkbox.Bind(wx.EVT_CHECKBOX, self.changeApplyToAll)
        checkbox.SetValue(self.settings['applyToAll'])

        self.applyToAll = self.settings['applyToAll']
        # csizer.Add(checkbox, 0, wx.EXPAND | wx.ALL, 3)

        mainSizer.Add(checkbox, 0, wx.EXPAND | wx.ALL, 4)

        self.SetSizer(mainSizer)
        self.Fit()
        self.Center()

    def Validate(self):
        # Since this dialog is shown through as ShowModal(),
        # we hook into the Validate function to veto the closing of the dialog until we're ready.
        # This always returns False, and when we're ready will EndModal()
        selectedItem = self.getSelected()

        settings = SettingsProvider.getInstance().getSettings("pyfaImportCollisionAction")
        settings["format"] = selectedItem
        settings["applyToAll"] = self.applyToAll

        def cb(text):
            toClipboard(text)
            self.EndModal(wx.ID_OK)

        self.importActionsDict[selectedItem](callback=cb)

        return False

    def changeSelected(self, event):
        obj = event.GetEventObject()
        formatName = obj.GetLabel()
        self.fitAction = self.fitActions[formatName][0]
        self.Fit()

    def getSelected(self):
        return self.fitAction

    def changeApplyToAll(self, event):
        obj = event.GetEventObject()
        self.applyToAll = obj.Value


    def doActionOverwrite(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportEft(fit, None, callback)

    def doActionSkip(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportDna(fit, None, callback)

    def doActionAddPostfix(self, callback):
        fit = getFit(self.mainFrame.getActiveFit())
        Port.exportESI(fit, callback)