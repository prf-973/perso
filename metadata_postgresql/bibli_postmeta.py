# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit,  QMainWindow) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
                     
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayerCache, QgsFeatureRequest, QgsSettings, QgsDataSourceUri, QgsCredentials
 
from qgis.utils import iface
import psycopg2

from qgis.gui import (QgsAttributeTableModel, QgsAttributeTableView, QgsLayerTreeViewMenuProvider, QgsAttributeTableFilterModel)
from qgis.utils import iface

from qgis.core import *
from qgis.gui import *
import qgis                              
import os                       
import datetime
import os.path
import time

#========================================================
#========================================================
def dicListSql(mKeySql):
    mdicListSql = {}

    #------------------
    # TESTS EN COURS
    #-----------------
    #Fonction tests 
    mdicListSql['Fonction_Tests'] = ("""
                  SELECT nombase, schema, nomobjet, typeobjet, etat FROM z_replique.replique;
                                          """) 
    mdicListSql['Fonction_Tests_SELECT'] = (""" SELECT * FROM "#schema#"."#table#"; """) 

    return  mdicListSql[mKeySql]

#==================================================
def test_interaction_sql(self) :
    mKeySql = dicListSql("Fonction_Tests_SELECT")                
    #**********************
    mSchemaNew, mSchemaOld = self.schema, "#schema#"
    mTableNew,  mTableOld  = self.table, "#table#"
    dicReplace = {mSchemaOld: mSchemaNew, mTableOld: mTableNew}
    #**********************
    for key, value in dicReplace.items():
        if isinstance(value, bool) :
           mValue = str(value)
        elif (value is None) :
           mValue = "''"
        else :
           value = value.replace("'", "''")
           mValue =  str(value) 
        mKeySql = mKeySql.replace(key, mValue)
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql)

    # A SUPPRIMER
    self.textTest = "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence." 
    for k, v in self.mDicObjetsInstancies.items() :
        if v['value'] == self.textTest :
           self.mDicObjetsInstancies[k]['main widget'].setText(str(r))
           break
    # A SUPPRIMER

#==================================================
def executeSql(pointeurBase, _mKeySql) :
    zMessError_Code, zMessError_Erreur, zMessError_Diag = '', '', ''
    QApplication.instance().setOverrideCursor(Qt.WaitCursor) 
    try :
      pointeurBase.execute(_mKeySql)
      result = pointeurBase.fetchall()
          
    except Exception as err:
      QApplication.instance().setOverrideCursor(Qt.ArrowCursor) 
      result = None
      zMessError_Code   = (str(err.pgcode) if hasattr(err, 'pgcode') else '')
      zMessError_Erreur = (str(err.pgerror) if hasattr(err, 'pgerror') else '')
      print("err.pgcode = %s" %(zMessError_Code))
      print("err.pgerror = %s" %(zMessError_Erreur))
      #zMessError_Erreur = cleanMessError(zMessError_Erreur)
      #dialogueMessageError(mTypeErreur, zMessError_Erreur )   
      #-------------

    QApplication.instance().setOverrideCursor(Qt.ArrowCursor) 
    return result, zMessError_Code, zMessError_Erreur, zMessError_Diag


#==================================================
def resizeIhm(self, l_Dialog, h_Dialog) :
    #----
    x, y = 10, 25
    larg, haut =  self.Dialog.width() -20, (self.Dialog.height() - self.groupBoxDown.height() -40 )
    self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))
    #----
    x, y = 0, 0 
    larg, haut =  self.tabWidget.width()-5, self.tabWidget.height()-25
    for elem in self.listeResizeIhm :
        elem.setGeometry(QtCore.QRect(x, y, larg, haut))
    #----
    self.Dialog.groupBoxDown.setGeometry(QtCore.QRect(10,h_Dialog - 50,l_Dialog -20,40))    
    self.okhButton.setGeometry(QtCore.QRect(((self.Dialog.groupBoxDown.width() -200) / 3) + 100 + ((self.Dialog.groupBoxDown.width() -200) / 3), 10, 100,23))
    self.helpButton.setGeometry(QtCore.QRect((self.Dialog.groupBoxDown.width() -200) / 3, 10, 100,23))
    #----
    #----
    #Réinit les dimensions de l'IHM
    returnAndSaveDialogParam(self, "Save")
    self.mDic_LH = returnAndSaveDialogParam(self, "Load")
    self.Dialog.lScreenDialog, self.Dialog.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
    #----
    return  

#==================================================
#Lecture du fichier ini pour dimensions Dialog
#==================================================
def returnAndSaveDialogParam(self, mAction):
    mDicAutre = {}
    mDicAutreColor = {}
    mDicAutrePolice = {}
    mSettings = QgsSettings()
    mSettings.beginGroup("POSTMETA")
    mSettings.beginGroup("Generale")
    
    if mAction == "Load" :
       #Ajouter si autre param
       valueDefautL = 810
       valueDefautH = 640
       valueDefautDisplayMessage = "dialogBox"
       valueDefautFileHelp  = "html"
       valueDefautFileHelpPdf   = "https://snum.scenari-community.org/Asgard/PDF/GuideAsgardManager"
       valueDefautFileHelpHtml  = "https://snum.scenari-community.org/Asgard/Documentation/#SEC_AsgardManager"
       valueDefautDurationBarInfo = 10
       valueDefautIHM = "window"
       mDicAutre["dialogLargeur"]  = valueDefautL
       mDicAutre["dialogHauteur"]  = valueDefautH
       mDicAutre["displayMessage"] = valueDefautDisplayMessage
       mDicAutre["fileHelp"]       = valueDefautFileHelp
       mDicAutre["fileHelpPdf"]    = valueDefautFileHelpPdf
       mDicAutre["fileHelpHtml"]   = valueDefautFileHelpHtml
       mDicAutre["durationBarInfo"]= valueDefautDurationBarInfo
       mDicAutre["ihm"]            = valueDefautIHM

       for key, value in mDicAutre.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutre[key] = mSettings.value(key)
       #--                  
       mSettings.endGroup()
       mSettings.beginGroup("BlocsColor")
       #Ajouter si autre param
       mDicAutreColor["defaut"]                      = "#958B62"
       mDicAutreColor["QGroupBox"]                   = "#BADCFF"
       mDicAutreColor["QGroupBoxGroupOfProperties"]  = "#7560FF"
       mDicAutreColor["QGroupBoxGroupOfValues"]      = "#00FF21"
       mDicAutreColor["QGroupBoxTranslationGroup"]   = "#0026FF"
       mDicAutreColor["QTabWidget"]                  = "#958B62"
       mDicAutreColor["QLabelBackGround"]            = "#BFEAE2"

       for key, value in mDicAutreColor.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutreColor[key] = mSettings.value(key)           
       #----
       mDicAutre = {**mDicAutre, **mDicAutreColor}          
       #--                  

       mSettings.endGroup()
       mSettings.beginGroup("BlocsPolice")
       #Ajouter si autre param
       mDicAutrePolice["QEdit"] = "outset"
       mDicAutrePolice["QGroupBoxEpaisseur"] = 1
       mDicAutrePolice["QGroupBoxLine"]    = "dashed"
       mDicAutrePolice["QGroupBoxPolice"]  = "Marianne"
       mDicAutrePolice["QTabWidgetPolice"] = "Helvetica"

       for key, value in mDicAutrePolice.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutrePolice[key] = mSettings.value(key)           
       #----
       mDicAutre = {**mDicAutre, **mDicAutrePolice}          
    elif mAction == "Save" :
       mDicAutre["dialogLargeur"] = self.Dialog.width()
       mDicAutre["dialogHauteur"] = self.Dialog.height()
                 
       for key, value in mDicAutre.items():
           mSettings.setValue(key, value)

    mSettings.endGroup()
    mSettings.endGroup()    
    return mDicAutre

#==================================================
def returnVersion() : return "version 0.1.0"

#==================================================
#Execute Pdf 
#==================================================
def execPdf(nameciblePdf):
    paramGlob = nameciblePdf            
    os.startfile(paramGlob)

    return            
#==================================================
def getThemeIcon(theName):
    myPath = CorrigePath(os.path.dirname(__file__))
    myDefPathIcons = myPath + "\\icons\\logo\\"
    myDefPath = myPath.replace("\\","/")+ theName
    myDefPathIcons = myDefPathIcons.replace("\\","/")+ theName
    myCurThemePath = QgsApplication.activeThemePath() + "/plugins/" + theName
    myDefThemePath = QgsApplication.defaultThemePath() + "/plugins/" + theName
    myQrcPath = "python/plugins/postmeta/" + theName
    if QFile.exists(myDefPath): return myDefPath
    elif QFile.exists(myDefPathIcons): return myDefPathIcons
    elif QFile.exists(myCurThemePath): return myCurThemePath
    elif QFile.exists(myDefThemePath): return myDefThemePath
    elif QFile.exists(myQrcPath): return myQrcPath
    else: return theName

#==================================================
def CorrigePath(nPath):
    nPath = str(nPath)
    a = len(nPath)
    subC = "/"
    b = nPath.rfind(subC, 0, a)
    if a != b : return (nPath + "/")
    else: return nPath

#==================================================
#==================================================
#==================================================
def displayMess(mDialog, type,zTitre,zMess, level=Qgis.Critical, duration = 10):
    #type 1 = MessageBar
    #type 2 = QMessageBox
    if type == 1 :
       mDialog.barInfo.clearWidgets()
       mDialog.barInfo.pushMessage(zTitre, zMess, level=level, duration = duration)
    else :
       QMessageBox.information(None,zTitre,zMess)
    return  
#--
def debugMess(type,zTitre,zMess, level=Qgis.Critical):
    #type 1 = MessageBar
    #type 2 = QMessageBox
    if type == 1 :
       qgis.utils.iface.messageBar().pushMessage(zTitre, zMess, level=level)
    else :
       QMessageBox.information(None,zTitre,zMess)
    return  

#==================================================
# FIN
#==================================================