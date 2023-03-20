from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QMenuBar, QFileDialog, QAction, QFrame, QMainWindow, QInputDialog, QDialog, QLabel, QMessageBox
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QTextBlockFormat
from PyQt5.QtCore import Qt, QByteArray
import sys, os, cProfile, codecs, binascii, math

# suppresses a GUI warning message on program start
os.environ["QT_STYLE_OVERRIDE"] = "fusion"
controlchars = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0A", "0B", "0C", "0D", "0E", "0F",
                "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1E", "1F",
                "7F"]


def syncscrolls(text0, text1, text2):
    scroll0 = text0.verticalScrollBar()
    scroll1 = text1.verticalScrollBar()
    scroll2 = text2.verticalScrollBar()
    text1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    text1.verticalScrollBar().hide()
    text1.verticalScrollBar().resize(0, 0)
    text2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    text2.verticalScrollBar().hide()
    text2.verticalScrollBar().resize(0, 0)
    scroll0.valueChanged.connect(scroll1.setValue)
    scroll0.valueChanged.connect(scroll2.setValue)
    

class HexDisplay(QWidget): 
    def __init__(self, QMenuBar, parent=None):
        super().__init__(parent)
        appfont = QFont("Monaco", 12)
        self.setWindowTitle("NEA Hex Editor")
        self.rawbytes = []
        self.rawbytes2 = []
        self.hexedit = QPlainTextEdit()
        self.hexedit.setFont(appfont)
        self.hexedit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.hexedit2 = QPlainTextEdit()
        self.hexedit2.setFont(appfont)
        self.hexedit2.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.asciiview = QPlainTextEdit()
        self.asciiview.setReadOnly(True)
        self.asciiview.setOverwriteMode(True)
        self.asciiview2 = QPlainTextEdit()
        self.asciiview2.setReadOnly(True)
        self.asciiview.setFont(appfont)
        self.asciiview2.setFont(appfont)
        self.asciiview2.setOverwriteMode(True)
        self.asciiview.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.asciiview2.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.offsetview = QPlainTextEdit()
        self.offsetview.setReadOnly(True)
        self.offsetview2 = QPlainTextEdit()
        self.offsetview2.setReadOnly(True)
        self.offsetview.setFont(appfont)
        self.offsetview2.setFont(appfont)
        self.pointer = self.offsetview.document()
        self.pointer2 = self.hexedit.document()
        self.pointer4 = self.hexedit2.document()
        self.pointer5 = self.offsetview2.document()
        self.pointer3 = self.asciiview.document()
        self.pointer6 = self.asciiview2.document()
        self.crc1 = ""
        self.crc2 = ""
        self.fileopen = False
        self.twoopen = False
        self.tableopen = False
        self.initialtitle = ""
        self.lookuptable = ""
        h_layout = QHBoxLayout()
        self.setLayout(h_layout)
        menubar = QMenuBar() 
        FileMenu = menubar.addMenu("File") 
        ViewMenu = menubar.addMenu("View")
        openfileaction = QAction("Open", self)
        offsetjumpaction = QAction("Jump to Offset", self)
        saveasfileaction = QAction("Save As", self)
        opentableaction = QAction("Open Table", self)
        openfileaction.triggered.connect(lambda: fileread(self))
        offsetjumpaction.triggered.connect(lambda: offsetjump(self))
        saveasfileaction.triggered.connect(lambda: savefileas(self))
        opentableaction.triggered.connect(lambda: tableread(self))
        FileMenu.addAction(openfileaction)
        FileMenu.addAction(saveasfileaction)
        FileMenu.addAction(opentableaction)
        ViewMenu.addAction(offsetjumpaction)
        h_layout.addWidget(menubar)
        h_layout.addWidget(self.offsetview, 1)
        h_layout.addWidget(self.hexedit, 4)
        h_layout.addWidget(self.asciiview, 1)
        syncscrolls(self.hexedit, self.offsetview, self.asciiview)
        def fileread(self):
            self.filewin = FileDisplay()
            path = self.filewin.getbrowsefile()
            self.filewin.show()
            if type(openfile(path)) == bool:
                self.filewin.hide()
                return
            newbytes = openfile(path)[0]
            crc = openfile(path)[1]
            self.filewin.close()
            if openfile == False:
                return 0
            if self.twoopen == True:
                self.dialogbox = DialogBox().openfilebutton("Do you want this file on the left or right? No for left, Yes for right.")
                if self.dialogbox == True:
                    h_layout.addWidget(self.offsetview2, 1)
                    h_layout.addWidget(self.hexedit2, 4)
                    h_layout.addWidget(self.asciiview2, 1)
                    offsetarray = screenhex(newbytes, self.hexedit2, self.offsetview2)
                    asciistuff = asciistringcreate(newbytes, self.asciiview2, self.hexedit2)
                    self.offsetview2.offsetarray = offsetarray
                    self.setWindowTitle(self.initialtitle + " ||| " + path)
                    syncscrolls(self.hexedit2, self.offsetview2, self.asciiview2)
                    self.twoopen = True
                    self.hexedit2.textChanged.connect(lambda: textinsert(self, self.hexedit2, self.asciiview2))
                    return
                elif self.dialogbox == False:
                    offsetarray = screenhex(newbytes, self.hexedit, self.offsetview)
                    asciistuff = asciistringcreate(newbytes, self.asciiview, self.hexedit)
                    self.offsetview.offsetarray = offsetarray
                    self.setWindowTitle("NEA Hex Editor - " + path)
                    self.initialtitle = ("NEA Hex Editor - " + path)
                    self.fileopen = True
                    self.crc1 = crc
                    asciistringcreate(textchange(self), self.asciiview, self.hexedit)
                    self.hexedit.textChanged.connect(lambda: textinsert(self,self.hexedit, self.asciiview))
                    return
                else:
                    return
            if self.fileopen == True and openfile != False:
                self.dialogbox = DialogBox().openfilebutton("Do you want to open this file in a side by side view? If not, then the previous file will be closed and any unsaved progress will be lost.")
                self.crc2 = crc
                if self.dialogbox == True:
                    h_layout.addWidget(self.offsetview2, 1)
                    h_layout.addWidget(self.hexedit2, 4)
                    h_layout.addWidget(self.asciiview2, 1)
                    offsetarray = screenhex(newbytes, self.hexedit2, self.offsetview2)
                    asciistuff = asciistringcreate(newbytes, self.asciiview2, self.hexedit2)
                    self.offsetview2.offsetarray = offsetarray
                    self.setWindowTitle(self.initialtitle + " ||| " + path)
                    syncscrolls(self.hexedit2, self.offsetview2, self.asciiview2)
                    self.twoopen = True
                    self.hexedit2.textChanged.connect(lambda: textinsert(self, self.hexedit2, self.asciiview2))
                    return
            offsetarray = screenhex(newbytes, self.hexedit, self.offsetview)
            asciistuff = asciistringcreate(newbytes, self.asciiview, self.hexedit)
            self.offsetview.offsetarray = offsetarray
            self.setWindowTitle("NEA Hex Editor - " + path)
            self.initialtitle = ("NEA Hex Editor - " + path)
            self.fileopen = True
            self.crc1 = crc
            asciistringcreate(textchange(self), self.asciiview, self.hexedit)
            self.hexedit.textChanged.connect(lambda: textinsert(self,self.hexedit, self.asciiview))
        def offsetjump(self):
            if self.twoopen == True:
                self.dialogbox = DialogBox().openfilebutton("Do you want to jump to the offsets on the file to the left? If no, then the file on the right will be jumped.")
                if self.dialogbox == True:
                    jumplocation = InputBox.retrievetext(self, "Input offset to jump to (hex)", "")
                    try:
                        number = self.offsetview.offsetarray.index(jumplocation[0])
                    except ValueError:
                        print("Blank or invalid offset, try again.")
                        print("Range of offsets: " + str(self.offsetview.offsetarray[0]) + " - " + self.offsetview.offsetarray[index])
                        return
                    linenumber = ((number * 2) + 39) 
                    setthingforoffset = self.pointer.findBlockByLineNumber(linenumber)
                    setthingforhex = self.pointer2.findBlockByLineNumber(linenumber)
                    setthingforascii = self.pointer3.findBlockByLineNumber(linenumber)
                    cursor = QTextCursor(setthingforoffset)
                    cursor2 = QTextCursor(setthingforhex)
                    cursor3 = QTextCursor(setthingforascii)
                    self.hexedit.setTextCursor(cursor2)
                    self.offsetview.setTextCursor(cursor)
                    self.asciiview.setTextCursor(cursor3)
                elif self.dialogbox == False:
                    jumplocation = InputBox.retrievetext(self, "Input offset to jump to (hex)", "")
                    try:
                        number = self.offsetview2.offsetarray.index(jumplocation[0])
                    except ValueError:
                        print("Blank or invalid offset, try again.")
                        print("Range of offsets: " + str(self.offsetview2.offsetarray[0]) + " - " + self.offsetview2.offsetarray[index])
                        return
                    linenumber = ((number * 2) + 39) 
                    setthingforoffset = self.pointer5.findBlockByLineNumber(linenumber)
                    setthingforhex = self.pointer4.findBlockByLineNumber(linenumber)
                    setthingforascii = self.pointer6.findBlockByLineNumber(linenumber)
                    cursor4 = QTextCursor(setthingforoffset)
                    cursor5 = QTextCursor(setthingforhex)
                    cursor6 = QTextCursor(setthingforascii)
                    self.hexedit2.setTextCursor(cursor5)
                    self.offsetview2.setTextCursor(cursor4)
                    self.asciiview2.setTextCursor(cursor6)
                else:
                    return
            elif self.twoopen == False:
                jumplocation = InputBox.retrievetext(self, "Input offset to jump to (hex)", "")
                try:
                    number = self.offsetview.offsetarray.index(jumplocation[0])
                except ValueError:
                    print("Blank or invalid offset, try again.")
                    index = len(self.offsetview.offsetarray) - 1
                    print("Range of offsets: " + str(self.offsetview.offsetarray[0]) + " - " + self.offsetview.offsetarray[index])
                    return
                linenumber = ((number * 2) + 39) 
                setthingforoffset = self.pointer.findBlockByLineNumber(linenumber)
                setthingforhex = self.pointer2.findBlockByLineNumber(linenumber)
                setthingforascii = self.pointer3.findBlockByLineNumber(linenumber)
                cursor = QTextCursor(setthingforoffset)
                cursor2 = QTextCursor(setthingforhex)
                cursor3 = QTextCursor(setthingforascii)
                self.hexedit.setTextCursor(cursor2)
                self.offsetview.setTextCursor(cursor)
                self.asciiview.setTextCursor(cursor3)
        def savefileas(self):
            if self.twoopen == True:
                dialog = DialogBox().openfilebutton("Do you want to save the file on the left? If no, then the file on the right will be saved.")
                if dialog == True:
                    text = self.hexedit.toPlainText()
                elif dialog == False:
                    text = self.hexedit2.toPlainText()
                else:
                    return
            elif self.twoopen == False:
                text = self.hexedit.toPlainText()
            array = []
            for i in range(0, len(text) - 1):
                array.append(text[i])
            if array[1] == " ":
                array[1] = array[0]
                array[0] = "0"
            for i in range(0, len(array) - 1):
                if array != " " and array[i - 1] == " " and array[i + 1] == " ":
                    array[i - 1] = "0"
            text = ""
            for i in range(0, len(array) - 1):
                text += f"{str(array[i])}"
            text = text.replace("\n", "")
            text = text.replace(" ", "")
            savebytes = bytearray.fromhex(text)
            savebytesproper = QByteArray(savebytes)
            self.filewin = FileDisplay()
            self.filewin.savefileas(savebytesproper)
            self.filewin.show()
            self.filewin.close()
            return savebytes
        def textchange(self):
            text = self.hexedit.toPlainText()
            array = []
            for i in range(0, len(text) - 1):
                array.append(text[i])
            if array[1] == " ":
                array[1] = array[0]
                array[0] = "0"
            for i in range(0, len(array) - 1):
                if array[i] != " " and array[i - 1] == " " and array[i + 1] == " ":
                    array[i - 1] = "0"
                if array[i] != " " and array[i - 1] == "\n" and array[i + 1] == " ":
                    array[i + 1] = array[i]
                    array[i] = "0"
            text = ""
            for i in range(0, len(array) - 1):
                text += f"{str(array[i])}"
            text = text.replace("\n", "")
            text = text.replace(" ", "")
            savebytes = bytearray.fromhex(text)              
            savebytesproper = QByteArray(savebytes)
            return savebytes
        def tableread(self):
            filewin = FileDisplay()
            tablepath = filewin.getbrowsefile()
            table = open(tablepath, 'r')
            self.tableopen = True
            lookuptable = []
            count = 0
            while True:
                count += 1
                temp = []
                line = ((table.readline()).strip())
                byte = line[:2]
                text = line[2:].replace("=", "")
                if not line:
                    break
                temp.append(byte)
                temp.append(text)
                if count < 1:
                    lookuptable.insert(0, temp)
                else:
                    lookuptable.insert(count, temp)
            table.close()
            tabletranslate(textchange(self), self.asciiview, lookuptable)
            self.hexedit.textChanged.connect(lambda: textinsert(self, self.hexedit, self.asciiview))
            self.lookuptable = lookuptable
        def textinsert(self, hexdisplay, textdisplay):
            x = True
            validposition = [1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 21, 22, 25, 26,
                             29, 30, 33, 34, 37, 38, 41, 42, 45, 46, 49, 50, 53,
                             54, 57, 58, 61, 62]
            cursor = hexdisplay.textCursor()
            cursor2 = textdisplay.textCursor()
            cursor2.setKeepPositionOnInsert(True)
            cursor.select(QTextCursor.WordUnderCursor)
            word = ""
            word = cursor.selectedText()
            try:
                position = 0
                blocknumber = cursor.block()
                linenumber = blocknumber.firstLineNumber() + 1
                if linenumber > 2:
                    linenumber = int(math.ceil(linenumber / 2))
                testnumber = cursor.position()
                if cursor.positionInBlock() not in validposition:
                    return
                if linenumber == 2:
                    cursornumber = (((linenumber - 1) * 17) + math.ceil(cursor.positionInBlock() / 4)) 
                if linenumber == 1:
                    cursornumber = testnumber // 4
                if linenumber > 2:
                    cursornumber = (((linenumber - 1) * 17) + math.ceil(cursor.positionInBlock() / 4)) + (1 * linenumber - 2)
                if self.tableopen == True:
                    asciibyte = tablecharactertranslate(word, self.lookuptable)
                else:
                    asciibyte = hextoascii(word)
                cursor2.setPosition(cursornumber)
                textdisplay.setTextCursor(cursor2)
                if word == "00":
                    asciibyte = "."
                if word in controlchars:
                    asciibyte = "."
                asciibyte = asciibyte.replace("\n", ".")
                cursor2.clearSelection()
                cursor2.deleteChar()
                textdisplay.insertPlainText(asciibyte)
            except ValueError:
                cursor2.setPosition(cursornumber)
                textdisplay.setTextCursor(cursor2)
                cursor2.deleteChar()
                textdisplay.insertPlainText(".")
                pass

class FileDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    def getbrowsefile(self):
        filedialog = QFileDialog.getOpenFileName()
        return filedialog[0]
    def savefileas(self, content):
        savedialog = QFileDialog()
        savedialog2 = savedialog.saveFileContent(content) 
    

class InputBox(QInputDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
    def retrievetext(self, labeltext, entrytext):
        answer = QInputDialog.getText(self, labeltext, entrytext)
        return answer

class DialogBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
    def openfilebutton(self, message):
        button = QMessageBox.question(
            self,
            "",
            message
            )
        if button == QMessageBox.Yes:
            return True
        elif button == QMessageBox.No:
            return False

def main():
    appfont = QFont("Monaco", 12)
    app = QApplication([])
    window = HexDisplay(QMenuBar)
    window.resize(1200, 800)
    window.show()
    app.exec()

def openfile(path):
    if path == "":
        return False
    file = open(path,"rb")
    testbytearray = file.read()
    buffer = (binascii.crc32(testbytearray) & 0xFFFFFFFF)
    crc = "%08X" % buffer
    file.close()
    return testbytearray, crc

def converthex(bytetoconvert):
    converted = (str(hex(bytetoconvert)[2:])).upper()
    return converted

def hextoascii(bytetoconvert):
    converted = bytes.fromhex(bytetoconvert).decode("utf-8")
    return converted

def returnoffsets(bytenumber, offsetarray):
    offset = converthex(bytenumber)
    offsetarray.append(offset)
    for i in range(0, 8 - len(offset)):
        offset = "0" + offset 
    return offset, offsetarray

def formatstring(displaystring, bytetoprint):
    displaystring = displaystring + bytetoprint + "   "
    return displaystring

def screenhex(testbytearray, textdisplay, offsetdisplay):
    count = -1
    offsetarray = []
    div = len(testbytearray) // 16
    remain = len(testbytearray) % 16
    displaystring = ""
    for i in range(0, len(testbytearray), 16):
        count += 1
        if count == div and remain != 0: 
            offsetdisplay.appendPlainText(returnoffsets(i, offsetarray)[0] + "\n")
            for f in range(0, remain):
                index = i + f
                bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                    bytetoprint = "0" + bytetoprint
                displaystring +=  f"{bytetoprint}  "
            displaystring += "\n" 
        elif count <= div:
            offsetdisplay.appendPlainText(returnoffsets(i, offsetarray)[0] + "\n")
            for y in range(0, 16):
                if remain == 0:
                    index = i + y -1
                    bytetoprint = converthex(testbytearray[index])
                else:
                    index = i + y
                    bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                    bytetoprint = "0" + bytetoprint
                displaystring += f"{bytetoprint}  "
            displaystring += "\n\n"
    displaystring.replace("     ", "")
    textdisplay.setPlainText(displaystring)
    return offsetarray

def asciistringcreate(testbytearray, textdisplay, hexdisplay):
    count = -1
    asciistring = ""
    div = len(testbytearray) // 16
    remain = len(testbytearray) % 16
    for i in range(0, len(testbytearray), 16):
        count += 1
        if count == div and remain != 0: 
            for f in range(0, remain):
                index = i + f
                bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                     bytetoprint = "0" + bytetoprint
                try:
                    asciibyte = hextoascii(bytetoprint)
                    if bytetoprint == "00":
                        asciibyte = "."
                    if bytetoprint in controlchars:
                        asciibyte = "."
                    asciibyte = asciibyte.replace("\n", ".")
                    asciistring += f"{asciibyte}"
                except UnicodeDecodeError:
                        asciistring += "."
                        continue
            asciistring += "\n" 
        elif count <= div:
            for y in range(0, 16):
                if remain == 0:
                    index = i + y - 1 
                    bytetoprint = converthex(testbytearray[index])
                else:
                    index = i + y
                    bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                    bytetoprint = "0" + bytetoprint
                try:
                    asciibyte = hextoascii(bytetoprint)
                    if bytetoprint == "00":
                        asciibyte = "."
                    if bytetoprint in controlchars:
                        asciibyte = "."
                    asciibyte = asciibyte.replace("\n", ".")
                    asciistring += f"{asciibyte}"
                except UnicodeDecodeError:
                    asciistring += "."
                    continue
            asciistring += "\n\n"
    asciistring = asciistring.replace(" ", ".")
    textdisplay.setPlainText(asciistring)
    return asciistring

def tabletranslate(testbytearray, textdisplay, lookuptable):
    count = -1
    asciistring = ""
    div = len(testbytearray) // 16
    remain = len(testbytearray) % 16
    for i in range(0, len(testbytearray), 16):
        count += 1
        if count == div and remain != 0: 
            for f in range(0, remain):
                translated = False
                index = i + f
                bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                    bytetoprint = "0" + bytetoprint
                for c in range(0, len(lookuptable) - 1):
                    if lookuptable[c][0] == bytetoprint:
                        asciibyte = lookuptable[c][1]
                        translated = True
                        asciibyte = asciibyte.replace("<line>", ".")
                        asciistring += f"{asciibyte}"
                if translated == False:
                    try:
                        asciibyte = hextoascii(bytetoprint)
                        if bytetoprint == "00":
                            asciibyte = "."
                        if bytetoprint in controlchars:
                            asciibyte = "."
                        asciibyte = asciibyte.replace("<line>", ".")
                        asciistring += f"{asciibyte}"
                    except UnicodeDecodeError:
                        asciistring += "."
                        continue
            asciistring += "\n" 
        elif count <= div:
            for y in range(0, 16):
                translated = False
                if remain == 0:
                    index = i + y - 1
                    bytetoprint = converthex(testbytearray[index])
                else:
                    index = i + y
                    bytetoprint = converthex(testbytearray[index])
                if len(bytetoprint) == 1:
                    bytetoprint = "0" + bytetoprint
                for c in range(0, len(lookuptable) - 1):
                    if lookuptable[c][0] == bytetoprint:
                        asciibyte = lookuptable[c][1]
                        translated = True
                        asciibyte = asciibyte.replace("<line>", ".")
                        asciistring += f"{asciibyte}"
                if translated == False:
                    try:
                        asciibyte = hextoascii(bytetoprint)
                        if bytetoprint == "00":
                            asciibyte = "."
                        if bytetoprint in controlchars:
                            asciibyte = "."
                        asciibyte = asciibyte.replace("<line>", ".")
                        asciistring += f"{asciibyte}"
                    except UnicodeDecodeError:
                        asciistring += "."
                        continue
            asciistring += "\n\n"
    asciistring = asciistring.replace(" ", ".")
    textdisplay.setPlainText(asciistring)
    return asciistring

def tablecharactertranslate(word, lookuptable):
    asciibyte = ""
    for i in range(0, len(lookuptable) - 1):
        if lookuptable[i][0] == word:
            asciibyte = lookuptable[i][1]
        if asciibyte == "":
            asciibyte = "."
    asciibyte = asciibyte.replace("<line>", ".")
    return asciibyte


if __name__ == "__main__":
    main()