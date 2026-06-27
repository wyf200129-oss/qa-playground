from base_page.basepage import BasePage


class DepotPage(BasePage):
    """仓库信息页面对象，封装列表查询、新增/编辑弹窗及行内操作。"""

    PATH = '/system/depot'

    # 列表页 - 查询区
    search_name = ('xpath', '//input[@placeholder="请输入仓库名称查询"]')
    search_remark = ('xpath', '//input[@placeholder="请输入备注查询"]')
    search_btn = ('xpath', '//span[contains(text(),"查询")]/..')
    reset_btn = ('xpath', '//span[contains(text(),"重置")]/..')

    # 列表页 - 工具栏
    add_btn = ('xpath', '//div[@class="table-operator"]/button[1]')
    delete_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"删除")]/..')
    enable_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"启用")]/..')
    disable_btn = ('xpath', '//div[@class="table-operator"]//span[contains(text(),"禁用")]/..')

    # 新增/编辑弹窗表单（优先使用 id 定位）
    depot_name = ('id', 'name')
    depot_address = ('id', 'address')
    depot_warehousing = ('id', 'warehousing')
    depot_truckage = ('id', 'truckage')
    depot_principal = ('css selector', '#principal .ant-select-selection')
    depot_sort = ('id', 'sort')
    depot_remark = ('id', 'remark')
    depot_save = ('xpath', '//div[contains(@class,"ant-modal-footer")]//button[contains(@class,"ant-btn-primary")]')

    def _select_principal(self, principal_name):
        """在下拉框中选择负责人。"""
        self.click(*self.depot_principal)
        self.wait(1)
        self.click(
            'xpath',
            f'//div[contains(@class,"ant-select-dropdown")]//li[contains(text(),"{principal_name}")]',
        )

    def open_list(self):
        """打开仓库信息列表页并等待页面加载。"""
        self.open_path(self.PATH)
        self.wait(2)

    def add_depot(self, name, address='', warehousing='', truckage='', principal='', sort='', remark=''):
        """新增仓库：打开列表 → 点击新增 → 填写表单 → 保存。"""
        self.open_list()
        self.click(*self.add_btn)
        self.wait(2)
        self.input(*self.depot_name, txt=name)
        if address:
            self.input(*self.depot_address, txt=address)
        if warehousing:
            self.input(*self.depot_warehousing, txt=str(warehousing))
        if truckage:
            self.input(*self.depot_truckage, txt=str(truckage))
        if principal:
            self._select_principal(principal)
        if sort:
            self.input(*self.depot_sort, txt=str(sort))
        if remark:
            self.input(*self.depot_remark, txt=remark)
        self.click(*self.depot_save)

    def search(self, name='', remark=''):
        """按仓库名称和/或备注查询列表。"""
        self.open_list()
        if name:
            self.input(*self.search_name, txt=name)
        if remark:
            self.input(*self.search_remark, txt=remark)
        self.click(*self.search_btn)

    def edit_depot(self, name, **fields):
        """根据仓库名称定位行并编辑，fields 支持 name/address/warehousing 等字段。"""
        self.search(name=name)
        self.click(
            'xpath',
            f'//td[contains(text(),"{name}")]/../td//a[contains(text(),"编辑")]',
        )
        self.wait(1)
        if 'name' in fields:
            self.locator(*self.depot_name).clear()
            self.input(*self.depot_name, txt=fields['name'])
        if 'address' in fields:
            self.locator(*self.depot_address).clear()
            self.input(*self.depot_address, txt=fields['address'])
        if 'warehousing' in fields:
            self.locator(*self.depot_warehousing).clear()
            self.input(*self.depot_warehousing, txt=str(fields['warehousing']))
        if 'truckage' in fields:
            self.locator(*self.depot_truckage).clear()
            self.input(*self.depot_truckage, txt=str(fields['truckage']))
        if 'principal' in fields:
            self._select_principal(fields['principal'])
        if 'sort' in fields:
            self.locator(*self.depot_sort).clear()
            self.input(*self.depot_sort, txt=str(fields['sort']))
        if 'remark' in fields:
            self.locator(*self.depot_remark).clear()
            self.input(*self.depot_remark, txt=fields['remark'])
        self.click(*self.depot_save)

    def delete_depot(self, name):
        """根据仓库名称定位行并删除，确认弹窗。"""
        self.search(name=name)
        self.click(
            'xpath',
            f'//td[contains(text(),"{name}")]/../td//a[contains(text(),"删除")]',
        )
        self.wait(1)
        self.click('xpath', '//div[@class="ant-modal-confirm-btns"]/button[2]')

    def set_default(self, name):
        """将指定仓库设为默认仓库。"""
        self.search(name=name)
        self.click(
            'xpath',
            f'//td[contains(text(),"{name}")]/../td//a[contains(text(),"设为默认")]',
        )
