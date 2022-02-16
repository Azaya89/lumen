import os

from functools import partial

import panel as pn
import param

from panel.widgets import Widget as _PnWidget

from ..base import Component
from ..state import state
from ..util import resolve_module_reference

_PARAM_MAP = {
    dict : param.Dict,
    float: param.Number,
    list : param.List,
    str  : param.String
}


class Variables(param.Parameterized):

    def __init__(self, **vars):
        super().__init__()
        for p, var in vars.items():
            vtype = type(var.value)
            ptype = _PARAM_MAP.get(vtype, param.Parameter)
            self.param.add_parameter(p, ptype())
            var.param.watch(partial(self._update_value, p), 'value')
            var.param.trigger('value')
        self._vars = vars

    def _update_value(self, p, event):
        self.param.update({p: event.new})

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def from_spec(cls, spec):
        vars = {}
        for name, var_spec in spec.items():
            if not isinstance(var_spec, dict):
                var_spec = {
                    'type': 'constant',
                    'default': var_spec
                }
            vars[name] = Variable.from_spec(dict(var_spec, name=name), vars)
        return cls(**vars)

    @property
    def panel(self):
        column = pn.Column(name='Variables', sizing_mode='stretch_width')
        for key, var in self._vars.items():
            var_panel = var.panel
            if var_panel is not None:
                column.append(var_panel)
        return column


class Variable(Component):

    default = param.Parameter(doc="""
       Default value to use if no other value is defined""")

    value = param.Parameter()

    variable_type = None

    def __init__(self, **params):
        if 'value' not in params and 'default' in params:
            params['value'] = params['default']
        super().__init__(**params)

    @classmethod
    def from_spec(cls, spec, variables=None):
        if isinstance(spec, dict):
            spec = dict(spec)
            var_type = spec.pop('type')
        else:
            var_type = 'constant'
            spec = {'default': spec}
        var_type = cls._get_type(var_type)
        resolved_spec, refs = {}, {}
        for k, val in spec.items():
            if isinstance(val, str) and val.startswith('@'):
                refs[k] = val
                val = state.resolve_reference(val, variables)
            resolved_spec[k] = val
        return var_type(refs=refs, **resolved_spec)

    @property
    def panel(self):
        """
        Optionally returns a renderable component that allows
        controlling the variable.
        """
        return None


class Constant(Variable):
    """
    A constant value variable.
    """

    variable_type = 'constant'


class EnvVariable(Variable):
    """
    An environment variable.
    """

    key = param.String(default=None)

    variable_type = 'env'

    def __init__(self, **params):
        super().__init__(**params)
        key = self.key or self.name
        if key in os.environ:
            self.value = os.environ[key]


class Widget(Variable):
    """
    A Widget variable that updates when the widget value changes.
    """

    variable_type = 'widget'

    def __init__(self, **params):
        default = params.pop('default', None)
        refs = params.pop('refs', {})
        super().__init__(default=default, refs=refs)
        kind = params.pop('kind', None)
        if kind is None:
            raise ValueError("A Widget Variable type must declare the kind of widget.")
        if '.' in kind:
            widget_type = resolve_module_reference(kind, _PnWidget)
        else:
            widget_type = getattr(pn.widgets, kind)
        if 'value' not in params:
            params['default'] = default
        deserialized = {}
        for k, v in params.items():
            if k in widget_type.param:
                v = widget_type.param[k].deserialize(v)
            deserialized[k] = v
        self._widget = widget_type(**deserialized)
        self._widget.link(self, value='value', bidirectional=True)

    @property
    def panel(self):
        return self._widget


class URLQuery(Variable):
    """
    A variable obtained from the URL query parameters.
    """

    key = param.String(default=None)

    variable_type = 'url'

    def __init__(self, **params):
        super().__init__(**params)
        key = self.key or self.name
        if pn.state.location:
            pn.state.location.param.watch(self._update_value, 'search')
            self._update_value()
        if pn.state.session_args and key in pn.state.session_args:
            self.value = pn.state.session_args[key][0].decode('utf-8')

    def _update_value(self, *args):
        key = self.key or self.name
        self.value = pn.state.location.query_params.get(key, self.default)


class Cookie(Variable):
    """
    A variable obtained from the cookies in the request.
    """

    key = param.String(default=None)

    variable_type = 'cookie'

    def __init__(self, **params):
        super().__init__(**params)
        if pn.state.cookies:
            key = self.key or self.name
            self.value = pn.state.cookies.get(key, self.default)


class UserInfo(Variable):
    """
    A variable obtained from OAuth provider's user info.
    """

    key = param.String(default=None)

    variable_type = 'user'

    def __init__(self, **params):
        super().__init__(**params)
        if pn.state.user_info:
            key = self.key or self.name
            self.value = pn.state.user_info.get(key, self.default)


class Header(Variable):
    """
    A variable obtained from the request header.
    """

    key = param.String(default=None)

    variable_type = 'header'

    def __init__(self, **params):
        super().__init__(**params)
        if pn.state.headers:
            key = self.key or self.name
            self.value = pn.state.headers.get(key, self.default)
