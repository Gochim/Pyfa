import wx

import config
from eos.db.saveddata.loadDefaultDatabaseValues import DefaultDatabaseValues
from eos.db.saveddata.queries import clearPrices, clearDamagePatterns, clearTargetProfiles
from gui.bitmap_loader import BitmapLoader
from gui.preferenceView import PreferenceView
from gui.utils import helpers_wxPython as wxHelpers


class PFGeneralPref(PreferenceView):
    title = "Database"

    def populatePanel(self, panel):
        self.dirtySettings = False

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.stTitle = wx.StaticText(panel, wx.ID_ANY, self.title, wx.DefaultPosition, wx.DefaultSize, 0)
        self.stTitle.Wrap(-1)
        self.stTitle.SetFont(wx.Font(12, 70, 90, 90, False, wx.EmptyString))
        mainSizer.Add(self.stTitle, 0, wx.EXPAND | wx.ALL, 5)

        self.stSubTitle = wx.StaticText(panel, wx.ID_ANY, "(Cannot be changed while pyfa is running. Set via command line switches.)",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.stSubTitle.Wrap(-1)
        mainSizer.Add(self.stSubTitle, 0, wx.ALL, 3)

        self.m_staticline1 = wx.StaticLine(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainSizer.Add(self.m_staticline1, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        # Save in Root
        self.cbsaveInRoot = wx.CheckBox(panel, wx.ID_ANY, "Using Executable Path for Saved Fit Database and Settings", wx.DefaultPosition, wx.DefaultSize, 0)
        mainSizer.Add(self.cbsaveInRoot, 0, wx.ALL | wx.EXPAND, 5)

        # Database path
        self.stSetUserPath = wx.StaticText(panel, wx.ID_ANY, "pyfa User Path:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.stSetUserPath.Wrap(-1)
        mainSizer.Add(self.stSetUserPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.inputUserPath = wx.TextCtrl(panel, wx.ID_ANY, config.savePath, wx.DefaultPosition, wx.DefaultSize, 0)
        self.inputUserPath.SetEditable(False)
        self.inputUserPath.SetBackgroundColour((200, 200, 200))
        mainSizer.Add(self.inputUserPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        # Save DB
        self.stFitDB = wx.StaticText(panel, wx.ID_ANY, "Fitting Database:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.stFitDB.Wrap(-1)
        mainSizer.Add(self.stFitDB, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputFitDB = wx.TextCtrl(panel, wx.ID_ANY, config.saveDB, wx.DefaultPosition, wx.DefaultSize, 0)
        self.inputFitDB.SetEditable(False)
        self.inputFitDB.SetBackgroundColour((200, 200, 200))
        mainSizer.Add(self.inputFitDB, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        # Game Data DB
        self.stGameDB = wx.StaticText(panel, wx.ID_ANY, "Game Database:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.stGameDB.Wrap(-1)
        mainSizer.Add(self.stGameDB, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputGameDB = wx.TextCtrl(panel, wx.ID_ANY, config.gameDB, wx.DefaultPosition, wx.DefaultSize, 0)
        self.inputGameDB.SetEditable(False)
        self.inputGameDB.SetBackgroundColour((200, 200, 200))
        mainSizer.Add(self.inputGameDB, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        self.cbsaveInRoot.SetValue(config.saveInRoot)
        self.cbsaveInRoot.Bind(wx.EVT_CHECKBOX, self.onCBsaveInRoot)

        # self.inputUserPath.Bind(wx.EVT_LEAVE_WINDOW, self.OnWindowLeave)
        # self.inputFitDB.Bind(wx.EVT_LEAVE_WINDOW, self.OnWindowLeave)
        # self.inputGameDB.Bind(wx.EVT_LEAVE_WINDOW, self.OnWindowLeave)

        self.m_staticline3 = wx.StaticLine(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainSizer.Add(self.m_staticline3, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        btnSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer.AddStretchSpacer()

        self.btnImportDefaults = wx.Button(panel, wx.ID_ANY, "Reimport Database Defaults", wx.DefaultPosition, wx.DefaultSize, 0)
        btnSizer.Add(self.btnImportDefaults, 0, wx.ALL, 5)
        self.btnImportDefaults.Bind(wx.EVT_BUTTON, self.loadDatabaseDefaults)

        self.btnDeleteDamagePatterns = wx.Button(panel, wx.ID_ANY, "Delete All Damage Pattern Profiles", wx.DefaultPosition, wx.DefaultSize, 0)
        btnSizer.Add(self.btnDeleteDamagePatterns, 0, wx.ALL, 5)
        self.btnDeleteDamagePatterns.Bind(wx.EVT_BUTTON, self.DeleteDamagePatterns)

        self.btnDeleteTargetProfiles = wx.Button(panel, wx.ID_ANY, "Delete All Target Profiles", wx.DefaultPosition, wx.DefaultSize, 0)
        btnSizer.Add(self.btnDeleteTargetProfiles, 0, wx.ALL, 5)
        self.btnDeleteTargetProfiles.Bind(wx.EVT_BUTTON, self.DeleteTargetProfiles)

        self.btnPrices = wx.Button(panel, wx.ID_ANY, "Delete All Prices", wx.DefaultPosition, wx.DefaultSize, 0)
        btnSizer.Add(self.btnPrices, 0, wx.ALL, 5)
        self.btnPrices.Bind(wx.EVT_BUTTON, self.DeletePrices)

        mainSizer.Add(btnSizer, 0, wx.EXPAND, 5)


        panel.SetSizer(mainSizer)
        panel.Layout()

    def loadDatabaseDefaults(self, event):
        # Import values that must exist otherwise Pyfa breaks
        DefaultDatabaseValues.importRequiredDefaults()
        # Import default values for damage profiles
        DefaultDatabaseValues.importDamageProfileDefaults()
        # Import default values for target resist profiles
        DefaultDatabaseValues.importTargetProfileDefaults()

    def DeleteDamagePatterns(self, event):
        question = "This is a destructive action that will delete all damage pattern profiles.\nAre you sure you want to do this?"
        if wxHelpers.YesNoDialog(question, "Confirm"):
            clearDamagePatterns()

    def DeleteTargetProfiles(self, event):
        question = "This is a destructive action that will delete all target profiles.\nAre you sure you want to do this?"
        if wxHelpers.YesNoDialog(question, "Confirm"):
            clearTargetProfiles()

    def DeletePrices(self, event):
        question = "This is a destructive action that will delete all cached prices out of the database.\nAre you sure you want to do this?"
        if wxHelpers.YesNoDialog(question, "Confirm"):
            clearPrices()

    def onCBsaveInRoot(self, event):
        # We don't want users to be able to actually change this,
        # so if they try and change it, set it back to the current setting
        self.cbsaveInRoot.SetValue(config.saveInRoot)

        # If we ever enable it might need this.
        '''
        config.saveInRoot = self.cbsaveInRoot.GetValue()
        '''

    def getImage(self):
        return BitmapLoader.getBitmap("settings_database", "gui")


PFGeneralPref.register()
