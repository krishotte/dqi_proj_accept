from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from os import path, listdir
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
import load_template
from kivy.uix.recycleview.views import RecycleDataAdapter
from kivy.uix.relativelayout import RelativeLayout
from m_file import Ini2
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import copy

files = ['project_view.kv', 'item_view.kv', 'manage_view.kv']
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
    """
    standard editable item class
    """
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
            a1.main_container.display_view_item(self.index)
        # TODO: propagate touch


class ItemSectionTitle(RecycleDataViewBehavior, BoxLayout):
    """
    standard section title item class
    """
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
        '''
        widget for item editing
        :param data_item: RecycleView.data[index] dictionary
        :param index: index to generate view
        '''
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
            else:
                each.state = 'normal'

        self.data_index = index

    def confirm(self):
        '''
        collects item data and calls RecycleView data update
        :return:
        '''
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
        # print('output_dict: ', _output_dict)
        a1.main_container.project_container.project_recycle_view.update_data(self.data_index, _output_dict)
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
        # overrides default DataAdapter used by RecycleView
        self.view_adapter = MyRDA()
        self.template_data1 = load_template.get_data()
        # need to do a deepcopy, otherwise self.template_data1 will be overwritten
        self.data = copy.deepcopy(self.template_data1)

    def update_data(self, data_index, update_data):
        '''
        updates data and refreshes view
        :param data_index: index to update
        :param update_data: dictionary to update self.data[index]
        :return:
        '''
        print('project recycle view, updating data...')
        _data = self.data
        self.data[data_index].update(update_data)
        print('updated index: ', data_index, ' data_item: ', self.data[data_index])
        self.refresh_from_data()

    def _update_all_data(self, data):
        print('project recycle view, updating all data...')
        self.data = copy.deepcopy(data)
        self.refresh_from_data()

    def reset_all_data(self):
        print('resetting all data...')
        self.data = copy.deepcopy(self.template_data1)  # load_template.get_data()  # TODO: self.template_data overwritten
        # not needed: self.refresh_from_data()
        for i in range(8):
            print('   index: ', i, 'status: ', self.data[i]['status'], ' template: ', self.template_data1[i]['status'])


class ProjectContainer(BoxLayout):
    '''
    container holding project labels, controls and ProjectRecycleView
    '''
    proj_name = StringProperty()

    def __init__(self, data_dir):
        super().__init__()
        self.project_recycle_view = ProjectRecycleView()
        self.add_widget(self.project_recycle_view)
        self.proj_name = 'Sample project'
        self.data_dir = data_dir
        self.ini = Ini2()
        self.load_newest_file()

    def save(self):
        """
        saves current RecycleView.data into file
        uses 'self.proj_name'_xxxx.json name
        xxxx next available number
        :return:
        """
        print('saving project...')
        self._check_saved_files()
        suffix = str(len(self.matched_saves)).zfill(4)
        filename = self.proj_name + '_' + suffix + '.json'
        print('filename used: ', filename)
        self.ini.write(path.join(self.data_dir, filename), self.project_recycle_view.data)

    def _check_saved_files(self):
        """
        gets list of saved project files self.matched_saves
        :return:
        """
        self.existing_files = listdir(self.data_dir)
        # print('existing files: ', self.existing_files)
        matched_saves = []
        filename_prefixes = []
        for item in self.existing_files:
            filename_prefixes.append(item.split('_')[0])
            if self.proj_name + '_' in item:
                # print('string found')
                matched_saves.append(item)
        projects = set(filename_prefixes)
        print('projects: ', projects)
        print('found files: ', matched_saves)
        self.matched_saves = matched_saves
        self.saved_projects = projects

    def load_newest_file(self):
        self._check_saved_files()
        self.last_file = self.matched_saves[-1]
        print('loading file: ', self.last_file)
        data = self.ini.read(path.join(self.data_dir, self.last_file))
        # print('loaded data: ', data)
        self.project_recycle_view.data = data

    def set_proj_name(self, project_name):
        self.proj_name = project_name

    def close(self):
        a1.main_container.display_project_manager()

    def reset_project_view(self):
        self.project_recycle_view.reset_all_data()


class ManageRecycleView(RecycleView):
    def __init__(self, data_dir, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir
        self.get_saved_projects()
        self.data = self.saved_projects
        self.selected = None

    def get_saved_projects(self):
        self.existing_files = listdir(self.data_dir)
        filename_prefixes = []
        for item in self.existing_files:
            filename_prefixes.append(item.split('_')[0])
        projects = set(filename_prefixes)
        print('projects: ', projects)
        data = []
        for each in projects:
            data.append({'text': each})
        self.saved_projects = data

    def add_project(self, new_name):
        self.data.append({'text': new_name})
        print('project added')
        # self.refresh_from_data()


class ProjectManager(BoxLayout):
    """
    container holding project management view
    """
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.manage_recycle_view = ManageRecycleView(data_dir)
        self.add_widget(self.manage_recycle_view)
        self.popup = CreateProjectPopup()

    def load(self):
        print('selected index', self.manage_recycle_view.selected)
        self.selected_project = self.manage_recycle_view.data[self.manage_recycle_view.selected]
        print('selected project: ', self.selected_project)
        a1.main_container.project_container.set_proj_name(self.selected_project['text'])
        a1.main_container.project_container.load_newest_file()
        a1.main_container.open_project_recycle_view()

    def open_popup(self):
        self.popup.open()

    def create_project(self, new_name):
        # print('creating new project', new_name)
        existing_projects = []
        for each in self.manage_recycle_view.saved_projects:
            existing_projects.append(each['text'])
        if new_name not in existing_projects and new_name != '':
            print('project created')
            a1.main_container.project_manager.manage_recycle_view.add_project(new_name)
            a1.main_container.project_container.set_proj_name(new_name)
            # TODO: heisenbug reset_project_view() overwrites self.template_data, do not know where
            a1.main_container.project_container.reset_project_view()
            a1.main_container.open_project_recycle_view()
            return True
        else:
            print('project not created')
            return False


class CreateProjectPopup(Popup):
    new_project_name = ObjectProperty()

    def _enter(self):
        print('popup OK pressed')
        print('new project name: ', self.new_project_name.text)
        response = a1.main_container.project_manager.create_project(self.new_project_name.text)
        print('creation response: ', response)
        if response:
            self.dismiss()

    def _cancel(self):
        print('popup Cancel pressed')
        self.dismiss()


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    def apply_selection(self, index, view, is_selected):
        print('selected nodes: ', self.selected_nodes)
        return super().apply_selection(index, view, is_selected)


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        print('refresh view attrs: ', index)
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            print('touch down 1, ', self.index)
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            print('touch down 2, ', self.index)
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            a1.main_container.project_manager.manage_recycle_view.selected = index
        else:
            print("selection removed for {0}".format(rv.data[index]))
            a1.main_container.project_manager.manage_recycle_view.selected = None


class MainContainer(RelativeLayout):
    def __init__(self, data_dir):
        '''
        container widget holding all subwidgets
        '''
        super().__init__()
        self.project_container = ProjectContainer(data_dir)
        self.project_manager = ProjectManager(data_dir)
        # self.add_widget(self.project_container)
        self.add_widget(self.project_manager)

    def display_view_item(self, index):
        self.remove_widget(self.project_container)
        self._view_item = ViewItem(a1.main_container.project_container.project_recycle_view.data[index], index)
        self.add_widget(self._view_item)

    def display_project_recycle_view(self):
        self.remove_widget(self._view_item)
        self.add_widget(self.project_container)

    def open_project_recycle_view(self):
        self.remove_widget(self.project_manager)
        self.add_widget(self.project_container)
        # self.project_container.project_recycle_view.refresh_from_data()

    def display_project_manager(self):
        self.remove_widget(self.project_container)
        self.add_widget(self.project_manager)


class Dqi_Proj_Accept(App):
    def build(self):
        self.main_container = MainContainer(self.user_data_dir)
        return self.main_container


if __name__ == '__main__':
    a1 = Dqi_Proj_Accept()
    a1.run()
