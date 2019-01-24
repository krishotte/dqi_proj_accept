from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from os import path
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
# from kivy.uix.behaviors import FocusBehavior
# from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import load_template
from kivy.uix.recycleview.views import RecycleDataAdapter
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color

files = ['project_view.kv', 'item_view.kv']
for file in files:
    kv = path.join(path.split(path.realpath(__file__))[0], file)
    print('loading kv file: ', kv)
    with open(kv, encoding='utf-8') as f:
        Builder.load_string(f.read())

paleblue = [0.102, 0.282, 0.412, 1]
darkred = [118/255, 22/255, 22/255, 1]
darkgreen = [ 32/255, 64/255, 16/255, 1]
black = [0, 0, 0, 1]
color_picker = {'OK': darkgreen, 'NOK': darkred, 'N/A': black, 'None': black}
print('color definition: ', color_picker)


class ItemBasicNA(RecycleDataViewBehavior, BoxLayout):
    status_color = ListProperty()
    name1 = StringProperty()
    id1 = StringProperty()
    status = StringProperty()
    note = StringProperty()

    def __init__(self):
        # self.status_color = [0, 0, 0, 1]
        super().__init__()

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(ItemBasicNA, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print('touched item, index: ', self.index)
            a1.main_container.display_item_view(self.index)
        # TODO: propagate touch


class ItemSectionTitle(RecycleDataViewBehavior, BoxLayout):
    background_color = ListProperty()
    name1 = StringProperty()
    id1 = StringProperty()

    def __init__(self):
        self.background_color = paleblue
        super().__init__()


class ViewItem(BoxLayout):
    notes = ObjectProperty()
    tbtn = ObjectProperty()
    id1 = StringProperty()
    name1 = StringProperty()

    def __init__(self, data_item, index):
        super().__init__()
        self.id1 = data_item['id1']
        self.name1 = data_item['name1']
        try:
            self.notes.text = data_item['notes']
        except KeyError:
            self.notes.text = ''
        try:
            self.status = data_item['status']
        except KeyError:
            self.status = 'None'

        _toggle_buttons = self.tbtn.get_widgets('_group')
        for each in _toggle_buttons:
            if each.text == self.status:
                each.state = 'down'

        self.data_index = index

    def confirm(self):
        print('Confirm button pressed')
        print('notes: ', self.notes.text)
        _toggle_buttons = self.tbtn.get_widgets('_group')
        _pressed_button = 'None'

        for each in _toggle_buttons:
            # print('tbtn state: ', each.state)
            if each.state == 'down':
                _pressed_button = each.text
        print('item status: ', _pressed_button)

        if self.notes.text == '':
            _note = '--'
        else:
            _note = 'note'

        _output_dict = dict(status=_pressed_button, notes=self.notes.text, status_color=color_picker[_pressed_button],
                            note=_note)
        print('output_dict: ', _output_dict)
        a1.main_container.project_recycle_view.update_data(self.data_index, _output_dict)
        a1.main_container.display_project_recycle_view()

    def cancel(self):
        print('Cancel button pressed')
        a1.main_container.display_project_recycle_view()


class MyRDA(RecycleDataAdapter):
    '''
    uses viewclass defined in RecycleView.data[index]['viewclass']
    for each item separately instead default viewclass defined
    in RecycleView;
    viewclasses need to be available in globals()
    '''
    def create_view(self, index, data_item, viewclass):
        vcls = globals()[data_item['viewclass']]
        print('my viewclass: ', vcls)
        if vcls is None:
            return

        view = vcls()
        self.refresh_view_attrs(index, data_item, view)
        return view

    def set_visible_views(self, indices, data, viewclasses):
        visible_views = {}
        previous_views = self.views
        ret_new = []
        ret_remain = []
        get_view = self.get_view

        # iterate though the visible view
        # add them into the container if not already done
        for index in indices:
            vcls = globals()[data[index]['viewclass']]
            print('my viewclass _: ', vcls)
        
            view = previous_views.pop(index, None)
            if view is not None:  # was current view
                visible_views[index] = view
                ret_remain.append((index, view))
            else:
                view = get_view(index, data[index], vcls)
                if view is None:
                    continue
                visible_views[index] = view
                ret_new.append((index, view))

        old_views = previous_views.items()
        self.make_views_dirty()
        self.views = visible_views
        return ret_new, ret_remain, old_views


class ProjectRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        'overrides default DataAdapter used by RecycleView'
        self.view_adapter = MyRDA()
        '''
        self.data = {}
        for i in range(60):
            self.data.append({
                'text1': str(i),
            })
        '''
        self.data = load_template.get_data()

    def update_data(self, data_index, update_data):
        print('project recycle view, updating data...')
        _data = self.data
        # self.data[data_index].update(update_data)
        _data[data_index].update(update_data)
        self.data = _data
        print('updated index: ', data_index, ' data_item: ', self.data[data_index])
        self.refresh_from_data()


class MainContainer(RelativeLayout):
    def __init__(self):
        super().__init__()
        self.project_recycle_view = ProjectRecycleView()
        # self.item_view = ViewItem()
        self.add_widget(self.project_recycle_view)

    def display_item_view(self, index):
        self.remove_widget(self.project_recycle_view)
        self._view_item = ViewItem(a1.main_container.project_recycle_view.data[index], index)
        self.add_widget(self._view_item)

    def display_project_recycle_view(self):
        self.remove_widget(self._view_item)
        self.add_widget(self.project_recycle_view)


class TestApp(App):
    def build(self):
        self.main_container = MainContainer()
        return self.main_container


if __name__ == '__main__':
    a1 = TestApp()
    a1.run()
