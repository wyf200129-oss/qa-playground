from base_page.basepage import BasePage


class SaleOrderPage(BasePage):
    PATH = '/bill/sale_order'

    # 列表页（图1）
    add_btn = ('xpath', '//div[@class="table-operator"]/button[1]')
    search_order_no = ('xpath', '//input[@placeholder="请输入单据编号"]')
    search_goods_info = ('xpath', '//input[contains(@placeholder,"请输入条码")]')
    search_btn = ('xpath', '//span[contains(text(),"查询")]/..')
    reset_btn = ('xpath', '//span[contains(text(),"重置")]/..')

    # 新增表单 - 头部（图2）
    customer = ('xpath', '//label[contains(.,"客户")]/following-sibling::div//input')
    order_date = ('xpath', '//label[contains(.,"单据日期")]/following-sibling::div//input')
    order_no = ('id', 'billNo')
    salesman = ('xpath', '//label[contains(.,"销售人员")]/following-sibling::div//input')

    # 明细操作
    insert_row = ('xpath', '//span[contains(text(),"插入行")]/..')
    scan_entry = ('xpath', '//span[contains(text(),"扫码录入")]/..')
    history_bill = ('xpath', '//span[contains(text(),"历史单据")]/..')
    import_detail = ('xpath', '//span[contains(text(),"导入明细")]/..')

    # 商品明细第一行
    goods_barcode = ('xpath', '//input[@placeholder="输入条码或名称"]')
    goods_search = ('xpath', '(//input[@placeholder="输入条码或名称"]/ancestor::span[contains(@class,"ant-input-search")]//span[contains(@class,"ant-input-search-icon")])[1]')
    goods_quantity = ('xpath', '//tbody/tr[1]/td[8]//input')
    goods_price = ('xpath', '//tbody/tr[1]/td[9]//input')

    # 底部字段
    remark = ('xpath', '//textarea[@placeholder="请输入备注"]')
    discount_rate = ('xpath', '//label[contains(.,"优惠率")]/following-sibling::div//input')
    discount_amount = ('xpath', '//label[contains(.,"收款优惠")]/following-sibling::div//input')
    final_amount = ('xpath', '//label[contains(.,"优惠后金额")]/following-sibling::div//input')
    account = ('xpath', '//label[contains(.,"结算账户")]/following-sibling::div//input')
    deposit = ('xpath', '//label[contains(.,"收取订金")]/following-sibling::div//input')
    attachment = ('xpath', '//span[text()="点击上传"]/..')

    # 底部操作（图2）
    cancel_btn = ('xpath', '//span[contains(text(),"取消")]/..')
    save_btn = ('xpath', '//span[contains(text(),"保存") and not(contains(text(),"审核"))]/..')
    save_audit_btn = ('xpath', '//span[contains(text(),"保存并审核")]/..')

    def _select_dropdown(self, input_locator, option_text):
        self.click(*input_locator)
        self.wait(1)
        self.click(
            'xpath',
            f'//div[contains(@class,"ant-select-dropdown")]//span[contains(text(),"{option_text}")]',
        )

    def open_add_form(self):
        self.open_path(self.PATH)
        self.wait(2)
        self.click(*self.add_btn)
        self.wait(2)

    def add_order(self, customer, goods_name, quantity, price, remark=''):
        self.open_add_form()
        self._select_dropdown(self.customer, customer)
        self.input(*self.goods_barcode, txt=goods_name)
        self.click(*self.goods_search)
        self.wait(2)
        self.input(*self.goods_quantity, txt=str(quantity))
        self.input(*self.goods_price, txt=str(price))
        if remark:
            self.input(*self.remark, txt=remark)

    def save_order(self):
        self.click(*self.save_btn)

    def save_and_audit_order(self):
        self.click(*self.save_audit_btn)

    def get_order_no(self):
        return self.locator(*self.order_no).get_attribute('value')

    def search(self, order_no):
        self.open_path(self.PATH)
        self.wait(2)
        self.input(*self.search_order_no, txt=order_no)
        self.click(*self.search_btn)
