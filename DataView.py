import urwid

class DataView:
    def __init__(self, back, parent, orwid):
        self.back = back
        self.parent = parent
        self.orwid = orwid

        self.n_ed = urwid.IntEdit(u'rows:', 0)
        self.m_ed = urwid.IntEdit(u'columns:', 0)
        self.n = 0
        self.m = 0

        self.updating = False

        self.val = []

        sb = urwid.Button(u'Set')
        nm = urwid.Columns([self.n_ed, self.m_ed, sb])

        bback = urwid.Button(u'Back')

        self.body = [nm, urwid.Pile([]), bback]
        DataView.set_dim(None, self)

        self.top = urwid.Filler(urwid.Pile(self.body), valign='top')

        urwid.connect_signal(self.n_ed, 'change', DataView.changed_dim, ['n', self])
        urwid.connect_signal(self.m_ed, 'change', DataView.changed_dim, ['m', self])
        urwid.connect_signal(sb, 'click', DataView.set_dim, self)
        urwid.connect_signal(bback, 'click', DataView.return_focus, self)

    def changed_dim(a, new_text, args):
        dim, self = args
        try:
            if dim == 'n':
                self.n = int(new_text)
            elif dim == 'm':
                self.m = int(new_text)
        except:
            pass

    def changed_val(a, new_text, args):
        pos, self = args
        try:
            if pos[0] != 0: 
                self.val[pos[0]][pos[1]] = float(new_text)
            else:
                old_text = str(self.val[pos[0]][pos[1]])
                self.val[pos[0]][pos[1]] = new_text
        except:
            pass 
        self.update()

    def set_dim(b, self):
        opt = self.body[1].options()
        self.body[1].contents.clear()
        self.val = [list(["" for i in range(self.m)])] + list([[0.0] * self.m for i in range(self.n)])
        for i in range(self.n+1):
            txt = str(i)
            if i == 0:
                txt = 'N'
            a = [urwid.Text(txt)]
            
            for j in range(self.m):
                if i == 0:
                    a += [urwid.Edit('', '')]
                else:
                    a += [urwid.Edit('', '0.0')]
                urwid.connect_signal(a[-1], 'change', DataView.changed_val, [(i,j), self])
            
            wid = urwid.Columns(a)
            self.body[1].contents.append((wid, opt))
        a = [urwid.Text("Mean")] + [urwid.Text(u'0.0') for z in range(self.m)]
        wid = urwid.Columns(a)
        self.body[1].contents.append((wid, opt))
    
    def return_focus(button, self):
        self.back(button, [self.parent, self.orwid])

    def update(self):
        if self.updating:
            return
        self.updating = True
        deltacols = []
        means = []
        headers = {}

        for i in range(self.m):
            mean = sum([x[i] for x in self.val[1:]])/self.n
            meanrow = self.body[1].contents[-1][0]
            meanrow.contents[i+1][0].set_text('%.4f'%mean)
            means += [mean]

            headrow = self.body[1].contents[0][0]
            header = headrow.contents[i+1][0].edit_text
            if len(header) > 1 and header[0] == 'd':
                deltacols += [(header[1:], i)]
            headers[header] = i
        

        for name, i in deltacols:
            needed = headers.get(name, [])
            mean = means[needed]
            error = [self.val[x+1][needed]-mean for x in range(self.n)]
            residual = (sum([(self.val[x+1][needed]-mean)**2 for x in range(self.n)])/(self.n*(self.n-1)))**0.5

            for j in range(self.n):
                row = self.body[1].contents[j+1][0]
                row.contents[i+1][0].set_edit_text('%.4f'%error[j])

            row = self.body[1].contents[-1][0]
            row.contents[i+1][0].set_text('%.4f'%residual)

        self.updating = False
