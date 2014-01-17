import urwid
from sympy import *

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
        exit = urwid.Button(u'Back')
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
        self.back(button, [self.parent, self.orwid])


