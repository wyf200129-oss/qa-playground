from base_page.basepage import BasePage


class PersonPage(BasePage):
    """经手人管理页面对象，封装列表查询、新增/编辑弹窗及行内操作。"""

    PATH = '/system/person'

    # 列表页 - 查询区
    search_name = ('xpath', '//input[@placeholder="请输入姓名查询"]')
    search_type = ('css selector', '.table-page-search-wrapper .ant-select-selection')
    search_btn = ('xpath', '//span[contains(text(),"查询")]/..')
    reset_btn = ('xpath', '//span[contains(text(),"重置")]/..')

    # 列表页 - 工具栏
    add_btn = ('xpath', '//div[@class="table-operator"]/button[1]')
    delete_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"删除")]/..')
    enable_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"启用")]/..')
    disable_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"禁用")]/..')

    # 新增/编辑弹窗表单
    person_name = ('id', 'name')
    person_type = ('css selector', '#type .ant-select-selection')
    person_sort = ('id', 'sort')
    person_save = ('xpath', '//div[contains(@class,"ant-modal-footer")]//button[contains(@class,"ant-btn-primary")]')
    delete_confirm = ('xpath', '//div[contains(@class,"ant-popover-buttons")]//button[contains(@class,"ant-btn-primary")]')

    def _select_type(self, person_type):
        """在弹窗下拉框中选择经手人类型。"""
        self.click(*self.person_type, key='person_type')
        self.wait(1)
        self.click(
            'xpath',
            f'//div[contains(@class,"ant-select-dropdown")]//li[contains(text(),"{person_type}")]',
            key='person_type_option',
        )

    def open_list(self):
        """打开经手人管理列表页并等待页面加载。"""
        self.open_path(self.PATH)
        self.wait(2)

    def add_person(self, name, person_type, sort=''):
        """新增经手人：打开列表 → 点击新增 → 填写表单 → 保存。"""
        self.open_list()
        self.click(*self.add_btn, key='add_btn')
        self.wait(2)
        self.input(*self.person_name, txt=name, key='person_name')
        self._select_type(person_type)
        if sort:
            self.input(*self.person_sort, txt=str(sort), key='person_sort')
        self.click(*self.person_save, key='person_save')

    def search(self, name=''):
        """按姓名查询经手人列表。"""
        self.open_list()
        if name:
            self.input(*self.search_name, txt=name, key='search_name')
        self.click(*self.search_btn, key='search_btn')

    def delete_person(self, name):
        """根据姓名定位行并删除，确认 popconfirm 弹窗。"""
        self.search(name=name)
        self.click(
            'xpath',
            f'//td[contains(text(),"{name}")]/../td//a[contains(text(),"删除")]',
            key='row_delete',
        )
        self.wait(1)
        self.click(*self.delete_confirm, key='delete_confirm')

    def assert_person_not_exists(self, name):
        """查询后断言列表中不存在指定姓名的经手人。"""
        self.search(name=name)
        self.driver.implicitly_wait(0)
        try:
            rows = self.driver.find_elements(
                'xpath', f'//td[contains(text(), "{name}")]',
            )
            assert not rows, f'预期经手人 {name} 已删除，但仍存在于列表中'
        finally:
            self.driver.implicitly_wait(self.IMPLICIT_WAIT)
