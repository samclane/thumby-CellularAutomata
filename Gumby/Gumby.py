# A GUI Library for thumby
import thumby

class Widget:
    x: int
    y: int
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def show(self):
        pass

    def hide(self):
        pass

    def update(self):
        pass

    def destroy(self):
        pass

class Button(Widget):
    text: str
    callback: callable
    _is_selected: bool
    def __init__(self, x, y, text, callback):
        super().__init__(x, y)
        self.text = text
        self.callback = callback
        self._is_selected = False
        self._is_active = True

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        if value != self.is_selected:
            self.hide()
            self._is_selected = value   

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        if value == False:
            self.hide()
        self._is_active = value

    def setLabel(self, label):
        self.text = label
        thumby.display.update()

    def setCallback(self, callback):
        self.callback = callback

    def show(self):
        if not self.is_active:
            return
        if self.is_selected:
            thumby.display.drawRectangle(self.x-1, self.y-1, len(self.text)*6 + 1, 9, 0)
            thumby.display.drawFilledRectangle(self.x, self.y, len(self.text)*6, 8, 1)
            thumby.display.drawText(self.text, self.x, self.y, 0)
        else:
            thumby.display.drawText(self.text, self.x, self.y, 1)
            thumby.display.drawRectangle(self.x-1, self.y-1, len(self.text)*6 + 1, 9, 1)
        thumby.display.update()

    def hide(self):
        if self.is_selected:
            thumby.display.drawRectangle(self.x-1, self.y-1, len(self.text)*6 + 1, 9, 0)
            thumby.display.drawFilledRectangle(self.x, self.y, len(self.text)*6, 8, 0)
            thumby.display.drawText(self.text, self.x, self.y, 0)
        else:
            thumby.display.drawRectangle(self.x-1, self.y-1, len(self.text)*6 + 1, 9, 0)
            thumby.display.drawText(self.text, self.x, self.y, 0)
        thumby.display.update()


class Label(Widget):
    text: str
    def __init__(self, x, y, text):
        super().__init__(x, y)
        self.text = text

    def setLabel(self, text):
        self.text = text
        thumby.display.update()

    def show(self):
        thumby.display.drawText(self.text, self.x, self.y, 1)
        thumby.display.update()

    def hide(self):
        thumby.display.drawText(self.text, self.x, self.y, 0)
        thumby.display.update()

    def destroy(self):
        return super().destroy()

class Frame:
    width: int
    height: int
    widgets: list[Widget]
    _is_current: bool

    def __init__(self, x, y, width, height, *widgets):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.widgets = widgets

        self._is_current = False

    @property
    def is_current(self):
        return self._is_current

    @is_current.setter
    def is_current(self, value):
        if value != self.is_current:
            self.hide()
            self._is_current = value
            for w in self.widgets:
                w.is_active = value
            

    def show(self):
        if self.is_current:
            thumby.display.drawRectangle(self.x, self.y, self.width, self.height, 1)
            for w in self.widgets:
                w.show()
        else:
            pass
        thumby.display.update()

    def hide(self):
        thumby.display.drawRectangle(self.x, self.y, self.width, self.height, 0)
        for w in self.widgets:
            w.is_active = False
        thumby.display.update()

    def destroy(self):
        return super().destroy()


class LabelFrame(Frame):
    label: Label
    def __init__(self, x, y, width, height, text, *widgets):
        super().__init__(x, y, width, height, *widgets)
        self.label = Label(x+1, y+1, text)

    def setLabel(self, text: str):
        self.label = Label(self.x+1, self.y+1, text)
        thumby.display.update()

    def show(self):
        super().show()
        if self.is_current:
            self.label.show()
        thumby.display.update()

    def hide(self):
        super().hide()
        self.label.hide()
        thumby.display.update()
    
    def destroy(self):
        self.label.destroy()
        return super().destroy()


class ThumbyApp:
    widgets: list
    button_hovered: Button
    current_frame: Frame
    def __init__(self, *widgets):
        self._button_hovered = None
        self._current_frame = None
        self.widgets = list(widgets)
        # search for child frames and add their widgets
        for widget in self.widgets:
            if isinstance(widget, Frame):
                self.widgets.extend(widget.widgets)
        self.current_frame = self.frames[0]
        # activate all widgets in the current frame
        for widget in self.current_frame.widgets:
            widget.is_active = True

    @property
    def buttons(self):
        return [widget for widget in self.widgets if isinstance(widget, Button)]

    @property
    def button_hovered(self):
        return [b for b in self.buttons if b.is_selected][0] if len([b for b in self.buttons if b.is_selected]) > 0 else None
    
    @property
    def frames(self):
        return [widget for widget in self.widgets if isinstance(widget, Frame)]

    @property
    def button_hovered(self):
        return self._button_hovered

    @property
    def current_frame(self):
        return self._current_frame

    @button_hovered.setter
    def button_hovered(self, value):
        if self._button_hovered is not None:
            self._button_hovered.is_selected = False
            self._button_hovered.show()
        self._button_hovered = value
        if value is not None:
            self._button_hovered.is_selected = True
            self._button_hovered.show()

    @current_frame.setter
    def current_frame(self, value):
        if self._current_frame is not None:
            self._current_frame.is_current = False
            self._current_frame.hide()
        self._current_frame = value
        if value is not None:
            self._current_frame.is_current = True
            self._current_frame.show()

    def run(self):
        thumby.display.fill(0)
        while True:
            self.update()

    def update(self):
        self.handle_input()
        self.current_frame.show()

    def handle_input(self):
        if thumby.buttonU.justPressed():
            if self.button_hovered is None:
                self.button_hovered = self.buttons[0]
            else:
                self.button_hovered = self.buttons[self.buttons.index(self.button_hovered)-1 if self.buttons.index(self.button_hovered) > 0 else len(self.buttons)-1]
        if thumby.buttonD.justPressed():
            if self.button_hovered is None:
                self.button_hovered = self.buttons[0]
            else:
                self.button_hovered = self.buttons[(self.buttons.index(self.button_hovered)+1) % (len(self.buttons))]
        if thumby.buttonL.justPressed():
            if self.current_frame is not None:
                self.current_frame = self.frames[self.frames.index(self.current_frame)-1 if self.frames.index(self.current_frame) > 0 else len(self.frames)-1]
        if thumby.buttonR.justPressed():
            if self.current_frame is not None:
                self.current_frame = self.frames[(self.frames.index(self.current_frame)+1) % (len(self.frames))]
        if thumby.buttonA.justPressed():
            if self.button_hovered is not None:
                self.button_hovered.callback()
        if thumby.buttonB.justPressed():
            if self.button_hovered is not None:
                self.button_hovered = None

    def destroy(self):
        for widget in self.widgets:
            widget.destroy()

# test code
app = ThumbyApp(
    LabelFrame(0, 0, 72, 40, "Hello World",
        Button(10, 10, "Button 1", lambda: print("Button 1 pressed")),
        Button(10, 20, "Button 2", lambda: print("Button 2 pressed")),
    ),
    LabelFrame(0, 0, 72, 40, "Another One"),
)
app.run()