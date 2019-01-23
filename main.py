from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from os import path
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
# from kivy.uix.behaviors import FocusBehavior
# from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import load_template
from kivy.uix.recycleview.views import RecycleDataAdapter

kv = path.join(path.split(path.realpath(__file__))[0], 'project_view.kv')
print('loading kv file: ', kv)
with open(kv, encoding='utf-8') as f:
    Builder.load_string(f.read())


class ItemBasicNA(RecycleDataViewBehavior, BoxLayout):
    pass


class ItemSectionTitle(RecycleDataViewBehavior, BoxLayout):
    pass


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


class TestApp(App):
    def build(self):
        self.rv = ProjectRecycleView()
        return self.rv


if __name__ == '__main__':
    a1 = TestApp()
    a1.run()
