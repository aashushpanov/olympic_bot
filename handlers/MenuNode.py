from aiogram.utils.callback_data import CallbackData

move = CallbackData('id', 'action', 'node', 'data')


class MenuNode:
    def __init__(self, text: str = None, callback=None, parent=None, id=None):
        self._id = id or 'admin'
        self._childs = []
        self._parent = parent
        self._text = text
        self._callback = callback

    @property
    def callback(self):
        return self._callback

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id if self._id else 0

    @property
    def text(self):
        return self._text

    async def childs_data(self, **kwargs):
        for child in self._childs:
            yield child.id, child.text, child.callback

    def child(self, child_id: str = None, text: str = None):
        if child_id is not None:
            for child in self._childs:
                if child.id == child_id:
                    return child
        elif text:
            for child in self._childs:
                if child.text == text:
                    return child
        raise KeyError

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        return result

    def all_childs(self, result=None):
        if result is None:
            result = {}
        result.update(self.childs())
        for child in self._childs:
            result = child.all_childs(result)
        return result

    def set_child(self, child):
        child._id = self._id + '_' + str(len(self._childs))
        if child.callback is None:
            child._callback = move.new(action='d', node=child.id, data='')
        self._childs.append(child)
        child._parent = self

    def set_childs(self, childs):
        for child in childs:
            self.set_child(child)

    def __next__(self, child_id):
        return self._childs[child_id]

    def prev(self):
        return self._parent


class NodeGenerator(MenuNode):
    def __init__(self, text, func, reg_nodes=[], parent=None, callback=None):
        self._id = 'gen'
        self._callback = callback
        self._text = text
        self._childs = []
        self._func = func
        self._reg_nodes = reg_nodes
        self._parent = parent
        self._sub_childs = []
        self._blind_node = None

    @property
    def func(self):
        return self._func

    async def childs_data(self, **kwargs):
        for child in self._reg_nodes:
            yield child.id, child.text, child.callback
        async for child in self.func(self, **kwargs):
            yield child.id, child.text, child.callback

    def append(self, node):
        self._reg_nodes.append(node)

    def add_blind_node(self, node_id):
        node_id = self.id + '_' + node_id
        self._blind_node = BlindNode(node_id, self)
        self._blind_node._parent = self

    def set_sub_child(self, sub_child):
        sub_child._id = self.blind_node.id + '_' + str(len(self.blind_node._childs))
        self._blind_node._childs.append(sub_child)
        sub_child._parent = self.blind_node

    def set_sub_childs(self, sub_childs):
        for sub_child in sub_childs:
            self.set_sub_child(sub_child)

    @property
    def blind_node(self):
        return self._blind_node

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        result.update({self.blind_node.id: self.blind_node})
        result.update(self.blind_node.childs())
        return result


class BlindNode(MenuNode):
    def __init__(self, node_id, parent):
        self._id = node_id
        self._childs = []
        self._parent = parent
        self._callback = None

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        return result

    @property
    def id(self):
        return self._id
