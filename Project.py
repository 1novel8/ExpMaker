#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Aleksei Konkov'

import pyodbc
import time
import sys
import shutil
import os.path
from PyQt4 import QtGui, QtCore
from Expl import Control, Convert, ExpA, FormB, Sprav
from Expl.DefaultSprav import default

def get_f22_notes():
    f22_notes = FormB.select_sprav('Select F22Code, Notes from S_Forma22')
    f22_n_dict = {}
    for row in f22_notes:
        f22_n_dict[row[0]] = row[1]
    return f22_n_dict

class ControlThread(QtCore.QThread):
    def __init__(self, dbf, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.dbfile = dbf
        self.controlpassed = False
    def run(self):
        contr_message = self.run_control(self.dbfile)
        if self.controlpassed:
            self.emit(QtCore.SIGNAL(u'controlpassed'))
        self.emit(QtCore.SIGNAL(u's1(const QString&)'), u'%s' % contr_message)

    def run_control(self, dbfile):
        contr = Control.DataControl(dbfile)
        errList = contr.run_field_control()
        if errList:
            protocol = u'\nКонтроль исходных данных завершен. Протокол ошбок:\n\n' % time.strftime(u"\n%d.%m.%Y   %H:%M   ")
            for err in errList:
                for i in err:
                    protocol += unicode(i) + u'     '
                protocol += u'\n'
            return protocol
        else:
            self.controlpassed = True
            return u'%s Контроль завершен успешно, несоответствий не обнаружено. Можно приступить к конвертации данных.\n' % time.strftime(u"\n%d.%m.%Y   %H:%M   ")

class ConvertThread(QtCore.QThread):
    def __init__(self, dbf, b2e, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.dbfile = dbf
        self.b2e = b2e
        self.convpassed = False
        self.converted_rows = []
    def run(self):
        convmessage = self.runConv()
        if self.convpassed:
            self.emit(QtCore.SIGNAL(u'convertpassed'))
        self.emit(QtCore.SIGNAL(u's2(const QString&)'), u'%s' % convmessage)

    def runConv(self):
        dict_with_err, self.converted_rows = Convert.convert(self.dbfile, self.b2e)
        if dict_with_err:
            protocol = u'%sКонвертация данных завершена. Найдены несоответствия с таблицей BGDtoEKP:' % time.strftime(u"\n%d.%m.%Y   %H:%M   ")
            for key in dict_with_err:
                protocol += u'\n\nДля UserN_%s найдены ошибки в объектах:\n' % key
                protocol += unicode(dict_with_err[key])
            return protocol
        else:
            self.convpassed = True
            return u'\n%sДанные успешно сконвертированы. Доступен расчет экспликаций.\n' % time.strftime(u"%d.%m.%Y   %H:%M   ")

class ExpAThread(QtCore.QThread):
    def __init__(self, edbf, rows, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.expdir = edbf
        self.expsA = ExpA.ExpFA(self.expdir, rows)
        self.exp_tree = self.expsA.make_exp_tree()
    def run(self):
        self.expsA.transferToIns()

class ExpBThread(QtCore.QThread):
    def __init__(self, edbf, rows, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.expfile = edbf
        self.rows = rows
    def run(self):
        ExpB = FormB.ExpFormaB(self.expfile, self.rows)
        ExpB.run_exp_b()

class BGDtoEThread(QtCore.QThread):
    def __init__(self, newfields, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.nf = newfields
    def run(self):
        sprav = Sprav.BGDtoERemaker()
        if sprav.sprav_connected:
            if sprav.losttables:
                pos = u'ет таблица' if len(sprav.losttables) == 1 else u'ют таблицы'
                self.emit(QtCore.SIGNAL(u'lost_table(const QString&)'), u'''\
Внимание!\n
В базе данных Spravochnik.mdb отсутству%s:\n%s
Для дальнейшего расчета экспликации необходимо
предоставить справочную информацию в полном объеме.''' % (pos,unicode(sprav.losttables)[1:-1]))
            elif sprav.badfields:
                for key in sprav.badfields:
                    pos1, pos2 = (u'ет',u'е') if len(sprav.badfields[key]) == 1 else (u'ют',u'я')
                    self.emit(QtCore.SIGNAL(u'lost_field(const QString&)'), u'''\
Внимание!\n
В таблице %s отсутству%s либо не соответству%s типу пол%s:\n%s
Дальнейший расчет будет выполнен на основе запрограммированных данных.
Данные из таблицы %s использованы не будут.''' % (key,pos1,pos1,pos2,unicode(sprav.badfields)[1:-1],key))
            elif self.nf:
                bgdtab = sprav.remakeBGD2(True)
                self.emit(QtCore.SIGNAL(u'bgd_table(PyQt_PyObject)'), bgdtab)
            else:
                bgdtab = sprav.remakeBGD2()
                self.emit(QtCore.SIGNAL(u'bgd_table(PyQt_PyObject)'), bgdtab)
        else:
            self.emit(QtCore.SIGNAL(u'failure_conn(const QString&)'), u'Не удалось подключиться к базе данных Spravochnik.mdb')

class LoadingThread(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
    def run(self):
        count = 0
        while True:
            self.emit(QtCore.SIGNAL(u's_loading(const QString&)'), u'. '*count)
            self.msleep(700)
            if count == 5:
                count = 1
            else: count += 1

class MyWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.__a_thr_reinit = False
        self.db_file = None
        self.e_db_file = None
        self.setWindowTitle(u'Создание экспликации')
        self.resize(1200, 700)
        self.centralwidget = QtGui.QFrame(self)
        self.centralwidget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.centralwidget.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.l1 = QtGui.QLabel(u"   1. Контроль",self.centralwidget)
        self.l2 = QtGui.QLabel(u"   2. Конвертация",self.centralwidget)
        self.l3 = QtGui.QLabel(u"   3. Расчет экспликации A",self.centralwidget)
        self.l4 = QtGui.QLabel(u"   4. Расчет экспликации B",self.centralwidget)
        self.loadinglbl = QtGui.QLabel(u'', self.centralwidget)
        self.loadinglbl.hide()
        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.control_btn = QtGui.QPushButton(u"Запустить",self.centralwidget)
        self.control_btn.setToolTip(u"Запустить контроль базы данных")
        self.control_btn.setSizePolicy(self.sizePolicy)
        self.convert_btn = QtGui.QPushButton(u"Запустить",self.centralwidget)
        self.convert_btn.setToolTip(u"Начать конвертацию базы данных для дальнейшего расчета экспликации")
        self.convert_btn.setSizePolicy(self.sizePolicy)
        self.exp_a_btn = QtGui.QPushButton(u"Расчитать",self.centralwidget)
        self.exp_a_btn.setToolTip(u"Запустить расчет экспликации A")
        self.exp_a_btn.setSizePolicy(self.sizePolicy)
        self.btn_a_all = QtGui.QPushButton(u"Полный",self.centralwidget)
        self.btn_a_all.setToolTip(u"Полный расчет экспликаций A. ")
        self.btn_a_tree = QtGui.QPushButton(u"Выборочный",self.centralwidget)
        self.btn_a_tree.setToolTip(u"Выборочный расчет экспликации A")
        self.btn_a_tree.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setSizePolicy(self.sizePolicy)
        self.btn_a_all.setHidden(True)
        self.btn_a_tree.setHidden(True)
        self.exp_b_btn = QtGui.QPushButton(u"Расчет",self.centralwidget)
        self.exp_b_btn.setToolTip(u"Запустить расчет экспликации B")
        self.exp_b_btn.setSizePolicy(self.sizePolicy)
        self.gridLayout.addWidget(self.l1, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.l2, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.l3, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.l4, 7, 0, 1, 1)
        self.gridLayout.addWidget(self.control_btn, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.convert_btn, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.exp_a_btn, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_a_tree,  4, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_a_all,  5, 1, 1, 1)
        self.gridLayout.addWidget(self.exp_b_btn, 7, 1, 1, 1)
        self.gridLayout.addWidget(self.loadinglbl, 13, 0, 1, 5)
        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.clearbutton = QtGui.QPushButton(u"Очистить окно сообщений",self.centralwidget)
        self.gridLayout.addWidget(self.clearbutton, 13, 11, 1, 1)
        # self.clearbutton.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)...
        self.setWindowIcon(QtGui.QIcon(u"D:\\pytoexe\\Icons\\up.png"))
        self.setCentralWidget(self.centralwidget)
        self.treeView = QtGui.QTreeView()
        self.treeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeView.setHidden(True)
        self.tree_text_widg = QtGui.QWidget()
        self.tree_text_vbox = QtGui.QVBoxLayout(self.tree_text_widg)
        self.tree_text_vbox.addWidget(self.treeView,4)
        self.tree_text_vbox.addWidget(self.textEdit,2)
        self.gridLayout.addWidget(self.tree_text_widg, 0, 2, 12, 11)
        self.setFocus()
        self.set_menu_properties()
        self.hide_props()
        self.connect(self.clearbutton, QtCore.SIGNAL(u"clicked()"), self.textEdit.clear)
        self.connect(self.control_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_control_btn()"))
        self.connect(self.convert_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_convert_btn()"))
        self.connect(self.exp_a_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_exp_a_btn()"))
        self.connect(self.btn_a_all, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_btn_a_all()"))
        self.connect(self.btn_a_tree, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_btn_a_tree()"))
        self.connect(self.exp_b_btn, QtCore.SIGNAL(u"clicked()"), QtCore.SLOT(u"on_clicked_exp_b_btn()"))
        self.show()
        self.b2e_li = default
        self.recountBGD()
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setStyleSheet((open('d:\workspace\PyQt\ss.css').read()))
        self.bold_font = QtGui.QFont()
        self.normal_font = QtGui.QFont()
        self.set_fonts_properties()
        self.set_widgets_font()
        self.set_sources_widgets()

    def set_sources_widgets(self):
        self.src_widget = QtGui.QWidget()
        self.src_h_box = QtGui.QHBoxLayout(self.src_widget)
        self.src_btn = QtGui.QToolButton()
        self.src_btn.setText(u'...')
        self.src_lbl = QtGui.QLabel(u'Источник данных', self.src_widget)
        self.src_lbl.setFont(QtGui.QFont('Segoe Print',9))
        self.src_btn.setAutoRaise(True)
        self.src_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.src_h_box.addWidget(self.src_lbl)
        self.src_h_box.addWidget(self.src_btn)
        self.gridLayout.addWidget(self.src_widget, 0,0,1,2)
        self.e_src_widget = QtGui.QWidget()
        self.e_src_h_box = QtGui.QHBoxLayout(self.e_src_widget)
        self.e_src_btn = QtGui.QToolButton()
        self.e_src_btn.setText(u'...')
        self.e_src_lbl = QtGui.QLabel(u'', self.e_src_widget)
        self.e_src_lbl.setFont(QtGui.QFont('Segoe Print',9))
        self.e_src_btn.setAutoRaise(True)
        self.e_src_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.e_src_h_box.addWidget(self.e_src_lbl)
        self.e_src_h_box.addWidget(self.e_src_btn)
        self.gridLayout.addWidget(self.e_src_widget, 8,0,1,2)
        self.e_src_widget.hide()
        self.connect(self.src_btn, QtCore.SIGNAL(u'clicked()'), self.open_file)
        self.connect(self.e_src_btn, QtCore.SIGNAL(u'clicked()'), self.get_edbf_name)

    def set_widgets_font(self):
        self.l1.setFont(self.normal_font)
        self.l2.setFont(self.normal_font)
        self.l3.setFont(self.normal_font)
        self.l4.setFont(self.normal_font)
        self.clearbutton.setFont(self.bold_font)
        self.textEdit.setFont(self.normal_font)
        self.btn_a_tree.setFont(self.bold_font)
        self.btn_a_all.setFont(self.bold_font)
        self.control_btn.setFont(self.bold_font)
        self.convert_btn.setFont(self.bold_font)
        self.exp_a_btn.setFont(self.bold_font)
        self.exp_b_btn.setFont(self.bold_font)

    def set_fonts_properties(self):
        self.normal_font.setPointSize(10)
        self.bold_font.setPointSize(10)
        self.bold_font.setBold(True)
        self.normal_font.setFamily('Dutch801 XBd Bt')#'Narkisim',
        self.bold_font.setFamily('Times New Roman')
    def hide_props(self, hide = True):
        self.l1.setHidden(hide)
        self.l2.setHidden(hide)
        self.l3.setHidden(hide)
        self.l4.setHidden(hide)
        self.control_btn.setHidden(hide)
        self.convert_btn.setHidden(hide)
        self.exp_a_btn.setHidden(hide)
        self.exp_b_btn.setHidden(hide)

    def block_btns(self, blocked = True):
        self.control_btn.blockSignals(blocked)
        self.convert_btn.blockSignals(blocked)
        self.exp_a_btn.blockSignals(blocked)
        self.exp_b_btn.blockSignals(blocked)

    def set_menu_properties(self):
        main_exit1 = QtGui.QAction(QtGui.QIcon(u'D:\\pytoexe\\Icons\\a5.png'), u'Открыть', self)
        main_exit2 = QtGui.QAction(QtGui.QIcon(u'D:\\pytoexe\\Icons\\stop1.png'), u'Закрыть', self)
        main_exit1.setShortcut(u'Ctrl+O')
        main_exit1.setStatusTip(u'Определение источника данных')
        main_exit2.setShortcut(u'Ctrl+Q')
        main_exit2.setStatusTip(u'Закрыть программу')
        self.connect(main_exit1, QtCore.SIGNAL(u'triggered()'), self.open_file)
        self.connect(main_exit2, QtCore.SIGNAL(u'triggered()'), QtGui.qApp, QtCore.SLOT(u'quit()'))
        spr_exit1 = QtGui.QAction(QtGui.QIcon(u'D:\\pytoexe\\Icons\\refresh.png'), u'Обновить BGDtoEKP', self)
        spr_exit2 = QtGui.QAction(QtGui.QIcon(u'D:\\pytoexe\\Icons\\refresh.png'), u'Обновить BGDtoEKP ("*_NEW")', self)
        spr_exit3 = QtGui.QAction(QtGui.QIcon(u'D:\\pytoexe\\Icons\\exclamation.png'), u'Использовать BGDtoEKP по умолчанию', self)
        spr_exit1.setShortcut(u'Ctrl+U')
        spr_exit1.setStatusTip(u'Обновление справочной таблицы BGDtoEKP')
        spr_exit2.setShortcut(u'Ctrl+Y')
        spr_exit2.setStatusTip(u'Обновление справочной таблицы BGDtoEKP\nc использованием дополнительных полей')
        spr_exit3.setShortcut(u'Ctrl+Y')
        spr_exit3.setStatusTip(u'Использовать данные BGDtoEKP статически загруженные в программу')
        self.connect(spr_exit1, QtCore.SIGNAL(u'triggered()'), self.recountBGD)
        self.connect(spr_exit2, QtCore.SIGNAL(u'triggered()'), lambda: self.recountBGD(True))
        self.connect(spr_exit3, QtCore.SIGNAL(u'triggered()'), self.set_b2e_default)
        menu = self.menuBar()
        menu_file = menu.addMenu(u'Файл')
        menu_sprav = menu.addMenu(u'Справочники')
        menu_file.addAction(main_exit1)
        menu_file.addAction(main_exit2)
        menu_sprav.addAction(spr_exit1)
        menu_sprav.addAction(spr_exit2)
        menu_sprav.addAction(spr_exit3)

    def reset_parameters(self):
        self.e_db_file = None
        self.hide_props(False)
        self.btn_a_all.setHidden(True)
        self.btn_a_tree.setHidden(True)
        self.treeView.setHidden(True)
        self.treeView.reset()
        # self.button1.setEnabled(False)
        # self.button2.setEnabled(False)
        self.exp_a_btn.setEnabled(False)
        self.exp_b_btn.setEnabled(False)
        self.e_src_widget.hide()
    def open_file(self):
        self.db_file = unicode(QtGui.QFileDialog.getOpenFileName(self, u'Укажите путь к базе данных...', u'\home'))
        if self.db_file:
            message = self.prepare_control(self.db_file)
            if not message:
                self.reset_parameters()
                self.add_visible_log(u'Открыт файл %s' % self.db_file, True)
                self.add_visible_log(u'В базе данных %s присутствуют данные, необходимые для расчета экспликации.' % self.db_file.split(u'/')[-1])
                self.add_visible_log(u'Запустите контроль данных для дальнейшей работы\n')
                self.control_btn.setEnabled(True)
                self.control_btn.blockSignals(False)
                self.src_lbl.setText(self.db_file)
                self.src_lbl.repaint()
            else:
                self.my_event(message)

    def my_event(self, messag):
        reply = QtGui.QMessageBox.question(self, u'Хотите продолжить работу?',messag,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.statusBar().showMessage(u'Ready')
        else:
            sys.exit()

    @staticmethod
    def prepare_control(file_path):
        contr = Control.DataControl(file_path)
        if not contr.try_to_connect:
            return u'Не удалось соединиться с базой данных'
        need_table = contr.contr_tables()
        table_message = u'Отсутствуют таблицы '
        tab_err = 0
        for tabl in need_table:
            if not tabl[1]:
                tab_err = 1
                table_message+= tabl[0] + u', '
        if tab_err == 1:
            return table_message
        else:
            return 0

    def enable_b2(self):
        self.convert_btn.setEnabled(True)
    def enable_b3_b4(self):
        self.exp_a_btn.setEnabled(True)
        self.exp_b_btn.setEnabled(True)

    def on_finished(self):
        self.block_btns(False)
        self.loadthread.terminate()
        self.loadinglbl.hide()
        self.statusBar().showMessage(u'Ready')

    def addloading(self, loadmessage):
        self.loadthread = LoadingThread()
        self.loadinglbl.show()
        self.lblmessage = loadmessage
        self.connect(self.loadthread, QtCore.SIGNAL(u's_loading(const QString&)'), self.set_lbl)
        self.loadthread.start()

    def set_lbl(self, dots):
        mes = self.lblmessage+dots
        self.loadinglbl.setText(mes)

    def set_b2e_default(self):
        self.b2e_li = default
        self.statusBar().showMessage(u'Ready')
        self.add_visible_log(u'Установлены исходные справочные данные. Таблица BGDtoEKP не используется', True)
    def set_b2e(self, bgd_sprav):
        self.b2e_li = bgd_sprav
        self.statusBar().showMessage(u'Ready')
        self.add_visible_log(u'Загрузка справочной информации завершена успешно\n', True)
    def recountBGD(self, bgdparam = False):
        self.bgd_thread = BGDtoEThread(bgdparam)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'bgd_table(PyQt_PyObject)'), self.set_b2e)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'failure_conn(const QString&)'), self.my_event)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'lost_table(const QString&)'), self.my_event)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'lost_field(const QString&)'), self.my_event)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'failure_conn(const QString&)'), self.set_b2e_default)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'lost_table(const QString&)'), self.set_b2e_default)
        self.connect(self.bgd_thread, QtCore.SIGNAL(u'lost_field(const QString&)'), self.set_b2e_default)
        self.bgd_thread.start()
        self.statusBar().showMessage(u'Busy')
    def newRecountBGD(self):
        self.recountBGD(True)

    @QtCore.pyqtSlot()
    def on_clicked_control_btn(self):
        self.block_btns()
        self.add_visible_log(u'Запущен контроль данных.',True)
        self.addloading(u'Производится контроль данных ')
        self.control_thr = ControlThread(self.db_file)
        self.connect(self.control_thr, QtCore.SIGNAL(u'controlpassed'), self.enable_b2)
        self.connect(self.control_thr, QtCore.SIGNAL(u's1(const QString&)'), self.add_visible_log)
        self.connect(self.control_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
        self.control_thr.start()
        self.statusBar().showMessage(u'Busy')

    @QtCore.pyqtSlot()
    def on_clicked_convert_btn(self):
        self.block_btns()
        self.add_visible_log(u'Запущено конвертирование данных.', True)
        self.convert_thr = ConvertThread(self.db_file, self.b2e_li)
        self.addloading(u'Данные конвертируются ')
        self.connect(self.convert_thr, QtCore.SIGNAL(u'convertpassed'), self.enable_b3_b4)
        self.connect(self.convert_thr, QtCore.SIGNAL(u's2(const QString&)'), self.textEdit.insertPlainText)
        self.connect(self.convert_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
        self.convert_thr.start()
        self.statusBar().showMessage(u'Busy')

    def get_edbf_name(self):
        exp_dir = unicode(QtGui.QFileDialog.getExistingDirectory(self, u'Выберите путь для сохранения файла Exp_*.mdb'))
        if exp_dir:
            e_dbf = exp_dir + u'\\Exp_' + self.db_file.split(u'/')[-1]
            if not os.path.isfile(e_dbf):
                templ = u"%s\\template.mdb" % Control.workDir
                if os.path.isfile(templ):
                    try:
                        shutil.copyfile(templ, e_dbf)
                    except:
                        print u'Something going Wrong!'
                else:
                    pass
                    #TODO: Show window, that template file is not exist
            self.e_src_lbl.setText(e_dbf)
            self.e_db_file = e_dbf

    @QtCore.pyqtSlot()
    def on_clicked_exp_a_btn(self):
        self.block_btns()
        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file:
            if self.e_src_widget.isHidden():
                self.e_src_widget.show()
            self.exp_a_thr = ExpAThread(self.e_db_file, self.convert_thr.converted_rows)
            self.btn_a_all.setHidden(False)
            self.btn_a_tree.setHidden(False)
            self.block_btns(False)
            self.exp_a_btn.hide()
        else: self.block_btns(False)

    @QtCore.pyqtSlot()
    def on_clicked_btn_a_all(self):
        self.block_btns()
        if self.try_to_connect(self.e_db_file):
            self.statusBar().showMessage(u'Производится расчет')
            self.add_visible_log(u'Запущен полный расчет экспликации А.', True)
            self.addloading(u'Пожалуйста, дождитесь окончания расчета экспликации А')
            if self.__a_thr_reinit:
                self.exp_a_thr = ExpAThread(self.e_db_file, self.convert_thr.converted_rows)
            else: self.__a_thr_reinit = True
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_a_thr, QtCore.SIGNAL(u'finished()'), self.finishtext)
            self.exp_a_thr.start()
        else:
            self.block_btns(False)
            #TODO: make sure that you have connection to exp file
            print u'Can\'t to connect to edb'

    @QtCore.pyqtSlot()
    def on_clicked_btn_a_tree(self):
        self.model = self.make_tree_model(self.exp_a_thr.exp_tree)
        self.model.setHorizontalHeaderLabels([u"Набор экспликаций А"])
        self.treeView.setModel(self.model)
        self.treeView.setHidden(False)
        self.connect(self.treeView, QtCore.SIGNAL("activated(const QModelIndex &)"),self.tree_edit_cell)

    def make_tree_model(self, data):
        model = QtGui.QStandardItemModel()
        forms22 = data.keys()
        f22_notes = get_f22_notes()
        self.tree_index_dict = {}
        for key in sorted(forms22):
            f22_item = QtGui.QStandardItem(key+u' '+f22_notes[key])
            f22_item_font = QtGui.QFont()
            f22_item_font.setBold(True)
            f22_item_font.setFamily('Cursive')
            f22_item_font.setPointSize(10)
            f22_item.setFont(f22_item_font)
            model.appendRow(f22_item)
            item_names = [i.info for i in data[key]]
            sorted_items = sorted(item_names)
            index_li = []
            for exp_item in sorted_items:
                index_li.append(item_names.index(exp_item))     #заполняет позициями элементов до сортировки, для дальнейшего определения инстанса в data[key]
                child_item = QtGui.QStandardItem(exp_item)
                child_item.setFont(QtGui.QFont('Serif', 10))
                f22_item.appendRow(child_item)
            self.tree_index_dict[key] = index_li
        return model

    def tree_edit_cell(self, qindex):
        if qindex.parent().isValid():
            data = self.exp_a_thr.exp_tree
            pressed_f22 = qindex.parent().row()
            pressed_exp = qindex.row()
            pressed_f22 = sorted(data.keys())[pressed_f22]
            indexes_before_sort = self.tree_index_dict[pressed_f22]
            exp_index = indexes_before_sort[pressed_exp]
            pressed_exp = data[pressed_f22][exp_index]
            pressed_exp.add_data()
            print pressed_f22, pressed_exp.info
            print pressed_exp.expArows

    @QtCore.pyqtSlot()
    def on_clicked_exp_b_btn(self):
        self.block_btns()
        if not self.e_db_file:
            self.get_edbf_name()
        if self.e_db_file and self.try_to_connect(self.e_db_file):
            if self.e_src_widget.isHidden():
                self.e_src_widget.show()
            self.statusBar().showMessage(u'Производится расчет')
            self.add_visible_log(u'Запущен расчет экспликации В.', True)
            self.addloading(u'Пожалуйста, дождитесь окончания расчета экспликации В')
            self.exp_b_thr = ExpBThread(self.e_db_file, self.convert_thr.converted_rows)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), self.on_finished)
            self.connect(self.exp_b_thr, QtCore.SIGNAL(u'finished()'), self.finishtext)
            self.exp_b_thr.start()
        else: self.block_btns(False)

    def finishtext(self):
        self.add_visible_log(u'Расчет завершен.\n',True)

    def add_visible_log(self, text, with_time = False):
        if with_time:
            self.textEdit.insertPlainText(time.strftime(u"\n%d.%m.%Y   %H:%M   ")+text)
        else: self.textEdit.insertPlainText(u'\n                                  '+text)

    @staticmethod
    def try_to_connect(dbfile):
        try:
            db = u'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % dbfile
            conn = pyodbc.connect(db, autocommit = True, unicode_results = True)
            dbc = conn.cursor()
            dbc.close()
            conn.close()
            return 1
        except pyodbc.Error :
            #TODO error: Не удалось соединиться с базой экспликации dbfile
            #TODO write def for error window
            return 0

if __name__ == u'__main__':
    app = QtGui.QApplication(sys.argv)
    cd = MyWindow()
    app.exec_()