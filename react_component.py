import sublime
import sublime_plugin
import os
from collections import OrderedDict


COMPONENT_TYPES = OrderedDict()
COMPONENT_TYPES['Functional Component with Return Statement'] = \
    """import React from 'react';
import PropTypes from 'prop-types';
%(style_import)s

const %(name)s = (props) => {
  return (
    <div></div>
  );
};

%(name)s.propTypes = {};

%(name)s.defaultProps = {};

export default %(name)s;
"""
COMPONENT_TYPES['Functional Component with Implicit Return'] = \
    """import React from 'react';
import PropTypes from 'prop-types';
%(style_import)s

const %(name)s = (props) => (
  <div></div>
);

%(name)s.propTypes = {};

%(name)s.defaultProps = {};

export default %(name)s;

"""


STYLE_TYPES = OrderedDict()
STYLE_TYPES['SCSS'] = '.scss'
STYLE_TYPES['CSS'] = '.css'
STYLE_TYPES['SASS'] = '.sass'
STYLE_TYPES['LESS'] = '.less'

CSS_MODULES_TYPES = OrderedDict()
CSS_MODULES_TYPES['Use CSS Modules (.module.) for stylesheet'] = '.module'
CSS_MODULES_TYPES['No CSS Modules'] = ''

TEST_FILE = """import React from 'react';
import { shallow } from 'enzyme';
import %(name)s from './%(name)s';

describe('<%(name)s />', () => {
  let component;

  beforeEach(() => {
    component = shallow(<%(name)s />);
  });

  test('It should mount', () => {
    expect(component.length).toBe(1);
  });
});
"""


class ReactCreateComponentCommand(sublime_plugin.WindowCommand):
    """
    Creates a React Component (new folder with an empty styles.css
    and a prefilled index.js file inside it)
    """
    def is_enabled(self, paths):
        paths = [] if paths is None else paths
        return self._is_valid_args(paths)

    def is_visible(self, paths):
        paths = [] if paths is None else paths
        return self._is_valid_args(paths)

    def run(self, paths):
        """Base run function, which gets paths and shows component type
        selector.

        :param paths: paths list to folder where component to be placed
        :type paths: list
        """
        paths = [] if paths is None else paths
        self.window.run_command('hide_panel')
        if self._is_valid_args(paths):
            self._path = paths[0]
            self.window.show_quick_panel(
                list(COMPONENT_TYPES.keys()),
                self._component_type_on_done)

    def _component_type_on_done(self, index):
        """Callback for the component type Quick Panel selector.

        :param index: index of the component type panel selection
        :type index: int
        """
        self._content = self._safe_get_selection(COMPONENT_TYPES, index)
        self.window.show_quick_panel(
            list(STYLE_TYPES.keys()),
            self._style_type_on_done)

    def _style_type_on_done(self, index):
        """Callback for the style type Quick Panel selector.

        :param index: index of the style type panel selection
        :type index: int
        """
        self._style = self._safe_get_selection(STYLE_TYPES, index)
        self.window.show_quick_panel(
            list(CSS_MODULES_TYPES.keys()),
            self._css_modules_type_on_done)

    def _css_modules_type_on_done(self, index):
        """Callback for the css-modules Quick Panel selector.

        :param index: index of the css-modules panel selection
        :type index: int
        """
        self._css_modules = self._safe_get_selection(CSS_MODULES_TYPES, index)
        self.window.show_input_panel(
            'Component Name:', '',
            self._component_name_on_done,
            None, None)

    def _component_name_on_done(self, name):
        """Callback for the component name Input Panel value.

        :param name: name of the component to be created
        :type name: string
        """
        if not name or ' ' in name:
            sublime.error_message(
                'Unable to create component: invalid name.')
            return

        new_dir = os.path.join(self._path, name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            index_name = '%s.js' % name
            stylesheet_name = '%s%s%s' % (name, self._css_modules, self._style)
            style_import = 'import \'./%s\';' % stylesheet_name
            test_name = '%s.test.js' % name
            if self._css_modules:
                style_import = 'import styles from \'./%s\';' % stylesheet_name
            open(os.path.join(new_dir, stylesheet_name), 'w').close()
            js_file = open(os.path.join(new_dir, index_name), 'w')
            js_file.write(
                self._content % {
                    'name': name,
                    'style_import': style_import,
                })
            js_file.close()
            test_file = open(os.path.join(new_dir, test_name), 'w')
            test_file.write(
                TEST_FILE % {
                    'name': name,
                })
            test_file.close()
        else:
            sublime.error_message(
                'Unable to create component: "%s" already exists.' % name)

    def _safe_get_selection(self, od, index):
        """Checks if the selection from a Quick Panel is valid and
        returns the value.

        :param od: the ordered dictionary to perform lookup on
        :type od: OrderedDict
        :param index: index of the panel selection
        :type index: int
        :returns: the value associated with the key index in `od`
        :rtype: {string}
        :raises: Exception
        """
        if index == -1:
            message = 'Unable to create component: no option selected.'
            sublime.error_message(message)
            raise Exception(message)

        try:
            key = list(od.keys())[index]
            data = od[key]
            return data
        except IndexError:
            message = 'Unable to create component: invalid selection.'
            sublime.error_message(message)
            raise Exception(message)

    def _is_valid_args(self, paths):
        if len(paths) >= 1:
            return os.path.isdir(paths[0])
        else:
            False
