"""
Provide a common way to import Qt classes used by pytest-qt in a unique manner,
abstracting API differences between PyQt4, PyQt5 and PySide.

.. note:: This module is not part of pytest-qt public API, hence its interface
may change between releases and users should not rely on it.

Based on from https://github.com/epage/PythonUtils.
"""

from __future__ import with_statement
from __future__ import division
from collections import namedtuple
import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

VersionTuple = namedtuple('VersionTuple', 'qt_api, qt_api_version, runtime, compiled')

if not on_rtd:  # pragma: no cover

    class _QtApi:

        @property
        def USING_PYSIDE(self):
            # backward compatibility
            return self.pytest_qt_api == 'pyside'

        def set_qt_api(self, qt_api):

            def _try_import(name):
                try:
                    __import__(name)
                    return True
                except ImportError:
                    return False

            def _guess_qt_api():
                if _try_import('PySide'):
                    return 'pyside'
                elif _try_import('PyQt4'):
                    return 'pyqt4'
                elif _try_import('PyQt5'):
                    return 'pyqt5'
                else:
                    msg = 'pytest-qt requires either PySide, PyQt4 or PyQt5 to be installed'
                    raise RuntimeError(msg)

            # backward compatibility support: PYTEST_QT_FORCE_PYQT
            if os.environ.get('PYTEST_QT_FORCE_PYQT', 'false') == 'true':
                qt_api = 'pyqt4'
            elif not qt_api:
                qt_api = os.environ.get('PYTEST_QT_API')
                if qt_api is not None:
                    qt_api = qt_api.lower()
                    if qt_api not in ('pyside', 'pyqt4', 'pyqt4v2', 'pyqt5'):
                        msg = 'Invalid value for $PYTEST_QT_API: %s'
                        raise RuntimeError(msg % qt_api)
                else:
                    qt_api = _guess_qt_api()

            self.pytest_qt_api = qt_api

            def _import_module(module_name):
                m = __import__(_root_module, globals(), locals(), [module_name], 0)
                return getattr(m, module_name)

            _root_modules = {
                'pyside': 'PySide',
                'pyqt4': 'PyQt4',
                'pyqt4v2': 'PyQt4',
                'pyqt5': 'PyQt5',
            }
            _root_module = _root_modules[qt_api]

            if qt_api == 'pyqt4v2':
                # the v2 api in PyQt4
                # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
                import sip
                sip.setapi("QDate", 2)
                sip.setapi("QDateTime", 2)
                sip.setapi("QString", 2)
                sip.setapi("QTextStream", 2)
                sip.setapi("QTime", 2)
                sip.setapi("QUrl", 2)
                sip.setapi("QVariant", 2)

            self.QtCore = QtCore = _import_module('QtCore')
            self.QtGui = QtGui = _import_module('QtGui')
            self.QtTest = _import_module('QtTest')
            self.Qt = QtCore.Qt
            self.QEvent = QtCore.QEvent

            self.qDebug = QtCore.qDebug
            self.qWarning = QtCore.qWarning
            self.qCritical = QtCore.qCritical
            self.qFatal = QtCore.qFatal
            self.QtDebugMsg = QtCore.QtDebugMsg
            self.QtWarningMsg = QtCore.QtWarningMsg
            self.QtCriticalMsg = QtCore.QtCriticalMsg
            self.QtFatalMsg = QtCore.QtFatalMsg

            # Qt4 and Qt5 have different functions to install a message handler;
            # the plugin will try to use the one that is not None
            self.qInstallMsgHandler = None
            self.qInstallMessageHandler = None

            if qt_api == 'pyside':
                self.Signal = QtCore.Signal
                self.Slot = QtCore.Slot
                self.Property = QtCore.Property
                self.QApplication = QtGui.QApplication
                self.QWidget = QtGui.QWidget
                self.qInstallMsgHandler = QtCore.qInstallMsgHandler

            elif qt_api in ('pyqt4', 'pyqt4v2', 'pyqt5'):
                self.Signal = QtCore.pyqtSignal
                self.Slot = QtCore.pyqtSlot
                self.Property = QtCore.pyqtProperty

                if qt_api == 'pyqt5':
                    _QtWidgets = _import_module('QtWidgets')
                    self.QApplication = _QtWidgets.QApplication
                    self.QWidget = _QtWidgets.QWidget
                    self.qInstallMessageHandler = QtCore.qInstallMessageHandler
                else:
                    self.QApplication = QtGui.QApplication
                    self.QWidget = QtGui.QWidget
                    self.qInstallMsgHandler = QtCore.qInstallMsgHandler

        def get_versions(self):
            if self.pytest_qt_api == 'pyside':
                import PySide
                return VersionTuple('PySide', PySide.__version__, self.QtCore.qVersion(),
                                    self.QtCore.__version__)
            else:
                qt_api_name = 'PyQt5' if self.pytest_qt_api == 'pyqt5' else 'PyQt4'
                return VersionTuple(qt_api_name, self.QtCore.PYQT_VERSION_STR,
                                    self.QtCore.qVersion(), self.QtCore.QT_VERSION_STR)

    qt_api = _QtApi()

else:  # pragma: no cover
    USING_PYSIDE = True

    # mock Qt when we are generating documentation at readthedocs.org
    class Mock(object):
        def __init__(self, *args, **kwargs):
            pass
    
        def __call__(self, *args, **kwargs):
            return Mock()
    
        @classmethod
        def __getattr__(cls, name):
            if name in ('__file__', '__path__'):
                return '/dev/null'
            elif name in ('__name__', '__qualname__'):
                return name
            elif name == '__annotations__':
                return {}
            else:
                return Mock()
    
    QtGui = Mock()
    QtCore = Mock()
    QtTest = Mock()
    Qt = Mock()
    QEvent = Mock()
    QApplication = Mock()
    QWidget = Mock()
    qInstallMsgHandler = Mock()
    qInstallMessageHandler = Mock()
    qDebug = Mock()
    qWarning = Mock()
    qCritical = Mock()
    qFatal = Mock()
    QtDebugMsg = Mock()
    QtWarningMsg = Mock()
    QtCriticalMsg = Mock()
    QtFatalMsg = Mock()
    QT_API = '<none>'
