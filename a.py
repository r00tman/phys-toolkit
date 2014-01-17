import urwid
from sympy import *

class DataView:
    def __init__(self, back, parent, orwid):
        pass

class ErrorView:
    def __init__(self, back, parent, orwid):
        self.back = back
        self.parent = parent
        self.orwid = orwid

        self.e_expr = None

        self.expr = urwid.Edit(u'Enter expression:\n')
        self.expr_ans = urwid.Text(u'')
        ok = urwid.Button(u'Set expression')
        okd = urwid.Button(u'Set error')
        exit = urwid.Button(u'Exit')
        evalf = urwid.Button(u'Eval')
        div = urwid.Divider()
        pile = urwid.Pile([self.expr, div, self.expr_ans, ok, okd, evalf, exit])
        self.top = urwid.Filler(pile, valign='top')
        urwid.connect_signal(ok, 'click', ErrorView.print_out, [self, False])
        urwid.connect_signal(okd, 'click', ErrorView.print_out, [self, True])
        urwid.connect_signal(exit, 'click', ErrorView.quit, self)
        urwid.connect_signal(evalf, 'click', ErrorView.evalf_add, self)
   
    def gen_units():
        r = {}
        exec("from sympy.physics.units import *", r)
        return r

    def gen_expr(self, der=False):
        s = self.expr.edit_text
        expr = sympify(s)
        syms = expr.atoms(Symbol)
        symdict = {x.name:Symbol(x.name, positive=True, real=True) for x in syms}
        expr = sympify(s, locals=symdict)
        syms = expr.atoms(Symbol)
        symdiffdict = {'d'+x.name:Symbol('d'+x.name, positive=True, real=True) for x in syms}
        a = Integer(0)
        for name, symbol in symdict.items():
            a += symdiffdict['d'+name]**2*diff(expr, symbol)**2
        if der:
            a = simplify(sqrt(a))
        else:
            a = expr
        return a

    def print_out(button, args):
        self, der = args
        a = self.gen_expr(der)
        self.e_expr = a
        self.expr_ans.set_text(pretty(a))#, use_unicode=False))

    def evalf(self, expr):
        syms = expr.atoms(Symbol)
        body = [urwid.Text(u"Evaluating\n%s"%pretty(expr)), urwid.Divider()]
        for s in syms:
            ed = urwid.Edit(s.name+u'=', u'')
            body.append(urwid.AttrMap(ed, None, focus_map='reversed'))
        tresult = urwid.Text(u'')
        beval = urwid.Button(u'Eval')
        bback = urwid.Button(u'Back')
        urwid.connect_signal(beval, 'click', ErrorView.calc, [self, body])
        urwid.connect_signal(bback, 'click', ErrorView.return_focus, self)
        body.append(tresult)
        body.append(beval)
        body.append(bback)

        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def evalf_add(button, self):
        if self.e_expr == None:
            self.e_expr = self.gen_expr()
        self.parent.main.original_widget = self.evalf(self.e_expr)

    def calc(button, args):
        self, body = args
        syms = {x.name:x for x in self.e_expr.atoms(Symbol)}
        subs = {}
        unitlocal = ErrorView.gen_units()
        for i in range(2, len(body)-3):
            s = body[i].original_widget
            subs[syms[s.caption[:-1]]] = sympify(s.edit_text, locals=unitlocal)
        body[-3].set_text(pretty(self.e_expr.subs(subs).evalf())) #sorry

    def return_focus(button, self):
        self.parent.main.original_widget = self.top

    def quit(button, self):
        MainMenu.exit_program(button, [self.parent, self.orwid])

class MainMenu:
    choices = [u"Data", u"Error", u"Exit"]
    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', MainMenu.item_chosen, [c, self])
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(button, args):
        choice, self= args
        if choice == MainMenu.choices[1]:
            orwid = self.main.original_widget
            ev = ErrorView(MainMenu.exit_program, self,  orwid) 
            self.main.original_widget = ev.top
        elif choice == MainMenu.choices[2]:
            raise urwid.ExitMainLoop()
    
    def exit_program(button, args):
        self, original_widget = args
        #raise urwid.ExitMainLoop()
        self.main.original_widget = original_widget
    
    def __init__(self):
        self.main = urwid.Padding(self.menu(u'Action', MainMenu.choices), left=2,right=2)
        self.top = urwid.Overlay(self.main, urwid.SolidFill(u'\m{MEDIUM SHADE}'), align='center', width=('relative', 80), valign='middle', height=('relative', 80), min_width=20, min_height=9)

mm = MainMenu()
urwid.MainLoop(mm.top, palette=[('reserved', 'standout', '')]).run()
