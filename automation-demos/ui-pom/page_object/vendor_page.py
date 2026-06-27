from base_page.basepage import BasePage


class VendorPage(BasePage):
    PATH = '/system/vendor'

    vendor_add = ('xpath', '//div[@class="table-operator"]/button[1]')
    supplier_name = ('id', 'supplier')
    supplier_telephone = ('id', 'telephone')
    supplier_save = ('xpath', '//div[@class="ant-modal-footer"]/div[1]/button[2]')
    search_name = ('xpath', '//input[@placeholder="请输入名称查询"]')
    search_button = ('xpath', '//span[text()="查 询"]/..')

    def add_supplier(self, name, tele):
        self.open_path(self.PATH)
        self.click(*self.vendor_add)
        self.input(*self.supplier_name, txt=name)
        self.input(*self.supplier_telephone, txt=tele)
        self.click(*self.supplier_save)

    def search(self, name):
        self.open_path(self.PATH)
        self.input(*self.search_name, txt=name)
        self.click(*self.search_button)
